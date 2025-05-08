import time
from lexical_analyzer import cilly_lexer
from syntactic_analyzer import cilly_parser
from vm import cilly_vm_compiler, cilly_vm
from eval import cilly_eval, reset_environment

def test_performance(code, iterations=10):
    """比较虚拟机和解释器的性能"""
    print(f"程序代码:\n{code}\n")
    
    # 解析代码
    tokens = cilly_lexer(code)
    ast = cilly_parser(tokens)
    
    # 测试解释器性能
    reset_environment()
    total_eval_time = 0
    
    for _ in range(iterations):
        reset_environment()
        start_time = time.time()
        cilly_eval(ast)
        end_time = time.time()
        total_eval_time += (end_time - start_time)
    
    avg_eval_time = total_eval_time / iterations
    
    # 测试虚拟机性能
    total_vm_time = 0
    
    for _ in range(iterations):
        start_time = time.time()
        code_obj, consts, scopes = cilly_vm_compiler(ast, [], [], [])
        cilly_vm(code_obj, consts, scopes)
        end_time = time.time()
        total_vm_time += (end_time - start_time)
    
    avg_vm_time = total_vm_time / iterations
    
    # 输出结果
    print(f"解释器平均执行时间: {avg_eval_time:.6f} 秒")
    print(f"虚拟机平均执行时间: {avg_vm_time:.6f} 秒")
    
    # 避免除零错误
    if avg_eval_time <= 0.000001:
        print("解释器执行时间太短，无法准确计算性能比")
    elif avg_vm_time <= 0.000001:
        print("虚拟机执行时间太短，无法准确计算性能比")
    elif avg_vm_time < avg_eval_time:
        speedup = avg_eval_time / avg_vm_time
        print(f"虚拟机比解释器快 {speedup:.2f} 倍")
    else:
        speedup = avg_vm_time / avg_eval_time
        print(f"解释器比虚拟机快 {speedup:.2f} 倍")
    
    print("-" * 50)

# 测试用例
test_cases = [
    # 简单计算
    """
    1 + 2 * 3;
    print(3 * 4 - 5, 6 / 2);
    """,
    
    # 条件判断
    """
    if(1 > 2)
        print(3);
    else
        print(4);
    """,
    
    # # 作用域和变量
    # """
    # var x1 = 100;
    # {
    #     var x2 = 200;
    #     {
    #         var x3 = 300;
    #         print("inner x3", x3);
    #     }
    #     print("middle x2", x2);
    # }
    # print("outer x1", x1);
    # """,
    
    # 简单递归函数调用 (避免过深递归)
    # """
    # var odd = fun(n){
    #   if(n == 1)
    #     return true;
    #   else
    #    return even(n-1);
    # };
    # var even = fun(n) {
    #  if(n==0)
    #    return true;
    #  else
    #    return odd(n-1);
    # };
    
    # # print(even(4), odd(3));
    # # """,
    
    # 简单的斐波那契计算 (避免过深递归)
    # """
    # var fib = fun(n) {
    #     if (n <= 1)
    #         return n;
    #     else
    #         return fib(n-1) + fib(n-2);
    # };
    
    # print(fib(8)); // 计算第8个斐波那契数
    # """,
    
    # # 循环测试
    # """
    # var sum = 0;
    # var i = 0;
    # while (i < 50) {
    #     sum = sum + i;
    #     i = i + 1;
    # }
    # print("Sum of 0 to 49:", sum);
    # """
]

if __name__ == "__main__":
    print("开始性能测试...\n")
    for i, test_code in enumerate(test_cases):
        print(f"测试用例 {i+1}:")
        test_performance(test_code) 