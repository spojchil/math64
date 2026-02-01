import datetime
import os
from PIL import Image
import PIL.ImageOps
import glob
import fitz  # PyMuPDF
import multiprocessing
import sys


def get_file_size(file_path):
    """获取文件大小（以MB为单位）"""
    return os.path.getsize(file_path) / (1024 * 1024)


def calculate_size_ratio(original_path, new_path):
    """计算新文件大小占原始文件大小的百分比"""
    original_size = get_file_size(original_path)
    new_size = get_file_size(new_path)
    ratio = (new_size / original_size) * 100

    print(f"\n文件大小对比:")
    print(f"原始文件: {original_size:.2f} MB")
    print(f"新文件: {new_size:.2f} MB")
    print(f"新文件是原始文件的: {ratio:.2f}%")

    return ratio


def convert_page(args):
    """转换单个页面"""
    pdf_path, page_num, image_path, zoom, jpeg_quality, invert = args
    pdf_doc = fitz.open(pdf_path)
    page = pdf_doc[page_num]
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    if invert:
        img = PIL.ImageOps.invert(img)

    img.save(f"{image_path}/page_{page_num:03d}.jpg", "JPEG", quality=jpeg_quality)
    pdf_doc.close()
    return page_num


def process_pages_parallel(pdf_path, image_path, zoom=1.5, jpeg_quality=85, invert=True,
                           start_page=None, end_page=None, num_processes=8):
    """并行处理PDF页面转换"""
    start_time = datetime.datetime.now()
    pdf_doc = fitz.open(pdf_path)
    total_pages = pdf_doc.page_count
    pdf_doc.close()

    # 设置页码范围
    if start_page is None:
        start_page = 0
    if end_page is None or end_page >= total_pages:
        end_page = total_pages - 1

    os.makedirs(image_path, exist_ok=True)

    # 创建任务列表
    tasks = []
    for pg in range(start_page, end_page + 1):
        tasks.append((pdf_path, pg, image_path, zoom, jpeg_quality, invert))

    # 创建进程池
    pool = multiprocessing.Pool(processes=num_processes)

    # 进度跟踪
    completed = 0
    total = end_page - start_page + 1

    def update_progress(result):
        nonlocal completed
        completed += 1
        elapsed = (datetime.datetime.now() - start_time).seconds
        speed = completed / max(1, elapsed)
        sys.stdout.write(f"\r转换进度: {completed}/{total}页 | "
                         f"耗时: {elapsed}s | "
                         f"速度: {speed:.2f}页/s")
        sys.stdout.flush()

    # 并行处理
    for _ in pool.imap_unordered(convert_page, tasks):
        update_progress(_)

    pool.close()
    pool.join()

    print(f"\n转换完成！总耗时: {(datetime.datetime.now() - start_time).seconds}秒")
    return total_pages


def get_toc(pdf_path):
    """获取PDF书签"""
    pdf_doc = fitz.open(pdf_path)
    toc = pdf_doc.get_toc()
    print(toc)
    pdf_doc.close()

    # 清理无效字符
    def clean_title(title):
        if not title:
            return title
        try:
            # 尝试正常编码
            title.encode('utf-16-be')
            return title
        except UnicodeEncodeError:
            # 如果失败，清理无效字符
            return ''.join(char for char in title
                           if ord(char) < 0xD800 or ord(char) > 0xDFFF)

    cleaned_toc = []
    for item in toc:
        if len(item) >= 2:
            level, title = item[0], item[1]
            cleaned_title = clean_title(title)
            new_item = [level, cleaned_title] + item[2:]
            cleaned_toc.append(new_item)
        else:
            cleaned_toc.append(item)

    return cleaned_toc


def pic2pdf(imagePath, newPath, toc=None, compress=True,
            start_page=None, end_page=None):
    """合并图片为PDF并添加书签"""
    doc = fitz.open()
    img_files = sorted(glob.glob(f"{imagePath}/*.jpg"))

    # 如果指定了页码范围，只处理范围内的图片
    if start_page is not None and end_page is not None:
        filtered_files = []
        for f in img_files:
            try:
                page_num = int(os.path.basename(f).split('_')[1].split('.')[0])
                if start_page <= page_num <= end_page:
                    filtered_files.append(f)
            except (IndexError, ValueError):
                continue
        img_files = filtered_files

    # 插入所有图片页面
    for i, img_path in enumerate(img_files):
        img_doc = fitz.open(img_path)
        pdf_bytes = img_doc.convert_to_pdf()
        img_doc.close()

        img_pdf = fitz.open("pdf", pdf_bytes)
        doc.insert_pdf(img_pdf)
        print(f"\r合并进度: {i + 1}/{len(img_files)}页", end="", flush=True)

    # 添加书签
    if (not (start_page or end_page)) and toc:
        doc.set_toc(toc)
    doc.save(newPath, deflate=compress)
    print()
    doc.close()
    print(f"\nPDF生成完成: {newPath}")


def clean_image_folder(imagePath):
    """清理临时图片"""
    for f in glob.glob(f"{imagePath}/*"):
        os.remove(f)
    os.rmdir(imagePath)
    print(f"已清理临时文件: {imagePath}")


def delete_pdf_page_pymupdf(input_path, output_path, page_to_delete):
    """
    使用PyMuPDF删除PDF中的指定页
    :param input_path: 输入PDF路径
    :param output_path: 输出PDF路径
    :param page_to_delete: 要删除的页码（从0开始）
    """
    doc = fitz.open(input_path)
    doc.delete_page(page_to_delete)
    doc.save(output_path)
    doc.close()


def preview_page(pdfPath, page_num, zoom=1.5, invert=True):
    """
    预览指定页面
    :param page_num: 要预览的页码(从0开始)
    :return: PIL图像对象
    """
    pdfDoc = fitz.open(pdfPath)
    page = pdfDoc[page_num]
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    if invert:
        img = PIL.ImageOps.invert(img)

    pdfDoc.close()
    return img


if __name__ == "__main__":
    # 参数配置
    pdfPath = "Java核心技术·卷I（原书第12版） ([美] 凯·S.霍斯特曼（Cay S.Horstmann）) .pdf"  # 输入PDF路径
    imagePath = "临时文件夹"  # 临时图片文件夹
    outputPdf = "暗色版_" + pdfPath  # 输出PDF路径
    num_processes = 8  # 进程数量

    start_page = None
    end_page = None

    # Step 1: 获取书签
    toc = get_toc(pdfPath)


    # Step 2: 并行处理PDF → 图片
    total_pages = process_pages_parallel(
        pdfPath, imagePath, zoom=2, jpeg_quality=85, invert=True,
        start_page=start_page, end_page=end_page, num_processes=num_processes
    ) # 扫描版的话该参数大小大约是源文件的2-3倍，质量还不错

    # Step 3: 图片 → PDF 并传入书签
    pic2pdf(imagePath, outputPdf, toc=toc, compress=True,
            start_page=start_page, end_page=end_page)

    # Step 4: 清理临时文件
    clean_image_folder(imagePath)

    if not (start_page or end_page):
        calculate_size_ratio(pdfPath, outputPdf)  # 一般来说质量很高时膨胀数十倍也很正常

    # 预览页面示例
    # preview_img = preview_page(pdfPath, 5)  # 预览第6页
    # preview_img.show()'''