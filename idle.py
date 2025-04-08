import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import sys
import io
from lexical_analyzer import cilly_lexer, error as cilly_error
from syntactic_analyzer import cilly_parser
from eval import cilly_eval


class CillyIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Cilly IDE")
        self.root.geometry("800x600")

        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TButton", font=("微软雅黑", 10))
        self.style.configure("TLabel", font=("微软雅黑", 10))

        # 创建主框架
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建顶部工具栏
        self.toolbar = ttk.Frame(self.main_frame)
        self.toolbar.pack(fill=tk.X, pady=(0, 5))

        # 运行按钮
        self.run_button = ttk.Button(self.toolbar, text="运行代码", command=self.run_code)
        self.run_button.pack(side=tk.LEFT, padx=5)

        # 清空按钮
        self.clear_button = ttk.Button(self.toolbar, text="清空编辑器", command=self.clear_editor)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # 清空输出按钮
        self.clear_output_button = ttk.Button(self.toolbar, text="清空输出", command=self.clear_output)
        self.clear_output_button.pack(side=tk.LEFT, padx=5)

        # 示例代码按钮
        self.example_button = ttk.Button(self.toolbar, text="插入示例代码", command=self.insert_example)
        self.example_button.pack(side=tk.LEFT, padx=5)

        # 创建分割窗口
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.VERTICAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # 创建代码编辑区
        self.editor_frame = ttk.LabelFrame(self.paned_window, text="Cilly 代码编辑器")
        self.paned_window.add(self.editor_frame, weight=3)

        self.code_editor = scrolledtext.ScrolledText(self.editor_frame, wrap=tk.WORD,
                                                     font=("Consolas", 12), bg="#f5f5f5")
        self.code_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建输出区
        self.output_frame = ttk.LabelFrame(self.paned_window, text="输出")
        self.paned_window.add(self.output_frame, weight=1)

        self.output_text = scrolledtext.ScrolledText(self.output_frame, wrap=tk.WORD,
                                                     font=("Consolas", 12), bg="#ffffff")
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.output_text.config(state=tk.DISABLED)

        # 状态栏
        self.status_bar = ttk.Label(self.main_frame, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))

        # 示例代码
        self.example_code = '''
# Cilly示例程序

# 变量定义和计算
var a = 10;
var b = 20;
var sum = a + b;
print("a + b =", sum);

# 条件语句
var x = -15;
var abs_x = x > 0 ? x : -x;
print("x的绝对值:", abs_x);

# 循环计算1到100的和
var sum = 0;
var i = 1;
while(i <= 100){
    sum = sum + i;
    i = i + 1;
}
print("1+2+...+100 =", sum);

# 幂运算
var pow = 2 ^ 3;
print("2的3次方 =", pow);

# for循环
for (var j = 0; j < 5; j = j + 1;) {
    print("for循环计数:", j);
}

# 函数定义和调用
var add = fun(a, b){
    return a + b;
};
print("函数调用:", add(5, 7));
'''

    def run_code(self):
        """运行用户编写的代码"""
        # 获取代码内容
        code = self.code_editor.get("1.0", tk.END)

        # 重定向标准输出
        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output

        # 清空输出区域
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)

        try:
            # 更新状态栏
            self.status_bar.config(text="运行中...")
            self.root.update()

            # 执行词法分析
            tokens = cilly_lexer(code)

            # 在输出中添加标记信息
            output = "--- 词法分析结果 ---\n"
            for token in tokens[:10]:  # 只显示前10个标记
                output += str(token) + "\n"
            if len(tokens) > 10:
                output += f"...共{len(tokens)}个标记\n"

            # 语法分析
            output += "\n--- 语法分析结果 ---\n"
            ast = cilly_parser(tokens)
            output += "语法树构建成功!\n"

            # 解释执行
            output += "\n--- 执行结果 ---\n"
            cilly_eval(ast)

            # 获取重定向的输出
            output += "\n" + redirected_output.getvalue()

            # 更新状态栏
            self.status_bar.config(text="运行完成")

        except Exception as e:
            output = f"错误: {str(e)}"
            self.status_bar.config(text="运行出错")

        finally:
            # 恢复标准输出
            sys.stdout = old_stdout

            # 在输出区域显示结果
            self.output_text.insert(tk.END, output)
            self.output_text.config(state=tk.DISABLED)

    def clear_editor(self):
        """清空代码编辑器"""
        self.code_editor.delete("1.0", tk.END)
        self.status_bar.config(text="编辑器已清空")

    def clear_output(self):
        """清空输出区域"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.status_bar.config(text="输出已清空")

    def insert_example(self):
        """插入示例代码"""
        # 清空当前内容
        self.code_editor.delete("1.0", tk.END)
        # 插入示例代码
        self.code_editor.insert(tk.END, self.example_code.strip())
        self.status_bar.config(text="示例代码已插入")


if __name__ == "__main__":
    root = tk.Tk()
    app = CillyIDE(root)
    root.mainloop()
