from lexical_analyzer import error
from eval import mk_num, mk_str, mk_bool, val, NULL, TRUE, FALSE
from lexical_analyzer import cilly_lexer
from syntactic_analyzer import cilly_parser
from eval import cilly_eval

'''
very simple stack machine
'''

# 3 + 5 * 6

PUSH = 1
ADD = 2
SUB = 3
MUL = 4
DIV = 5

POP = 6

PRINT = 7

p1 = [
    PUSH, 3,
    PUSH, 5,
    PUSH, 6,
    MUL,
    ADD,
    PRINT,
]


class Stack:
    def __init__(self):
        self.stack = []

    def push(self, v):
        self.stack.append(v)

    def pop(self):
        return self.stack.pop()

    def top(self):
        return self.stack[-1]

    def empty(self):
        return len(self.stack) == 0


def simple_stack_vm(code):
    pc = 0

    def err(msg):
        error('simple stack machine', msg)

    stack = Stack()

    def push(v):
        return stack.push(v)

    def pop():
        return stack.pop()

    while pc < len(code):

        opcode = code[pc]

        if opcode == PUSH:
            v = code[pc + 1]
            push(v)
            pc = pc + 2
        elif opcode == PRINT:
            v = pop()
            print(v)
            pc = pc + 1
        elif opcode == ADD:
            v2 = pop()
            v1 = pop()
            push(v1 + v2)
            pc = pc + 1
        elif opcode == SUB:
            v2 = pop()
            v1 = pop()
            push(v1 - v2)
            pc = pc + 1
        elif opcode == MUL:
            v2 = pop()
            v1 = pop()
            push(v1 * v2)
            pc = pc + 1
        elif opcode == DIV:
            v2 = pop()
            v1 = pop()
            push(v1 / v2)
            pc = pc + 1
        else:
            err(f'非法opcode: {opcode}')


'''
cilly vm: stack machine
'''

LOAD_CONST = 1

LOAD_NULL = 2
LOAD_TRUE = 3
LOAD_FALSE = 4

LOAD_VAR = 5
STORE_VAR = 6

PRINT_ITEM = 7
PRINT_NEWLINE = 8

JMP = 9
JMP_TRUE = 10
JMP_FALSE = 11

POP = 12

ENTER_SCOPE = 13
LEAVE_SCOPE = 14

UNARY_NEG = 101
UNARY_NOT = 102

BINARY_ADD = 111
BINARY_SUB = 112
BINARY_MUL = 113
BINARY_DIV = 114
BINARY_MOD = 115
BINARY_POW = 116

BINARY_EQ = 117
BINARY_NE = 118
BINARY_LT = 119  # <
BINARY_GE = 120  # >=

# 新增函数相关操作码
MAKE_FUNCTION = 20
CALL_FUNCTION = 21
RETURN = 22

OPS_NAME = {
    LOAD_CONST: ('LOAD_CONST', 2),

    LOAD_NULL: ('LOAD_NULL', 1),
    LOAD_TRUE: ('LOAD_TRUE', 1),
    LOAD_FALSE: ('LOAD_FALSE', 1),

    LOAD_VAR: ('LOAD_VAR', 3),
    STORE_VAR: ('STORE_VAR', 3),

    PRINT_ITEM: ('PRINT_ITEM', 1),
    PRINT_NEWLINE: ('PRINT_NEWLINE', 1),

    POP: ('POP', 1),

    ENTER_SCOPE: ('ENTER_SCOPE', 2),
    LEAVE_SCOPE: ('LEAVE_SCOPE', 1),

    JMP: ('JMP', 2),
    JMP_TRUE: ('JMP_TRUE', 2),
    JMP_FALSE: ('JMP_FALSE', 2),

    UNARY_NEG: ('UNARY_NEG', 1),
    UNARY_NOT: ('UNARY_NOT', 1),

    BINARY_ADD: ('BINARY_ADD', 1),
    BINARY_SUB: ('BINARY_SUB', 1),
    BINARY_MUL: ('BINARY_MUL', 1),
    BINARY_DIV: ('BINARY_DIV', 1),
    BINARY_MOD: ('BINARY_MOD', 1),
    BINARY_POW: ('BINARY_POW', 1),

    BINARY_EQ: ('BINARY_EQ', 1),
    BINARY_NE: ('BINARY_NE', 1),
    BINARY_LT: ('BINARY_LT', 1),
    BINARY_GE: ('BINARY_GE', 1),

    MAKE_FUNCTION: ('MAKE_FUNCTION', 2),
    CALL_FUNCTION: ('CALL_FUNCTION', 1),
    RETURN: ('RETURN', 1),

}


def cilly_vm(code, consts, scopes):
    def err(msg):
        error('cilly vm', msg)

    stack = Stack()
    call_stack = []  # 用于保存函数调用的返回地址和局部变量

    def push(v):
        stack.push(v)

    def pop():
        return stack.pop()

    def load_const(pc):
        index = code[pc + 1]
        v = consts[index]
        push(v)
        return pc + 2

    def load_null(pc):
        push(NULL)
        return pc + 1

    def load_true(pc):
        push(TRUE)
        return pc + 1

    def load_false(pc):
        push(FALSE)
        return pc + 1

    def load_var(pc):
        scope_i = code[pc + 1]
        if scope_i >= len(scopes):
            err(f'作用域索引超出访问: {scope_i}')
        scope = scopes[-scope_i - 1]
        index = code[pc + 2]
        if index >= len(scope):
            err(f'load_var变量索引超出范围:{index}')
        push(scope[index])
        return pc + 3

    def store_var(pc):
        scope_i = code[pc + 1]
        if scope_i >= len(scopes):
            err(f'作用域索引超出访问: {scope_i}')
        scope = scopes[-scope_i - 1]
        index = code[pc + 2]
        if index >= len(scope):
            err(f'store_var变量索引超出范围:{index}')
        scope[index] = pop()
        return pc + 3

    def enter_scope(pc):
        var_count = code[pc + 1]
        scope = [NULL for _ in range(var_count)]
        nonlocal scopes
        scopes = scopes + [scope]
        return pc + 2

    def leave_scope(pc):
        nonlocal scopes
        scopes = scopes[:-1]
        return pc + 1

    def print_item(pc):
        v = val(pop())
        print(v, end=' ')
        return pc + 1

    def print_newline(pc):
        print('')
        return pc + 1

    def pop_proc(pc):
        pop()
        return pc + 1

    def jmp(pc):
        target = code[pc + 1]
        return target

    def jmp_true(pc):
        target = code[pc + 1]
        if pop() == TRUE:
            return target
        else:
            return pc + 2

    def jmp_false(pc):
        target = code[pc + 1]
        if pop() == FALSE:
            return target
        else:
            return pc + 2

    def unary_op(pc):
        v = val(pop())
        opcode = code[pc]
        if opcode == UNARY_NEG:
            push(mk_num(-v))
        elif opcode == UNARY_NOT:
            push(mk_bool(not v))
        else:
            err(f'非法一元opcode: {opcode}')
        return pc + 1

    def binary_op(pc):
        v2 = val(pop())
        v1 = val(pop())
        opcode = code[pc]
        if opcode == BINARY_ADD:
            push(mk_num(v1 + v2))
        elif opcode == BINARY_SUB:
            push(mk_num(v1 - v2))
        elif opcode == BINARY_MUL:
            push(mk_num(v1 * v2))
        elif opcode == BINARY_DIV:
            push(mk_num(v1 / v2))
        elif opcode == BINARY_MOD:
            push(mk_num(v1 % v2))
        elif opcode == BINARY_POW:
            push(mk_num(v1 ** v2))
        elif opcode == BINARY_EQ:
            push(mk_bool(v1 == v2))
        elif opcode == BINARY_NE:
            push(mk_bool(v1 != v2))
        elif opcode == BINARY_LT:
            push(mk_bool(v1 < v2))
        elif opcode == BINARY_GE:
            push(mk_bool(v1 >= v2))
        else:
            err(f'非法二元opcode:{opcode}')
        return pc + 1

    def make_function(pc):
        index = code[pc + 1]
        fun_code = consts[index]
        push(['function', fun_code])
        return pc + 2

    def call_function(pc):
        arg_count = code[pc + 1]
        # 获取函数对象
        fun = pop()
        if not isinstance(fun, list) or fun[0] != 'function':
            err('调用非函数对象')
        # 获取参数
        args = []
        for _ in range(arg_count):
            args.insert(0, pop())
        # 保存当前状态
        nonlocal scopes
        call_stack.append((pc + 2, scopes))
        # 创建新的作用域
        scopes = [[]]
        # 设置参数
        for arg in args:
            scopes[0].append(arg)
        # 执行函数代码
        return 0  # 从函数代码开始处执行

    def return_proc(pc):
        if not call_stack:
            err('在非函数上下文中返回')
        # 获取返回值
        ret_val = pop()
        # 恢复调用前的状态
        pc, scopes = call_stack.pop()
        # 将返回值压入栈
        push(ret_val)
        return pc

    ops = {
        LOAD_CONST: load_const,
        LOAD_NULL: load_null,
        LOAD_TRUE: load_true,
        LOAD_FALSE: load_false,
        LOAD_VAR: load_var,
        STORE_VAR: store_var,
        ENTER_SCOPE: enter_scope,
        LEAVE_SCOPE: leave_scope,
        PRINT_ITEM: print_item,
        PRINT_NEWLINE: print_newline,
        POP: pop_proc,
        JMP: jmp,
        JMP_TRUE: jmp_true,
        JMP_FALSE: jmp_false,
        UNARY_NEG: unary_op,
        UNARY_NOT: unary_op,
        BINARY_ADD: binary_op,
        BINARY_SUB: binary_op,
        BINARY_MUL: binary_op,
        BINARY_DIV: binary_op,
        BINARY_MOD: binary_op,
        BINARY_POW: binary_op,
        BINARY_EQ: binary_op,
        BINARY_NE: binary_op,
        BINARY_LT: binary_op,
        BINARY_GE: binary_op,
        MAKE_FUNCTION: make_function,
        CALL_FUNCTION: call_function,
        RETURN: return_proc,
    }

    def get_opcode_proc(opcode):
        if opcode not in ops:
            err(f'非法opcode: {opcode}')
        return ops[opcode]

    def run():
        pc = 0
        while pc < len(code):
            opcode = code[pc]
            proc = get_opcode_proc(opcode)
            pc = proc(pc)

    run()


'''
cilly vm反汇编器
'''


def cilly_vm_dis(code, consts, var_names):
    def err(msg):
        error('cilly vm disassembler', msg)

    pc = 0

    while pc < len(code):
        opcode = code[pc]

        if opcode == LOAD_CONST:
            index = code[pc + 1]
            if index < len(consts):
                v = consts[index]
                print(f'{pc}\t LOAD_CONST {index} ({v})')
            else:
                print(f'{pc}\t LOAD_CONST {index} (invalid index)')
            pc = pc + 2
        elif opcode == LOAD_VAR:
            scope_i = code[pc + 1]
            index = code[pc + 2]
            if scope_i < len(var_names) and index < len(var_names[-scope_i - 1]):
                var_name = var_names[-scope_i - 1][index]
                print(f'{pc}\t LOAD_VAR {scope_i} {index} ({var_name})')
            else:
                print(f'{pc}\t LOAD_VAR {scope_i} {index}')
            pc = pc + 3
        elif opcode == STORE_VAR:
            scope_i = code[pc + 1]
            index = code[pc + 2]
            if scope_i < len(var_names) and index < len(var_names[-scope_i - 1]):
                var_name = var_names[-scope_i - 1][index]
                print(f'{pc}\t STORE_VAR {scope_i} {index} ({var_name})')
            else:
                print(f'{pc}\t STORE_VAR {scope_i} {index}')
            pc = pc + 3
        elif opcode in OPS_NAME:
            name, size = OPS_NAME[opcode]

            print(f'{pc}\t {name}', end='')

            if size > 1:
                print(f' {code[pc + 1]}', end='')
                if size > 2:
                    print(f' {code[pc + 2]}', end='')

            print('')
            pc = pc + size
        else:
            err(f'非法opcode:{opcode}')


'''
Cilly vm compiler
'''


def cilly_vm_compiler(ast, code, consts, scopes):
    def err(msg):
        error('cilly vm compiler', msg)

    def add_const(c):
        for i in range(len(consts)):
            if consts[i] == c:
                return i
        consts.append(c)
        return len(consts) - 1

    def get_next_emit_addr():
        return len(code)

    def emit(opcode, operand1=None, operand2=None):
        addr = get_next_emit_addr()
        code.append(opcode)
        if operand1 != None:
            code.append(operand1)
        if operand2 != None:
            code.append(operand2)
        return addr

    def backpatch(addr, operand1=None, operand2=None):
        if operand1 != None:
            code[addr + 1] = operand1
        if operand2 != None:
            code[addr + 2] = operand2

    def define_var(name):
        scope = scopes[-1]
        for i in range(len(scope)):
            if scope[i] == name:
                err(f'已定义变量: {name}')
        scope.append(name)
        return len(scope) - 1

    def lookup_var(name):
        for scope_i in range(len(scopes)):
            scope = scopes[-scope_i - 1]
            for index in range(len(scope)):
                if scope[index] == name:
                    return scope_i, index
        # 对于前向引用，我们返回全局作用域的索引
        # 这样在运行时可以访问到后续定义的函数
        return 0, len(scopes[0]) - 1

    def compile_program(node):
        _, statements = node
        # 创建全局作用域
        nonlocal scopes
        scopes = [[]]  # 初始化全局作用域
        # 先处理所有变量定义，包括函数定义
        for stmt in statements:
            if stmt[0] == 'define':
                define_var(stmt[1])
            elif stmt[0] == 'fun':
                define_var(stmt[1])  # 为函数名创建变量
        # 编译所有语句
        visit(['block', statements])

    def compile_expr_stat(node):
        _, e = node
        visit(e)
        emit(POP)

    def compile_print(node):
        _, args = node
        for a in args:
            visit(a)
            emit(PRINT_ITEM)
        emit(PRINT_NEWLINE)

    def compile_literal(node):
        tag = node[0]
        if tag == 'null':
            emit(LOAD_NULL)
        elif tag == 'true':
            emit(LOAD_TRUE)
        elif tag == 'false':
            emit(LOAD_FALSE)
        elif tag in ['num', 'str']:
            index = add_const(node)
            emit(LOAD_CONST, index)

    def compile_unary(node):
        _, op, e = node
        visit(e)
        if op == '-':
            emit(UNARY_NEG)
        elif op == '!':
            emit(UNARY_NOT)
        else:
            err(f'非法一元运算符：{op}')

    def compile_binary(node):
        _, op, e1, e2 = node
        if op == '&&':
            visit(e1)
            addr1 = emit(JMP_FALSE, -1)
            visit(e2)
            addr2 = emit(JMP, -1)
            backpatch(addr1, get_next_emit_addr())
            emit(LOAD_FALSE)
            backpatch(addr2, get_next_emit_addr())
            return

        if op == '||':
            visit(e1)
            addr1 = emit(JMP_TRUE, -1)
            visit(e2)
            addr2 = emit(JMP, -1)
            backpatch(addr1, get_next_emit_addr())
            emit(LOAD_TRUE)
            backpatch(addr2, get_next_emit_addr())
            return

        if op in ['>', '<=']:
            visit(e2)
            visit(e1)
            if op == '>':
                emit(BINARY_LT)
            else:
                emit(BINARY_GE)
            return

        visit(e1)
        visit(e2)

        if op == '+':
            emit(BINARY_ADD)
        elif op == '-':
            emit(BINARY_SUB)
        elif op == '*':
            emit(BINARY_MUL)
        elif op == '/':
            emit(BINARY_DIV)
        elif op == '%':
            emit(BINARY_MOD)
        elif op == '^':
            emit(BINARY_POW)
        elif op == '==':
            emit(BINARY_EQ)
        elif op == '!=':
            emit(BINARY_NE)
        elif op == '<':
            emit(BINARY_LT)
        elif op == '>=':
            emit(BINARY_GE)
        else:
            err(f'非法二元运算符：{op}')

    def compile_if(node):
        _, cond, true_s, false_s = node
        visit(cond)
        addr1 = emit(JMP_FALSE, -1)
        visit(true_s)
        if false_s == None:
            backpatch(addr1, get_next_emit_addr())
        else:
            addr2 = emit(JMP, -1)
            backpatch(addr1, get_next_emit_addr())
            visit(false_s)
            backpatch(addr2, get_next_emit_addr())

    def compile_block(node):
        _, statements = node
        nonlocal scopes
        # 创建新的作用域并添加变量名
        scope = []
        scopes = scopes + [scope]
        addr = emit(ENTER_SCOPE, -1)
        for s in statements:
            visit(s)
        emit(LEAVE_SCOPE)
        backpatch(addr, len(scope))
        scopes = scopes[:-1]

    def compile_define(node):
        _, name, e = node
        visit(e)
        index = define_var(name)
        # 确保变量名被添加到当前作用域
        if len(scopes[-1]) <= index:
            scopes[-1].append(name)
        emit(STORE_VAR, 0, index)

    def compile_assign(node):
        _, name, e = node
        visit(e)
        scope_i, index = lookup_var(name)
        emit(STORE_VAR, scope_i, index)

    def compile_id(node):
        _, name, _, _ = node
        scope_i, index = lookup_var(name)
        emit(LOAD_VAR, scope_i, index)

    def compile_fun(node):
        _, params, body = node
        # 保存当前作用域
        nonlocal scopes
        old_scopes = scopes
        # 创建新的作用域
        scopes = [[]]
        # 为参数创建变量
        for param in params:
            define_var(param)
        # 保存当前代码长度
        start_addr = len(code)
        # 编译函数体
        visit(body)
        # 如果没有显式的return语句，添加一个返回null
        if code[-1] != RETURN:
            emit(RETURN)
        # 获取函数代码
        fun_code = code[start_addr:]
        # 恢复原来的作用域
        scopes = old_scopes
        # 将函数代码添加到常量表
        index = add_const(fun_code)
        emit(MAKE_FUNCTION, index)

    def compile_fun_stat(node):
        _, name, params, body = node
        # 编译函数体
        visit(['fun', params, body])
        # 存储函数到变量
        index = define_var(name)
        emit(STORE_VAR, 0, index)

    def compile_call(node):
        _, fun, args = node
        # 编译函数表达式
        visit(fun)
        # 编译参数
        for arg in args:
            visit(arg)
        # 调用函数
        emit(CALL_FUNCTION, len(args))

    def compile_return(node):
        _, e = node
        # 编译返回值表达式
        visit(e)
        # 生成返回指令
        emit(RETURN)

    visitors = {
        'program': compile_program,
        'expr_stat': compile_expr_stat,
        'print': compile_print,
        'if': compile_if,
        'define': compile_define,
        'assign': compile_assign,
        'block': compile_block,
        'unary': compile_unary,
        'binary': compile_binary,
        'id': compile_id,
        'num': compile_literal,
        'str': compile_literal,
        'true': compile_literal,
        'false': compile_literal,
        'null': compile_literal,
        'fun': compile_fun,
        'fun_stat': compile_fun_stat,
        'call': compile_call,
        'return': compile_return,
    }

    def visit(node):
        tag = node[0]
        if tag not in visitors:
            err(f'非法ast节点: {tag}')
        v = visitors[tag]
        v(node)

    visit(ast)
    return code, consts, scopes


# p1 = '''
# 1;
# "hello";
# print(123,"hello", "world", true);
# '''

# p1 = '''
# 1 + 2 * 3;
# print(3 *4 - 5, 6 / 2);
# '''

# p1 = '''
# print(false && true);
# '''

# p1 = '''
# if(1 > 2)
#     print(3);
# else
#     print(4);
# '''

# p1 = '''
# if( 1 > 2)
#     print(3);
# print(4);
# '''

# p1 = '''
# if( 1 > 2 && 5 > 4)
#     print(30);
# else
#     print(42);
# '''

# p1 = '''
# var x1 = 100;
#
# {
#     var x1 = 200;
#     {
#         var x1 = 300;
#         print("inner x1", x1);
#     }
#     print("middle x1", x1);
# }
#
# print("outer x1", x1);
# '''

p1 = '''
var odd = fun(n){
  if(n == 1)
    return true;
  else
   return even(n-1);
};
var even = fun(n) {
 if(n==0)
   return true;
 else
   return odd(n-1);
};

print(even(3), odd(3));
'''

ts = cilly_lexer(p1)
print("tokens:", ts)

ast = cilly_parser(ts)
print("ast:", ast)

code, consts, scopes = cilly_vm_compiler(ast, [], [], [])
print("code:", code)
print("consts:", consts)
print("scopes:", scopes)
cilly_vm_dis(code, consts, scopes)
