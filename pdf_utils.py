import re
import os
from PyPDF2 import PdfReader, PdfWriter
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer

class PDFSplitter:
    @staticmethod
    def split_by_pages(input_path, output_dir, page_ranges):
        """固定页码分割"""
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        
        for i, (start, end) in enumerate(page_ranges, 1):
            writer = PdfWriter()
            for page_num in range(start-1, min(end, total_pages)):
                writer.add_page(reader.pages[page_num])
            output_path = os.path.join(output_dir, f"split_part_{i}.pdf")
            with open(output_path, "wb") as f:
                writer.write(f)

    @staticmethod
    def split_by_custom(input_path, output_dir, split_points):
        """自定义分割点"""
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        split_points = sorted(split_points)
        
        prev = 0
        for i, point in enumerate(split_points + [total_pages], 1):
            writer = PdfWriter()
            for page_num in range(prev, min(point, total_pages)):
                writer.add_page(reader.pages[page_num])
            output_path = os.path.join(output_dir, f"custom_part_{i}.pdf")
            with open(output_path, "wb") as f:
                writer.write(f)
            prev = point

    @staticmethod
    def split_by_titles(input_path, output_dir, patterns):
        """按标题分割"""
        # 获取标题位置
        title_pages = []
        for page_num, page_layout in enumerate(extract_pages(input_path)):
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    text = element.get_text().strip()
                    for pattern in patterns:
                        if re.match(pattern, text):
                            title_pages.append(page_num + 1)  # 转为1-based
                            break
        
        # 执行分割
        reader = PdfReader(input_path)
        split_points = title_pages[1:]  # 从第二个标题开始分割
        return PDFSplitter.split_by_custom(input_path, output_dir, split_points)