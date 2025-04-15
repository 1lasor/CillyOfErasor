import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import sys
import io
from lexical_analyzer import cilly_lexer, error as cilly_error
from syntactic_analyzer import cilly_parser
from eval import cilly_eval, reset_environment, val


class CillyIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Cilly IDE")
        self.root.geometry("800x600")

        # 添加模式标志
        self.interactive_mode = False
        self.run_count = 0  # 添加运行次数计数器

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

        # 添加交互模式按钮
        self.interactive_button = ttk.Button(self.toolbar, text="打开交互模式", command=self.open_interactive)
        self.interactive_button.pack(side=tk.LEFT, padx=5)

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
var sum1 = a + b;
print("a + b =", sum1);

# 条件语句
var x = -15;
var abs_x = x > 0 ? x : -x;
print("x的绝对值:", abs_x);

# 循环计算1到100的和
var sum2 = 0;
var i = 1;
while(i <= 100){
    sum2 = sum2 + i;
    i = i + 1;
}
print("1+2+...+100 =", sum2);

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

# 外部函数引用
greet("me");
'''

    def open_interactive(self):
        """打开交互模式窗口"""
        # 创建新窗口
        self.interactive_window = tk.Toplevel(self.root)
        self.interactive_window.title("Cilly 交互模式")
        self.interactive_window.geometry("600x500")
        
        # 为交互模式创建一个持久化的环境
        self.interactive_env = None  # 将在首次执行时初始化
        
        # 创建主框架
        main_frame = ttk.Frame(self.interactive_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建菜单栏
        menubar = tk.Menu(self.interactive_window)
        self.interactive_window.config(menu=menubar)
        
        # 添加"编辑"菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="清空控制台", command=self.clear_interactive_console)
        
        # 创建交互式控制台
        self.interactive_console = scrolledtext.ScrolledText(
            main_frame, 
            wrap=tk.WORD,
            font=("Consolas", 12),
            bg="#ffffff",
            insertbackground="black",  # 光标颜色
            selectbackground="#d0d0d0",  # 选择文本背景色
            padx=5,
            pady=5
        )
        self.interactive_console.pack(fill=tk.BOTH, expand=True)
        
        # 设置文本标签
        self.interactive_console.tag_configure("prompt", foreground="blue")
        self.interactive_console.tag_configure("input", foreground="black")
        self.interactive_console.tag_configure("output", foreground="darkgreen")
        self.interactive_console.tag_configure("error", foreground="red")
        
        # 输入历史
        self.command_history = []
        self.history_index = 0
        
        # 当前提示符位置
        self.prompt_position = "1.0"
        
        # 显示欢迎信息
        welcome_text = "欢迎使用 Cilly 交互模式！\n"
        self.interactive_console.insert(tk.END, welcome_text, "output")
        
        # 插入初始提示符
        self.insert_prompt()
        
        # 绑定键盘事件
        self.interactive_console.bind("<Return>", self.handle_return)
        self.interactive_console.bind("<Up>", self.handle_up)
        self.interactive_console.bind("<Down>", self.handle_down)
        self.interactive_console.bind("<BackSpace>", self.handle_backspace)
        self.interactive_console.bind("<Tab>", self.handle_tab)
        self.interactive_console.bind("<KeyPress>", self.check_input_position)
        
        # 设置焦点
        self.interactive_console.focus_set()
        
        # 设置窗口关闭事件
        self.interactive_window.protocol("WM_DELETE_WINDOW", self.close_interactive_window)
    
    def insert_prompt(self):
        """插入提示符"""
        self.interactive_console.insert(tk.END, ">>> ", "prompt")
        self.prompt_position = self.interactive_console.index(tk.INSERT)
    
    def check_input_position(self, event):
        """检查光标位置，防止删除提示符"""
        cursor_position = self.interactive_console.index(tk.INSERT)
        prompt_line, prompt_char = map(int, self.prompt_position.split('.'))
        cursor_line, cursor_char = map(int, cursor_position.split('.'))
        
        # 如果光标在提示符之前，则移动到提示符之后
        if cursor_line < prompt_line or (cursor_line == prompt_line and cursor_char < prompt_char):
            self.interactive_console.mark_set(tk.INSERT, self.prompt_position)
            return "break"
        return None
    
    def handle_backspace(self, event):
        """处理退格键，防止删除提示符"""
        cursor_position = self.interactive_console.index(tk.INSERT)
        prompt_position = self.prompt_position
        
        if cursor_position == prompt_position:
            return "break"  # 阻止删除提示符
        return None
    
    def handle_tab(self, event):
        """处理Tab键，插入4个空格"""
        self.interactive_console.insert(tk.INSERT, "    ")
        return "break"
    
    def handle_return(self, event):
        """处理回车键，执行命令"""
        # 获取当前行到末尾的文本
        line_content = self.interactive_console.get(self.prompt_position, tk.END).strip()
        
        if not line_content:
            # 如果是空行，就插入新的提示符
            self.interactive_console.insert(tk.END, "\n")
            self.insert_prompt()
            return "break"
        
        # 记录命令历史
        self.command_history.append(line_content)
        self.history_index = len(self.command_history)
        
        # 执行命令
        self.interactive_console.insert(tk.END, "\n")
        self.execute_command(line_content)
        
        return "break"  # 防止默认行为
    
    def handle_up(self, event):
        """处理向上键，浏览历史命令"""
        if not self.command_history:
            return "break"
        
        if self.history_index > 0:
            self.history_index -= 1
            self.replace_current_line(self.command_history[self.history_index])
        
        return "break"
    
    def handle_down(self, event):
        """处理向下键，浏览历史命令"""
        if not self.command_history:
            return "break"
        
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.replace_current_line(self.command_history[self.history_index])
        else:
            # 如果已经到最后一条历史记录，则清空当前行
            self.history_index = len(self.command_history)
            self.replace_current_line("")
        
        return "break"
    
    def replace_current_line(self, text):
        """替换当前行的内容"""
        # 删除当前行内容
        self.interactive_console.delete(self.prompt_position, tk.END)
        # 插入新内容
        self.interactive_console.insert(self.prompt_position, text, "input")
    
    def execute_command(self, command):
        """执行Cilly命令"""
        # 重定向输出
        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output
        
        try:
            # 执行命令
            tokens = cilly_lexer(command)
            ast = cilly_parser(tokens)
            
            # 初始化或重用交互环境
            if self.interactive_env is None:
                result, self.interactive_env = cilly_eval(ast)
            else:
                # 使用现有环境继续执行，不重置
                result, self.interactive_env = cilly_eval(ast, self.interactive_env)
            
            # 获取输出
            output = redirected_output.getvalue()
            
            # 显示输出
            if output:
                self.interactive_console.insert(tk.END, output, "output")
                
            # 显示返回值（如果有且不是None）
            if result is not None and result[0] != 'null':
                self.interactive_console.insert(tk.END, str(val(result)) + "\n", "output")
                
        except Exception as e:
            # 显示错误
            error_message = str(e)
            self.interactive_console.insert(tk.END, "错误: " + error_message + "\n", "error")
            
        finally:
            # 恢复标准输出
            sys.stdout = old_stdout
            
            # 插入新提示符
            self.insert_prompt()
            
            # 滚动到底部
            self.interactive_console.see(tk.END)
    
    def clear_interactive_console(self):
        """清空交互式控制台"""
        self.interactive_console.delete("1.0", tk.END)
        
        # 可选：重置环境
        if messagebox.askyesno("重置环境", "是否同时重置所有变量？"):
            self.interactive_env = None
            self.interactive_console.insert(tk.END, "环境已重置。\n", "output")
        
        self.insert_prompt()
        self.interactive_console.focus_set()
    
    def close_interactive_window(self):
        """关闭交互模式窗口"""
        self.interactive_window.destroy()

    def run_code(self):
        """运行用户编写的代码"""
        code = self.code_editor.get("1.0", tk.END)
        
        # 增加运行次数
        self.run_count += 1
        
        # 在输出区域添加分隔符
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, f"\n{'='*50}\n运行 #{self.run_count}\n{'='*50}\n")
        self.output_text.config(state=tk.DISABLED)
        
        try:
            # 重置环境 - 只在主界面重置
            reset_environment()
            
            # 词法分析
            tokens = cilly_lexer(code)
            # 语法分析
            ast = cilly_parser(tokens)
            
            # 执行代码
            old_stdout = sys.stdout
            redirected_output = io.StringIO()
            sys.stdout = redirected_output
            
            try:
                result, _ = cilly_eval(ast)  # 忽略环境，因为主界面每次都重置
                output = redirected_output.getvalue()
                self.output_text.config(state=tk.NORMAL)
                self.output_text.insert(tk.END, output)
                self.output_text.config(state=tk.DISABLED)
                self.status_bar.config(text=f"运行 #{self.run_count} 完成")
            finally:
                sys.stdout = old_stdout
                    
        except Exception as e:
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, f"错误: {str(e)}\n")
            self.output_text.config(state=tk.DISABLED)
            self.status_bar.config(text=f"运行 #{self.run_count} 出错")

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
