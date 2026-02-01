import datetime
import os
from PIL import Image
import PIL.ImageOps
import glob
import fitz  # PyMuPDF


def get_file_size(file_path):
    """获取文件大小（以MB为单位）"""
    return os.path.getsize(file_path) / (1024*1024)


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

def pyMuPDF_fitz(pdfPath, imagePath, zoom=1.5, jpeg_quality=85, invert=True,
                 start_page=None, end_page=None):
    """
    将PDF转换为图片并返回书签信息
    :param start_page: 起始页码(从0开始)
    :param end_page: 结束页码(包含)
    :return: 书签列表和总页数
    """
    startTime = datetime.datetime.now()
    pdfDoc = fitz.open(pdfPath)
    total_pages = pdfDoc.page_count

    # 设置页码范围
    if start_page is None:
        start_page = 0
    if end_page is None or end_page >= total_pages:
        end_page = total_pages - 1

    # 获取原始书签
    toc = pdfDoc.get_toc()
    os.makedirs(imagePath, exist_ok=True)

    # 只处理指定范围内的页面
    for pg in range(start_page, end_page + 1):
        page = pdfDoc[pg]
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        if invert:
            img = PIL.ImageOps.invert(img)

        img.save(f"{imagePath}/page_{pg:03d}.jpg", "JPEG", quality=jpeg_quality)
        print(f"\r转换进度: {pg - start_page + 1}/{end_page - start_page + 1}页 | "
              f"耗时: {(datetime.datetime.now() - startTime).seconds}s | "
              f"速度: {((pg - start_page + 1)/max(1,(datetime.datetime.now() - startTime).seconds)):.2f}页/s", end="", flush=True)

    pdfDoc.close()
    print(f"\n转换完成！总耗时: {(datetime.datetime.now() - startTime).seconds}秒")
    return toc, total_pages  # 返回书签和总页数


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
    pdfPath = "Head First Java 中文高清版.pdf"  # 输入PDF路径
    imagePath = "临时文件夹"  # 临时图片文件夹
    outputPdf = "暗色版_" + pdfPath  # 输出PDF路径

    # 示例：只生成第6-8页（页码从0开始）
    start_page = None  # 第6页
    end_page = None  # 第8页

    # Step 1: PDF → 图片（修复进度+反色）并获取书签
    toc, total_pages = pyMuPDF_fitz(pdfPath, imagePath, zoom=3,
                                    jpeg_quality=100, invert=True,
                                    start_page=start_page, end_page=end_page)

    # Step 2: 图片 → PDF 并传入书签
    pic2pdf(imagePath, outputPdf, toc=toc, compress=True,
            start_page=start_page, end_page=end_page)

    # Step 3: 清理临时文件（可选）
    clean_image_folder(imagePath)

    if not (start_page or end_page):
        calculate_size_ratio(pdfPath, outputPdf)  #一般来说质量很高时膨胀数十倍也很正常

    # 预览页面示例
    # preview_img = preview_page(pdfPath, 5)  # 预览第6页
    # preview_img.show()