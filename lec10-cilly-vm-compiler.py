# from cilly_lexer_parser import error
# from cilly_lexer_parser import mk_num, mk_str, mk_bool, val, NULL, TRUE, FALSE
#
# from cilly_lexer_parser import cilly_lexer, cilly_parser
from lexical_analyzer import error,cilly_lexer
from syntactic_analyzer import cilly_parser
from eval import mk_num,mk_str,mk_bool,val,NULL,TRUE,FALSE

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
            v = code[pc+1]
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
BINARY_LT = 119 # <
BINARY_GE = 120 # >=

OPS_NAME = {
    LOAD_CONST : ('LOAD_CONST', 2),

    LOAD_NULL : ('LOAD_NULL', 1),
    LOAD_TRUE : ('LOAD_TRUE', 1),
    LOAD_FALSE : ('LOAD_FALSE', 1),

    LOAD_VAR : ('LOAD_VAR', 3),
    STORE_VAR : ('STORE_VAR', 3),

    PRINT_ITEM : ('PRINT_ITEM', 1),
    PRINT_NEWLINE : ('PRINT_NEWLINE', 1),

    POP : ('POP', 1),
    
    ENTER_SCOPE : ('ENTER_SCOPE', 2),
    LEAVE_SCOPE : ('LEAVE_SCOPE', 1),
    
    JMP : ('JMP', 2),
    JMP_TRUE : ('JMP_TRUE', 2),
    JMP_FALSE : ('JMP_FALSE', 2),

    UNARY_NEG : ('UNARY_NEG', 1),
    UNARY_NOT : ('UNARY_NOT', 1),

    BINARY_ADD : ('BINARY_ADD', 1),
    BINARY_SUB : ('BINARY_SUB', 1),
    BINARY_MUL : ('BINARY_MUL', 1),
    BINARY_DIV : ('BINARY_DIV', 1),
    BINARY_MOD : ('BINARY_MOD', 1),
    BINARY_POW : ('BINARY_POW', 1),

    BINARY_EQ : ('BINARY_EQ', 1),
    BINARY_NE : ('BINARY_NE', 1),
    BINARY_LT : ('BINARY_LT', 1),
    BINARY_GE : ('BINARY_GE', 1),
    
}        
def cilly_vm(code, consts, scopes):
    
    def err(msg):
        error('cilly vm', msg)
    
    stack = Stack()
    
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
            
        push( scope[index] )
        
        return pc + 3
    
    def store_var(pc):
        scope_i = code[pc + 1]
        if scope_i >= len(scopes):
            err(f'作用域索引超出访问: {scope_i}')
            
        scope = scopes[-scope_i - 1]
        
        index = code[pc + 2]
        if index >= len(scope):
            err(f'load_var变量索引超出范围:{index}')
            
        scope[index] = pop()
        
        return pc + 3
    
    def enter_scope(pc):
        var_count = code[pc + 1]
        
        scope = [NULL for _ in range(var_count)]
        nonlocal scopes
        
        scopes = scopes + [scope] #不用scopes.append(scope)
        
        return pc + 2
    
    def leave_scope(pc):
        nonlocal scopes
        scopes = scopes[:-1] #不用scopes.pop()
        
        return pc + 1
    def print_item(pc):
        v = val( pop() )
        print(v, end = ' ')
        return pc + 1
        
    def print_newline(pc):
        print('')
        
        return pc + 1
    
    def pop_proc(pc):
        pop()
        return pc + 1
    
    def jmp(pc):
        target = code[pc+1]
        
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
        v = val( pop() )
        
        opcode = code[pc]
        
        if opcode == UNARY_NEG:
            push( mk_num(-v) )
        elif opcode == UNARY_NOT:
            push( mk_bool(not v ) )
        else:
            err(f'非法一元opcode: {opcode}')
            
        return pc + 1
            
    def binary_op(pc):
        v2 = val( pop() )
        v1 = val( pop() )
        
        opcode = code[pc]
        
        if opcode == BINARY_ADD:
            push( mk_num(v1 + v2) )
        elif opcode == BINARY_SUB:
            push( mk_num(v1 - v2) )
        elif opcode == BINARY_MUL:
            push( mk_num(v1 * v2) )
        elif opcode == BINARY_DIV:
            push( mk_num(v1 / v2) )
        elif opcode == BINARY_MOD:
            push( mk_num(v1 % v2) )
        elif opcode == BINARY_POW:
            push( mk_num(v1 ** v2) )
        elif opcode == BINARY_EQ:
            push( mk_bool(v1 == v2) )
        elif opcode == BINARY_NE:
            push( mk_bool(v1 != v2) )
        elif opcode == BINARY_LT:
            push( mk_bool(v1 < v2) )
        elif opcode == BINARY_GE:
            push( mk_bool(v1 >= v2) )
        else:
            err(f'非法二元opcode:{opcode}')
        
        return pc + 1
                  
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
            
consts = [
    mk_num(3),
    mk_num(5),
    mk_num(6),
]
vars = [
    mk_num(100), # a
    mk_num(200), # b,
    NULL, #c
]
# 3 + 5 * 6

p1 = [
    LOAD_CONST, 0,
    LOAD_CONST, 1,
    LOAD_CONST, 2,
    BINARY_MUL,
    BINARY_ADD,
    PRINT_ITEM,
    PRINT_NEWLINE,
]

# c = a + b * 5

p1 = [
    LOAD_VAR, 0, # push a
    LOAD_VAR, 1, # push b
    LOAD_CONST, 1, #push 5
    
    BINARY_MUL, # b * 5
    BINARY_ADD, # a + b * 5
    
    STORE_VAR, 2, #c = pop()
    
    LOAD_VAR, 2, #push c
    PRINT_ITEM,  #print c
    PRINT_NEWLINE,
]

'''
var i = 1;
var sum = 0;

while (i <= 100){
    sum = sum + i;
    i = i + 1;
}

print(sum);
'''
consts = [
    mk_num(0),
    mk_num(1),
    mk_num(100),
]
vars = [
    NULL, #i
    NULL, #sum
]

p1 = [
    # i = 1
    LOAD_CONST, 1,
    STORE_VAR, 0,
    
    # sum = 0
    LOAD_CONST, 0,
    STORE_VAR, 1,
    
    # while ( i <= 100 ) {
    LOAD_CONST, 2,
    LOAD_VAR, 0,
    BINARY_LT,
    
    JMP_TRUE, 31, #i > 100退出while循环
    
    #sum = sum + i
    LOAD_VAR, 1,
    LOAD_VAR, 0,
    BINARY_ADD,
    STORE_VAR, 1,
    
    #i = i + 1
    LOAD_VAR, 0,
    LOAD_CONST, 1,
    BINARY_ADD,
    STORE_VAR, 0,
    
    JMP, 8,
    #}
    
    # print sum
    LOAD_VAR, 1,
    PRINT_ITEM,
    PRINT_NEWLINE,
    
]
#cilly_vm(p1, consts, vars)

def sum100():
    i = 1
    sum = 0
    while i <= 100:
        sum = sum + i
        i = i + 1
        
    print(sum)
        
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
            v = consts[index]
            
            print(f'{pc}\t LOAD_CONST {index} ({v})')
            
            pc = pc + 2
        elif opcode in OPS_NAME:
            name, size = OPS_NAME[opcode]
            
            print(f'{pc}\t {name}', end='')
            
            if size > 1:
                print(f' {code[pc+1]}', end='')
                if size > 2:
                    print(f' {code[pc+2]}', end='')
                    
            print('')
            pc = pc + size
        else:
            err(f'非法opcode:{opcode}')
        
vars_name = [
    'i',
    'sum',
]

#cilly_vm_dis(p1, consts, vars_name)

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
    
    def emit(opcode, operand1 = None, operand2 = None):
        
        addr = get_next_emit_addr()
        
        code.append(opcode)
        
        if operand1 != None:
            code.append(operand1)
            
        if operand2 != None:
            code.append(operand2)
        
        return addr
    
    def backpatch(addr, operand1 = None, operand2 = None):
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
        for scope_i in range( len(scopes) ):
            scope = scopes[-scope_i-1]
            
            for index in range(len(scope)):
                if scope[index] == name:
                    return scope_i, index
                
        err(f'未定义变量：{name}')
        
    def compile_program(node):
        _, statements = node
        
        visit(['block', statements])
        
        #for s in statements:
        #    visit(s)
            

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
            
            
        
        if op in ['>','<=']:
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
        scope = []
        
        #compiler scope: name
        scopes = scopes + [scope]
        
        #vm scope: value
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
        emit(STORE_VAR, 0, index)
        
    def compile_assign(node):
        _, name, e = node
        
        visit(e)
        
        scope_i, index = lookup_var(name)
        emit(STORE_VAR, scope_i, index)
        
    def compile_id(node):
        _, name,_,_ = node
        
        scope_i, index = lookup_var(name)
        emit(LOAD_VAR, scope_i, index)
        
    visitors = {
        'program': compile_program,
         'expr_stat': compile_expr_stat,
         'print': compile_print,
         'if': compile_if,
#         'while': compile_while,
#         'break': compile_break,
#         'continue': compile_continue,
#         
         'define': compile_define,
         'assign': compile_assign,
# 
         'block': compile_block,
#         
          'unary': compile_unary,
          'binary': compile_binary,
#         
         'id': compile_id,
#         
#         'fun': compile_fun,
#         'return': compile_return,
#         'call': compile_call,
#         
        'num': compile_literal,
        'str': compile_literal,
        'true': compile_literal,
        'false': compile_literal,
        'null': compile_literal,
        
    }
    
    def visit(node):
        tag = node[0]
        
        if tag not in visitors:
            err(f'非法ast节点: {tag}')
            
        v = visitors[tag]
        
        v(node)
    
    visit(ast)
    
    return code, consts, scopes

p1 = '''
1;
"hello";
print(123,"hello", "world", true);
'''

p1 = '''
1 + 2 * 3;
print(3 *4 - 5, 6 / 2);
'''

p1 = '''
print(false && true);
'''

p1 = '''
if(1 > 2)
    print(3);
else
    print(4);
'''

p1 = '''
if( 1 > 2)
    print(3);
print(4);
'''

p1 = '''
if( 1 > 2 && 5 > 4)
    print(30);
else
    print(42);
'''

p2 = '''
var x1 = 100;

{
    var x1 = 200;
    {
        var x1 = 300;
        print("inner x1", x1);
    }
    print("middle x1", x1);
}

print("outer x1", x1);
'''
ts = cilly_lexer(p2)
ast = cilly_parser(ts)
code, consts, scopes = cilly_vm_compiler(ast, [], [], [])
cilly_vm_dis(code, consts, scopes)
