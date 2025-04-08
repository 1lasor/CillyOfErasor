from lexical_analyzer import cilly_lexer, error
from syntactic_analyzer import cilly_parser


def mk_num(i):
    return ['num', i]


def mk_str(s):
    return ['str', s]


TRUE = ['bool', True]
FALSE = ['bool', False]


def mk_bool(b):
    return TRUE if b else FALSE


def mk_proc(params, body):
    return ['proc', params, body]


NULL = ['null', None]


def val(v):
    return v[1]


def lookup_var(env, var):
    if var not in env:
        error('lookup var', f'未定义变量{var}')

    return env[var]


def set_var(env, var, val):
    if var not in env:
        error('set var', f'未定义变量{var}')

    env[var] = val


def define_var(env, var, val):
    if var in env:
        error('define var', f'变量已定义{var}')

    env[var] = val


env = {}


def cilly_eval(ast):
    def err(msg):
        return error('cilly eval', msg)

    def ev_program(node):
        _, statements = node

        r = NULL

        for s in statements:
            r = visit(s)

        return r

    def ev_expr_stat(node):
        _, e = node
        return visit(e)

    def ev_print(node):
        _, args = node

        for a in args:
            print(val(visit(a)), end=' ')

        print('')

        return NULL

    def ev_literal(node):
        tag, v, _, _ = node

        if tag in ['num', 'str']:
            return node

        if tag in ['true', 'false']:
            return TRUE if tag == 'true' else FALSE

        if tag == 'null':
            return NULL

        err(f'非法字面量{node}')

    def ev_unary(node):
        _, op, e = node

        v = val(visit(e))

        if op == '-':
            return mk_num(-v)

        if op == '!':
            return FALSE if v else TRUE

        err(f'非法一元运算符{op}')

    def ev_binary(node):
        _, op, e1, e2 = node

        v1 = val(visit(e1))
        if op == '&&':
            if v1 == False:
                return FALSE
            else:
                return visit(e2)

        if op == '||':
            if v1 == True:
                return TRUE
            else:
                return visit(e2)

        v2 = val(visit(e2))

        if op == '+':
            return mk_num(v1 + v2)

        if op == '-':
            return mk_num(v1 - v2)

        if op == '*':
            return mk_num(v1 * v2)

        if op == '/':
            return mk_num(v1 / v2)

        if op == '^':
            return mk_num(v1 ** v2)

        if op == '>':
            return mk_bool(v1 > v2)
        if op == '>=':
            return mk_bool(v1 >= v2)
        if op == '<':
            return mk_bool(v1 < v2)
        if op == '<=':
            return mk_bool(v1 <= v2)
        if op == '==':
            return mk_bool(v1 == v2)
        if op == '!=':
            return mk_bool(v1 != v2)

        err(f'非法二元运算符{op}')

    def ev_ternary(node):
        _, cond, true_expr, false_expr = node

        if visit(cond) == TRUE:
            return visit(true_expr)
        else:
            return visit(false_expr)

    def ev_if(node):
        _, cond, true_s, false_s = node

        if visit(cond) == TRUE:
            return visit(true_s)

        if false_s != None:
            return visit(false_s)

        return NULL

    def ev_while(node):
        _, cond, body = node

        r = NULL
        prev_r = NULL
        while visit(cond) == TRUE:
            r = visit(body)
            if r[0] == 'break':
                r = prev_r
                break

            if r[0] == 'continue':
                continue
            prev_r = r

        return r

    def ev_for(node):
        _, init, cond, incr, body = node

        r = NULL
        prev_r = NULL

        visit(init)  # 执行初始化语句

        while True:
            cond_val = visit(cond)
            if cond_val[0] == 'expr_stat':
                cond_val = cond_val[1]

            if cond_val != TRUE:
                break

            r = visit(body)
            if r[0] == 'break':
                r = prev_r
                break

            if r[0] == 'continue':
                visit(incr)
                continue

            prev_r = r
            visit(incr)  # 执行增量语句

        return r

    def ev_break(node):
        return ['break']

    def ev_continue(node):
        return ['continue']

    def ev_block(node):
        _, statements = node

        r = NULL

        for s in statements:
            r = visit(s)
            if r[0] in ['break', 'continue']:
                return r

        return r

    def ev_id(node):
        _, name, _, _ = node

        return lookup_var(env, name)

    def ev_define(node):
        _, name, e = node
        v = visit(e)

        define_var(env, name, v)
        return NULL

    def ev_assign(node):
        _, name, e = node
        v = visit(e)

        set_var(env, name, v)
        return NULL

    def ev_return(node):
        _, e = node

        if e != None:
            return visit(e)
        else:
            return NULL

    def ev_fun(node):
        _, params, body = node
        return mk_proc(params, body)

    def ev_fun_def(node):
        _, name, params, body = node
        proc = mk_proc(params, body)
        define_var(env, name, proc)
        return NULL

    def ev_call(node):
        _, f_expr, args = node

        p = visit(f_expr)
        if p[0] != 'proc':
            err(f'非法函数{p}')

        _, params, body = p

        args = [visit(a) for a in args]

        global env
        old = env

        env = {p: a for (p, a) in zip(params, args)}

        v = visit(body)

        env = old

        return v

    visitors = {
        'program': ev_program,
        'expr_stat': ev_expr_stat,
        'print': ev_print,
        'if': ev_if,
        'while': ev_while,
        'for': ev_for,
        'break': ev_break,
        'continue': ev_continue,
        'block': ev_block,

        'define': ev_define,
        'assign': ev_assign,

        'unary': ev_unary,
        'binary': ev_binary,
        'ternary': ev_ternary,

        'return': ev_return,
        'fun': ev_fun,
        'fun_def': ev_fun_def,
        'call': ev_call,

        'id': ev_id,
        'num': ev_literal,
        'str': ev_literal,
        'true': ev_literal,
        'false': ev_literal,
        'null': ev_literal,
    }

    def visit(node):
        tag = node[0]
        if tag not in visitors:
            err(f'非法节点{node}')

        return visitors[tag](node)

    return visit(ast)


if __name__ == "__main__":
    test_cases = [
        # 测试基本语法和运算
        '''
        var sum = 0;
        var i = 1;
        
        while(i <= 100){
            sum = sum + i;
            i = i + 1;
        }
        
        print("1+2+...100=",sum);
        ''',

        # 测试幂运算
        '''
        var x = 2 ^ 3 ^ 2;
        print("2^3^2=", x);
        ''',

        # 测试三元表达式
        '''
        var x = -5;
        var y = x > 0 ? x : -x;
        print("绝对值:", y);
        ''',

        # 测试for循环
        '''
        for (var i = 0; i < 10; i = i + 1;) {
            print("循环计数:", i);
        }
        ''',

        # 测试函数
        '''
        var add = fun(a,b){
            return a + b;
        };
        
        print("函数测试:", add(1,2), add(3*4, 6));
        '''
    ]

    for i, test in enumerate(test_cases):
        print(f"\n测试 {i + 1}:")
        tokens = cilly_lexer(test)
        print("tokens:", tokens)

        ast = cilly_parser(tokens)
        print("ast:", ast)

        print("执行结果:")
        env = {}  # 重置环境
        v = cilly_eval(ast)
