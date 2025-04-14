'''
cilly 语法

program : statement* EOF

statement
    : define_statement
    | assign_statement
    | print_statement
    | if_statement
    | while_statement
    | continue_statement
    | break_statement
    | return_statement
    | block_statement
    | expr_statement
    ;
    
define_statement
    : 'var' ID '=' expr ';'
    ;
    
assign_statement
    : ID '=' expr ';'
    ;
    
print_statement
    : 'print' '(' args? ')' ';'
    ;
    
args : expr (',' expr)* ;

if_statement
    : 'if' '(' expr ')' statement ('else' statement)?
    ;
    
while_statement
    : 'while' '(' expr ')' statement
    ;
    
continue_statement
    : 'continue' ';'
    ;
    
break_statement
    : 'break' ';'
    ;
    
return_statement
    : 'return' expr? ';'
    ;
    
block_statement
    : '{' statement* '}'
    ;
    
expr_statement:
    : expr ';'
    
expr
    : id | num | string | 'true' | 'false' | 'null'
    | '(' expr ')'
    | ('-' | '!') expr
    | expr ('+' | '-' | '*' | '/' | '==' | '!=' | '>' | '>=' | '<' | '<=' | '&&' | '||') expr
    | 'fun' '(' params? ')' block_statement
    | expr '(' args? ')'
    ;

表达式实现
方法1：改造文法

expr: logic_expr
logic_expr : rel_expr ('&&' rel_expr)*
rel_expr : add_expr ('>' add_expr)*
add_expr : mul_expr ('+' mul_expr)*
mul_expr : unary ('*' unary)*
unary : factor | '-' unary
factor : id | num | ....

方法2： pratt解析

   1     +    2
     30    40
     
   1     *    2
     50     60
     
   1  +   2   *  3
        40  50
        
   1  +   2  +   3
       40   30
comment : '#' 非换行符号 '\r'? '\n'
    
cilly 词法
program : token* 'eof'

token
    : id | num | string
    | 'true' | 'false' | 'null'
    | 'var' | 'if' | 'else' | 'while' | 'continue' | 'break' | 'return' | 'fun'
    | '(' | ')' | '{' | '}' | ','
    | '=' | '=='
    | '+' | '-' | '*' | '/'
    | '!' | '!='
    | '>' | '>='
    | '<' | '<='
    | '&&' | '||'
    ;
    
num : [0-9]+ ('.' [0-9]*)? 
string : '"' char* '"'
char : 不是双引号的字符
ws : (' ' | '\r' | '\n' | '\t)+

 
'''

p1 = '''
    var pi = 3.1415926;
    
    var area = fun(r) {
        return pi * r * r;
    } ;
    
    print(area(10), area(20));
    
    var abs = fun(x) {
        if(x < 0)
            return -x;
        else
            return x;
    } ;
    
    var sqrt = fun(x) {
        var iter = fun(guess) {
            if( abs(x - guess * guess) < 0.0001 )
                return guess;
            else
                return iter((guess + x / guess) / 2);
        };
        
        return iter(1);
    
    };
    
    print(sqrt(2), sqrt(2) * sqrt(2));
    
    var make_counter = fun(i) {
        return fun() {
            i = i + 1;
            return i;
        };
    };
    
    var c1 = make_counter(0);
    var c2 = make_counter(0);
    
    print(c1(), c1(), c2());
    
    var K = fun(a) {
        return fun(b) {
            return a;
        };
    };
    
    var KI = fun(a) {
        return fun(b) {
            return b;
        };
    };

    var pair = fun(a,b) {
        return fun(f) {
            return f(a)(b);
        };
    };
    
    var first = fun(p) {
        return p(K);
    };
    
    var second = fun(p) {
        return p(KI);
    };
    
    var p = pair(1,2);
    
    print(first(p), second(p));
    
    var fact = fun(n) {
        if(n == 0)
            return 1;
        else
            return n * fact(n-1);
   };
   
   var fact2 = fun(n) {
       var r = 1;
       var i = n;
       
       while(n > 0) {
           r = n * r;
           n = n - 1;
       }
       
       return r;
       
   };
'''

def error(src, msg):
    raise Exception(f'{src} : {msg}')

def mk_tk(tag, val=None):
    return [tag, val]

def tk_tag(t):
    return t[0]

def tk_val(t):
    return t[1]

def make_str_reader(s, err):
    cur = None
    pos = -1
    
    def peek(p=0):
        if pos + p >= len(s):
            return 'eof'
        else:
            return s[pos + p]
        
    def match(c):
        if c != peek():
            err(f'期望{c}, 实际{peek()}')
            
        return next()
    
    def next():
        nonlocal pos, cur
        
        old = cur
        pos = pos + 1
        if pos >= len(s):
            cur = 'eof'
        else:
            cur = s[pos]
            
        return old
    
    next()
    return peek, match, next

cilly_op1 = [
    '(',')','{','}',',',';',
    '+','-','*','/','%',
]

cilly_op2 = {
    '>': '>=',
    '<': '<=',
    '=': '==',
    '!': '!=',
    '&': '&&',
    '|': '||',
}

cilly_keywords = [
    'var','print','if','else', 'while','break','continue','return','fun',
    'true', 'false', 'null',
]

def cilly_lexer(prog):
    
    def err(msg):
        error('cilly lexer', msg)
        
    peek, match, next = make_str_reader(prog, err)
    
    def program():
        r = []
        
        while True:
            skip_ws()
            if peek() == 'eof':
                break
            
            r.append( token() )
        
        return r
    
    def skip_ws():
        while peek() in [' ', '\t','\r','\n']:
            next()
            
    def token():
        
        c = peek()
        
        if is_digit(c):
            return num()
        
        if c == '"':
            return string()
        
        if c == '_' or is_alpha(c):
            return id()
        
        if c in cilly_op1 :
            next()
            return mk_tk(c)
        
    
        if c in cilly_op2:
            next()
            if peek() == cilly_op2[c][1]:
                next()
                return mk_tk(cilly_op2[c])
            else:
                return mk_tk(c)
        
        err(f'非法字符{c}')
    
    def is_digit(c):
        return c >= '0' and c <= '9'
    
    def num():
        r = ''
        
        while is_digit(peek()):
            r = r + next()
            
        if peek() == '.':
            r = r + next()
            
            while is_digit(peek()):
                r = r + next()
                
        return mk_tk('num', float(r) if '.' in r else int(r))
    
    def string():
        match('"')
        
        r = ''
        while peek() != '"' and peek() != 'eof':
            r = r + next()
            
        match('"')
        
        return mk_tk('str', r)

    def is_alpha(c):
        return (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z')
    
    def is_digit_alpha__(c):
        return c == '_' or is_digit(c) or is_alpha(c)
    
    def id():
        r = '' + next()
        
        while is_digit_alpha__(peek()):
            r = r + next()
            
        if r in cilly_keywords:
            return mk_tk(r)
        
        return mk_tk('id', r)
    
            
    return program()
            
EOF = mk_tk('eof')

def make_token_reader(ts, err):
    pos = -1
    cur = None
    
    def peek(p=0):
        if pos + p >= len(ts):
            return 'eof'
        else:
            return tk_tag(ts[pos + p])
        
    def match(t):
        if peek() != t:
            err(f'期望{t},实际为{cur}')
            
        return next()
    
    def next():
        nonlocal pos, cur
        
        old = cur
        pos = pos + 1
        
        if pos >= len(ts):
            cur = EOF
        else:
            cur = ts[pos]
            
        return old
    next()
    
    return peek, match, next
        
def cilly_parser(tokens):
    def err(msg):
        error('cilly parser',  msg)
        
    peek, match, next = make_token_reader(tokens, err)
    
    def program():
        
        r = []
        
        while peek() != 'eof':
            r.append( statement() )
            
        return ['program', r]
    
    def statement():
        t = peek()
        
        if t == 'var':
            return define_stat()
        
        if t == 'id' and peek(1) == '=':
            return assign_stat()
        
        if t == 'print':
            return print_stat()
        
        if t == 'if':
            return if_stat()
        
        if t == 'while':
            return while_stat()
        
        if t == 'break':
            return break_stat()
        
        if t == 'continue':
            return continue_stat()
        
        if t == 'return':
            return return_stat()
        
        if t == '{':
            return block_stat()
        
        return expr_stat()
    
    def define_stat():
        match('var')
        
        id = tk_val ( match('id') )
        
        match('=')
        
        e = expr()
        
        match(';')
        
        return ['define', id, e]
    
    def assign_stat():
        id = tk_val( match('id') )
        
        match('=')
        
        e = expr()
        
        match(';')
        
        return ['assign', id, e]
    
    def print_stat():
        match('print')
        match('(')
        
        if peek() == ')':
            alist = []
        else:
            alist = args()
            
        match(')')
        match(';')
        
        return ['print', alist]
    
    def args():
        
        r = [expr()]
        
        while peek() == ',':
            match(',')
            r.append( expr() )
            
        return r
    
    def if_stat(): # if ( expr ) statement (else statment)?
        match('if')
        match('(')
        cond = expr()
        match(')')
        
        true_stat = statement()
        
        if peek() == 'else':
            match('else')
            false_stat = statement()
        else:
            false_stat = None
        return ['if', cond , true_stat, false_stat]
    
    def while_stat():
        match('while')
        match('(')
        cond = expr()
        match(')')
        body = statement()
        
        return ['while', cond, body]
    
    def continue_stat():
        match('continue')
        match(';')
        
        return ['continue']
    
    def break_stat():
        match('break')
        match(';')
        return ['break']
    
    def return_stat():
        match('return')
        
        if peek() != ';':
            e = expr()
        else:
            e = None
            
        match(';')
        
        return ['return', e]
    
    def block_stat():
        match('{')
        
        r = []
        
        while peek() != '}':
            r.append( statement() )
            
        match('}')
        return ['block', r]
        
    def expr_stat():
        e = expr()
        match(';')
        
        return ['expr_stat', e]
    
    def literal(bp=0):
        return next()
    
    def unary(bp):
        op = tk_tag( next() )
        e = expr(bp)
        
        return ['unary', op, e]
    
    def fun_expr(bp=0):
        match('fun')
        match( '(' )
        if peek() == ')':
            plist = []
        else:
            plist = params()
            
        match(')')
        body = block_stat()
        
        return ['fun', plist, body]
    
    def params():
        r = [ tk_val( match('id') )]
        
        while peek() == ',':
            match(',')
            r.append ( tk_val( match('id') ) )
            
        return r
    
    def parens(bp=0):
        match('(')
        
        e = expr()
        
        match(')')
        
        return e
    
    op1 = {
        'id': (100, literal),
        'num': (100, literal),
        'str': (100, literal),
        'true': (100, literal),
        'false': (100, literal),
        'null': (100, literal),
        '-': (85, unary),
        '!': (85, unary),
        'fun': (98, fun_expr),
        '(': (100, parens),
        
    }
    
    def get_op1_parser(t):
        if t not in op1:
            err(f'非法token: {t}')
            
        return op1[t]
    def binary(left, bp):
        
        op = tk_tag( next() )
        
        right = expr(bp)
        
        return ['binary', op, left, right]
    
    def call(fun_expr, bp=0):
        match('(')
        if peek() != ')':
            alist = args()
        else:
            alist = []
        match(')')
        return ['call', fun_expr, alist]
    
    op2 = {
        '*': (80, 81, binary),
        '/': (80, 81, binary),
        '%': (80, 81, binary),
        '+': (70, 71, binary),
        '-': (70, 71, binary),
        '>': (60, 61, binary),
        '>=': (60, 61, binary),
        '<': (60, 61, binary),
        '<=': (60, 61, binary),
        '==': (50, 51, binary),
        '!=': (50, 51, binary),
        '&&': (40, 41, binary),
        '||': (30, 31, binary),
        '(': (90, 91, call),
    }
    
    def get_op2_parser(t):
        if t not in op2:
            return (0,0,None)
        else:
            return op2[t]
            
    def expr(bp = 0):
        r_bp, parser = get_op1_parser( peek() )
        left = parser(r_bp)
        
        while True:
            l_bp, r_bp, parser = get_op2_parser( peek() )
            if parser == None or l_bp <= bp:
                break
            
            left = parser(left, r_bp)
        
        return left
    
    return program()



def mk_num(i):
    return ['num', i]

def mk_str(s):
    return ['str', s]

def mk_proc(params, body, env):
    return ['proc', params, body, env]

def mk_primitive_proc(f):
    return ['primitive', f]

TRUE = ['bool', True]
FALSE = ['bool', False]

def mk_bool(b):
    return TRUE if b else FALSE

NULL = ['null', None]

def val(v):
    return v[1]

#环境: ({x:1, y:2},parent_env) 
def lookup_var(env, name):
    while env:
        e, env = env
        
        if name in e:
            return e[name]
        
    error('lookup var', f'变量未定义{name}')
        

def set_var(env, name, val):
    while env:
        e, env = env
        if name in e:
            e[name] = val
            return
    
    error('set var', f'变量未定义{name}')
    
def define_var(env, name, val):
    e, env = env
    
    if name in e:
        error('define var', f'变量已定义{name}')
        
    e[name] = val
    
def extend_env(vars, vals, env):
    e = { var:val for (var, val) in zip(vars, vals) }
    return (e, env)

env = ({}, None)

def cilly_eval(ast, env):
    def err(msg):
        return error('cilly eval', msg)
    
    def ev_program(node, env):
        _, statements = node
    
        r = NULL
        
        for s in statements:
            r = visit(s, env)
            
        return r
    
    def ev_expr_stat(node, env):
        _, e = node
        
        return visit(e, env)
    
    
    def ev_print(node, env):
        _, args = node
        
        for a in args:
            print( val( visit(a, env) ) , end=' ')
            
        print('')
        
        return NULL
        
    def ev_literal(node, env):
        tag, val = node
        
        if tag in ['num','str']:
            return node
        
        if tag in ['true', 'false']:
            return TRUE if tag == 'true' else FALSE
        
        if tag == 'null':
            return NULL
        
        err(f'非法字面量{node}')
        
    def ev_unary(node, env):
        _, op, e = node
        
        v = val( visit(e, env) )
        
        if op == '-':
            return mk_num( -v )
        
        if op == '!':
            return mk_bool( not(v) )
        
        err(f'非法一元运算符{op}')
        
    def ev_binary(node, env):
        _, op, e1, e2 = node
        
        v1 = val( visit(e1, env) )
        
        if op == 'mk_proc&&':
            if v1 == False:
                return FALSE
            else:
                return visit(e2, env)
            
        if op == '||':
            if v1 == True:
                return TRUE
            else:
                return visit(e2, env)
                
        v2 = val( visit(e2,env) )
        
        if op == '+':
            return mk_num( v1 + v2 )
        
        if op == '-':
            return mk_num( v1 - v2 )

        if op == '*':
            return mk_num( v1 * v2 )

        if op == '/':
            return mk_num( v1 / v2 )

        if op == '%':
            return mk_num( v1 % v2 )

        if op == '>':
            return mk_bool( v1 > v2 )
        
        if op == '>=':
            return mk_bool( v1 >= v2 )
        
        if op == '<':
            return mk_bool( v1 < v2 )
        
        if op == '<=':
            return mk_bool( v1 <= v2 )
        
        
        if op == '==':
            return mk_bool( v1 == v2 )
               
        if op == '!=':
            return mk_bool( v1 != v2 )
        
       
        

        err(f'非法二元运算符{op}')
        
    def ev_if(node, env):
        _, cond, true_stat, false_stat = node
        
        if visit(cond, env) == TRUE:
            return visit(true_stat, env)
        
        if false_stat != None:
            return visit(false_stat, env)
        
        return NULL
    
    def ev_while(node, env):
        _, cond, body = node
    
        r = NULL
        prev_r = NULL
        while visit(cond, env) == TRUE:
            r = visit(body, env)
            if r[0] == 'continue':
                continue
            
            if r[0] == 'break':
                r = prev_r
                break
            
            prev_r = r
            
        return r
    
    def ev_break(node, env):
        return ['break']
    
    def ev_continue(node, env):
        return ['continue']
    
    def ev_block(node, env):
        _, statements = node
        
        r = NULL
        
        block_env = extend_env({}, {}, env)
        
        for s in statements:
    
            r = visit(s, block_env)
            if r[0] in ['break', 'continue', 'return']:
                return r
            
        return r
    
    def ev_id(node, env):
        _, name = node
        
        return lookup_var(env, name)
    
    def ev_define(node, env):
        _, name, e = node
        
        v = visit(e, env)
        
        define_var(env, name, v)
        
        return NULL
    
    def ev_assign(node, env):
        _, name, e = node
        
        v = visit(e, env)
        
        set_var(env, name, v)
        
        return NULL
    
    def ev_fun(node, env):
        _, params, body = node
        
        return mk_proc(params, body, env)

    def ev_return(node, env):
        _, e = node
        
        if e != None:
            return visit(e, env)
        else:
            return NULL
        
    def ev_call(node, env):
        _, f_expr, args = node
        
        proc = visit(f_expr, env)
        if proc[0] not in ['proc', 'primitive']:
            err(f'非法函数{proc}')
            
        if proc[0] == 'primitive':
            _, f = proc
            args = [ val( visit(a, env) ) for a in args]
            return f(*args)
        
        _, params, body, saved_env = proc
        
        args = [ visit(a, env) for a in args]
        
        
        f_env = extend_env(params, args, saved_env)
        
        v = visit(body, f_env)
        
        
        if v[0] == 'return':
            r = r[1]
            
        return v
        
    visitors = {
        'program': ev_program,
        'expr_stat': ev_expr_stat,
        'print': ev_print,
        'if': ev_if,
        'while': ev_while,
        'break': ev_break,
        'continue': ev_continue,
        
        'define': ev_define,
        'assign': ev_assign,

        'block': ev_block,
        
        'unary': ev_unary,
        'binary': ev_binary,
        
        'id': ev_id,
        
        'fun': ev_fun,
        'return': ev_return,
        'call': ev_call,
        
        'num': ev_literal,
        'str': ev_literal,
        'true': ev_literal,
        'false': ev_literal,
        'null': ev_literal,
    }
    
    def visit(node, env):
        t = node[0]
        if t not in visitors:
            err(f'非法节点{node}')
            
        return visitors[t](node, env)
    
    return visit(ast, env)
        
p1 = '''

var sum = 0;
var i = 1;

while(i <= 100){
    if(i % 2 == 0)
        sum = sum + i;
    i = i + 1;
}

print("1..100的偶数和=",sum);

var f0 = 0;
var f1 = 1;

i = 1;

var t = 0;

while(i <= 10){
    t = f1;
    f1 = f0 + f1;
    f0 = t;
    
    i = i + 1;
}

print("fib(10)=", f0);

var add = fun(a,b){
    return a + b;
};

print(add(1,2), add(1 * 2 + 3, 4 * 6));

    

'''

p1 = '''

var K = fun(a) {
    return fun(b) {return a;};
};

var KI = fun(a) {
    return fun(b) {return b;};
};

var pair = fun(a,b) {
    return fun(f) {
        return f(a)(b);
    };
};

var first = fun(p) {
    return p(K);
};

var second = fun(p) {
    return p(KI);
};

var p = pair(1,2);
print(first(p), second(p));

var x = 1;
{
    var y = 100;
    var x = 2;
    {
        var x = 3;
        print("inner x", x, "middle y", y);
    }
    print("middle x", x);
}

print("outer x", x);

cilly_greet("小米");

'''

def greet(name):
    print("Hello " + name)
    return NULL

env = (
    {
        'cilly_greet': mk_primitive_proc(greet),    
    },
    None
)
tokens = cilly_lexer(p1)
ast = cilly_parser(tokens)
v = cilly_eval(ast, env)

            
    
 

        
        