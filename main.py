import tkinter as tk
from tkinter import filedialog, messagebox
from pdf_utils import PDFSplitter
import os

class PDFSplitterGUI:
    def __init__(self, master):
        self.master = master
        master.title("PDF智能分割器")
        
        # 文件选择
        self.file_path = tk.StringVar()
        tk.Label(master, text="选择PDF文件").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(master, textvariable=self.file_path, width=50).grid(row=0, column=1)
        tk.Button(master, text="浏览", command=self.browse_file).grid(row=0, column=2)
        
        # 分割方式选择
        self.mode = tk.IntVar(value=1)
        modes = [
            ("固定页码分割", 1),
            ("自定义分割点", 2),
            ("按标题分割", 3)
        ]
        for i, (text, val) in enumerate(modes, start=1):
            tk.Radiobutton(master, text=text, variable=self.mode, value=val
                          ).grid(row=i, column=0, sticky='w')
        
        # 输入框
        self.input_text = tk.Text(master, height=3, width=50)
        self.input_text.grid(row=5, column=1, pady=5)
        
        # 示例提示
        self.example_label = tk.Label(master, text="")
        self.example_label.grid(row=6, column=1, sticky='w')
        
        # 按钮
        tk.Button(master, text="开始分割", command=self.start_split).grid(row=7, column=1, pady=10)
        
        # 绑定事件
        self.mode.trace_add('write', self.update_ui)
        self.update_ui()

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("PDF文件", ".pdf")])
        if filename:
            self.file_path.set(filename)

    def update_ui(self):
        mode = self.mode.get()
        self.input_text.delete(1.0, tk.END)
        
        examples = {
            1 :"示例:n\每3页分割 → 输入'3'\n指定范围 → 输入'1-5,6-10'",
            2 :"示例:n\在第5、10页分割 → 输入'5,10'",
            3 :"示例:n\使用默认标题格式 → 留空n\自定义格式 → 输入正则如'^第[一二三四五六七八九十]+章$'"
        }
        self.example_label.config(text=examples.get(mode, ))

    def start_split(self):
        input_file = self.file_path.get()
        if not os.path.exists(input_file):
            messagebox.showerror("错误", "请先选择有效的PDF文件")
            return
        
        output_dir = filedialog.askdirectory()
        if not output_dir:
            return
        
        try:
            if self.mode.get() == 1:  # 固定页码
                rule = self.input_text.get(1.0, tk.END).strip()
                if '-' in rule:
                    ranges = [tuple(map(int, r.split('-'))) 
                             for r in rule.split(',')]
                else:
                    step = int(rule)
                    from PyPDF2 import PdfReader
                    reader = PdfReader(input_file)
                    total = len(reader.pages)
                    ranges = [(i+1, min(i+step, total)) 
                             for i in range(0, total, step)]
                PDFSplitter.split_by_pages(input_file, output_dir, ranges)
            
            elif self.mode.get() == 2:  # 自定义分割
                points = list(map(int, self.input_text.get(1.0, tk.END).split(',')))
                PDFSplitter.split_by_custom(input_file, output_dir, points)
            
            elif self.mode.get() == 3:  # 按标题
                patterns = [p.strip() for p in self.input_text.get(1.0, tk.END).split('\n') if p.strip()]
                if not patterns:  # 空列表时使用默认正则
                    patterns = [
                        r'^第[一二三四五六七八九十]+章',
                        r'^第一部分',
                        r'^第\d+章'
                    ]
                PDFSplitter.split_by_titles(input_file, output_dir, patterns)
            
            messagebox.showinfo("完成", "文件分割成功！")
        
        except Exception as e:
            messagebox.showerror("错误", f"处理失败: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFSplitterGUI(root)
    root.mainloop()