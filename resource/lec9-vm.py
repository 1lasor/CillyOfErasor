from cilly_lexer_parser import error
from cilly_lexer_parser import mk_num, mk_str, mk_bool, val, NULL, TRUE, FALSE

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

    LOAD_VAR : ('LOAD_VAR', 2),
    STORE_VAR : ('STORE_VAR', 2),

    PRINT_ITEM : ('PRINT_ITEM', 1),
    PRINT_NEWLINE : ('PRINT_NEWLINE', 1),

    JMP : ('JMP', 2),
    JMP_TRUE : ('JMP_TRUE', 2),
    JMP_FALSE : ('JMP_FALSE', 1),

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
def cilly_vm(code, consts, vars):
    
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
        index = code[pc + 1]
        if index >= len(vars):
            err(f'load_var变量索引超出范围:{index}')
            
        push( vars[index] )
        
        return pc + 2
    
    def store_var(pc):
        index = code[pc + 1]
        if index >= len(vars):
            err(f'store_var变量索引超出范围：{index}')
            
        vars[index] = pop()
        
        return pc + 2
    
    def print_item(pc):
        v = val( pop() )
        print(v, end = '')
        return pc + 1
        
    def print_newline(pc):
        print('')
        
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
        
        PRINT_ITEM: print_item,
        PRINT_NEWLINE: print_newline,
        
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
cilly_vm(p1, consts, vars)

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
        elif opcode == LOAD_VAR:
            index = code[pc+1]
            name = var_names[index]
            
            print(f'{pc}\t LOAD_VAR {index} ({name})')
            
            pc = pc + 2
        elif opcode == STORE_VAR:
            index = code[pc+1]
            name = var_names[index]
            
            print(f'{pc}\t STORE_VAR {index} ({name})')
            
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

cilly_vm_dis(p1, consts, vars_name)
