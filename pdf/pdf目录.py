from PyPDF2 import PdfReader


def extract_pdf_outline(pdf_path, output_path="pdf大纲.txt"):
    """
    使用PyPDF2提取PDF大纲（仅提取到三级目录），处理无页面的书签和路径转义问题
    :param pdf_path: PDF文件路径（支持Windows带反斜杠的路径）
    :param output_path: 输出文本文件路径
    """
    try:
        # 初始化PDF阅读器
        reader = PdfReader(pdf_path)
        outline = reader.outline  # 获取大纲（书签）

        # 若PDF无大纲，直接提示并返回
        if not outline:
            print(f"提示：PDF文件「{pdf_path}」未检测到目录/书签！")
            return

        # 写入目录到文本文件
        with open(output_path, "w", encoding="utf-8") as f:
            def parse_outline(items, level=0):
                """递归解析大纲层级，仅处理到三级（level 0/1/2）"""
                # 核心判断：只处理level ≤ 2（对应一级、二级、三级），超过则直接返回
                if level > 1:
                    return

                for item in items:
                    if isinstance(item, list):
                        # 递归处理子层级（仅当当前level < 2时才继续）
                        parse_outline(item, level + 1)
                    else:
                        # 层级缩进，增强可读性
                        indent = "  " * level
                        try:
                            # 尝试获取页码（PyPDF2返回0-based索引，需+1）
                            if item.page is not None:  # 先判断页面是否存在
                                page_num = reader.get_page_number(item.page) + 1
                                page_info = f" - 第{page_num}页"
                            else:
                                page_info = " - 无关联页面"
                        except AttributeError:
                            # 捕获NullObject异常，标记无页码
                            page_info = " - 无关联页面"

                        # 写入三级及以内的目录项
                        f.write(f"{indent}{item.title}{page_info}\n")

            # 开始解析大纲
            parse_outline(outline)

        print(f"✅ 仅三级目录导出成功！文件保存至：{output_path}")

    except FileNotFoundError:
        print(f"❌ 错误：未找到PDF文件「{pdf_path}」，请检查路径是否正确！")
    except Exception as e:
        print(f"❌ 运行出错：{str(e)}")


# ==================== 使用示例 ====================
# 路径前加r（原始字符串）避免转义问题，替换为你的PDF路径
pdf_file_path = r"D:\Edge下载\建筑施工手册（第六版）全册.pdf"
extract_pdf_outline(pdf_file_path)