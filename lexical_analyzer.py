'''
cilly 词法
program : token* 'eof'

token
    : id | num | string
    | 'true' | 'false' | 'null'
    | 'var' | 'if' | 'else' | 'while' | 'for' | 'continue' | 'break' | 'return' | 'fun'
    | '(' | ')' | '{' | '}' | ','
    | '=' | '=='
    | '+' | '-' | '*' | '/' | '^'
    | '!' | '!='
    | '>' | '>='
    | '<' | '<='
    | '&&' | '||'
    | '?' | ':'
    ;
    
num : [0-9]+ ('.' [0-9]*)? 
string : '"' char* '"'
char : 不是双引号的字符
ws : (' ' | '\r' | '\n' | '\t)+
comment : '#' 非换行符号* '\r'? '\n'
'''


def error(src, msg, token=None):
    if token:
        line = tk_line(token)
        column = tk_column(token)
        raise Exception(f'{src} : 第{line}行第{column}列 : {msg}')
    else:
        raise Exception(f'{src} : {msg}')


def mk_tk(tag, val=None, line=None, column=None):
    return [tag, val, line, column]


def tk_tag(t):
    return t[0]


def tk_val(t):
    return t[1]


def tk_line(t):
    return t[2]


def tk_column(t):
    return t[3]


def make_str_reader(s, err):
    cur = None
    pos = -1
    line = 1
    line_start = 0

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
        nonlocal pos, cur, line, line_start

        old = cur
        pos = pos + 1

        if pos >= len(s):
            cur = 'eof'
        else:
            cur = s[pos]
            if cur == '\n':
                line = line + 1
                line_start = pos + 1

        return old

    def get_line():
        return line

    def get_column():
        return pos - line_start + 1

    next()
    return peek, match, next, get_line, get_column


cilly_op1 = [
    '(', ')', '{', '}', ',', ';',
    '+', '-', '*', '/', '^',
    '?', ':'
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
    'var', 'print', 'if', 'else', 'while', 'for', 'break', 'continue', 'return', 'fun',
]


def cilly_lexer(prog):
    def err(msg):
        # 获取当前的行号和列号
        line = get_line()
        column = get_column()
        error('cilly lexer', f'第{line}行第{column}列 : {msg}')

    peek, match, next, get_line, get_column = make_str_reader(prog, err)

    def program():
        r = []

        while True:
            skip_ws_and_comments()
            if peek() == 'eof':
                break

            r.append(token())

        return r

    def skip_ws_and_comments():
        while True:
            while peek() in [' ', '\t', '\r', '\n']:
                next()

            if peek() == '#':
                skip_comment()
            else:
                break

    def skip_comment():
        match('#')

        while peek() != '\n' and peek() != '\r' and peek() != 'eof':
            next()

        if peek() == '\r' and peek(1) == '\n':
            next()
            next()
        elif peek() == '\n' or peek() == '\r':
            next()

    def token():
        line = get_line()
        column = get_column()

        c = peek()

        if is_digit(c):
            return num()

        if c == '"':
            return string()

        if c == '_' or is_alpha(c):
            return id()

        if c in cilly_op1:
            next()
            return mk_tk(c, None, line, column)

        if c in cilly_op2:
            next()
            if peek() == cilly_op2[c][1]:
                next()
                return mk_tk(cilly_op2[c], None, line, column)
            else:
                return mk_tk(c, None, line, column)

        err(f'非法字符{c}')

    def is_digit(c):
        return c >= '0' and c <= '9'

    def num():
        line = get_line()
        column = get_column()
        r = ''

        while is_digit(peek()):
            r = r + next()

        if peek() == '.':
            r = r + next()

            while is_digit(peek()):
                r = r + next()

        return mk_tk('num', float(r) if '.' in r else int(r), line, column)

    def string():
        line = get_line()
        column = get_column()
        match('"')

        r = ''
        while peek() != '"' and peek() != 'eof':
            r = r + next()

        match('"')

        return mk_tk('str', r, line, column)

    def is_alpha(c):
        return (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z')

    def is_digit_alpha__(c):
        return c == '_' or is_digit(c) or is_alpha(c)

    def id():
        line = get_line()
        column = get_column()
        r = '' + next()

        while is_digit_alpha__(peek()):
            r = r + next()

        if r in cilly_keywords:
            return mk_tk(r, None, line, column)

        return mk_tk('id', r, line, column)

    return program()


if __name__ == "__main__":
    from syntactic_analyzer import cilly_parser

    p1 = '''
    # true;
    #     # 
    #     # # 这是一个测试程序
    #     # 1 + 2 ^ 3; # 计算1+2^3
    #     # 
    #     # # 三元表达式测试
    #     # x > 0 ? x : -x;
    #     # 
    #     # # for循环测试
    #     # for (var i = 0; i < 10; i = i + 1;) { 
    #     #     print(i); # 打印i的值
    #     # }
    #     # # 
    #     # # # while循环测试
    #     # # while (i < 10;) { 
    #     # #     i = i + 1; # 增加i的值
    #     # # }
    #     # 
    #     # # 函数定义测试
    #     # fun test(a, b) { 
    #     #     return a + b; # 返回a+b
    #     # }
    #     # #
    fun fern(len) {
        if(len > 5){
            forward(len);
            right(10);
            fern( len - 10);
            left( 40);
            fern( len - 10);
            right(30);
            backward(len);
        }
    }
    
    pencolor("green");
    left(90);
    penup();
    backward(200);
    pendown();
    fern(100);
    '''

    tokens = cilly_lexer(p1)
    print("tokens:", tokens)

    ast = cilly_parser(tokens)
    print("ast:", ast)
