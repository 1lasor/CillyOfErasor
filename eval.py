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
    if var not in env.variables:
        error('lookup var', f'未定义变量{var}')
    return env.variables[var]


def set_var(env, var, val):
    if var not in env.variables:
        error('set var', f'未定义变量{var}')
    env.variables[var] = val


def define_var(env, var, val):
    if var in env.variables:
        error('define var', f'变量已定义{var}')
    env.variables[var] = val

def extend_env(vars, vals, env):
    e = { var:val for (var, val) in zip(vars, vals) }
    return (e, env)

# 全局环境变量
global_env = {}


def reset_environment():
    """重置全局环境"""
    global global_env
    global_env = Environment()


def cilly_eval(ast, env=None):
    if env is None:
        env = Environment()  # 创建根环境
    
    # 执行单个语句
    result = None
    for node in ast[1]:
        result = evaluate_node(node, env)
    
    return result, env


def evaluate_node(node, env):
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
            print(val(visit(a, env)), end=' ')
        print('')
        return NULL

    def ev_literal(node,env):
        tag, v, _, _ = node

        if tag in ['num', 'str']:
            return node

        if tag in ['true', 'false']:
            return TRUE if tag == 'true' else FALSE

        if tag == 'null':
            return NULL

        err(f'非法字面量{node}')

    def ev_unary(node,env):
        _, op, e = node

        v = val(visit(e, env))

        if op == '-':
            return mk_num(-v)

        if op == '!':
            return FALSE if v else TRUE

        err(f'非法一元运算符{op}')

    def ev_binary(node,env):
        _, op, e1, e2 = node

        v1 = val(visit(e1, env))
        if op == '&&':
            if v1 == False:
                return FALSE
            else:
                return visit(e2, env)

        if op == '||':
            if v1 == True:
                return TRUE
            else:
                return visit(e2, env)

        v2 = val(visit(e2, env))

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

    def ev_ternary(node,env):
        _, cond, true_expr, false_expr = node

        if visit(cond, env) == TRUE:
            return visit(true_expr, env)
        else:
            return visit(false_expr, env)

    def ev_if(node,env):
        _, cond, true_s, false_s = node

        if visit(cond, env) == TRUE:
            return visit(true_s, env)

        if false_s != None:
            return visit(false_s, env)

        return NULL

    def ev_while(node,env):
        _, cond, body = node

        r = NULL
        prev_r = NULL
        while visit(cond, env) == TRUE:
            r = visit(body, env)
            if r[0] == 'break':
                r = prev_r
                break

            if r[0] == 'continue':
                continue
            prev_r = r

        return r

    def ev_for(node,env):
        _, init, cond, incr, body = node

        r = NULL
        prev_r = NULL

        visit(init, env)  # 执行初始化语句

        while True:
            cond_val = visit(cond, env)
            if cond_val[0] == 'expr_stat':
                cond_val = cond_val[1]

            if cond_val != TRUE:
                break

            r = visit(body, env)
            if r[0] == 'break':
                r = prev_r
                break

            if r[0] == 'continue':
                visit(incr, env)
                continue

            prev_r = r
            visit(incr, env)  # 执行增量语句

        return r

    def ev_break(node,env):
        return ['break']

    def ev_continue(node,env):
        return ['continue']

    def ev_block(node,env):
        _, statements = node

        r = NULL

        for s in statements:
            r = visit(s, env)
            if r[0] in ['break', 'continue']:
                return r

        return r

    def ev_id(node, env):
        _, name, _, _ = node
        return env.lookup_var(name)

    def ev_define(node, env):
        _, name, e = node
        v = visit(e, env)
        env.define_var(name, v)
        return NULL

    def ev_assign(node, env):
        _, name, e = node
        v = visit(e, env)
        env.set_var(name, v)
        return NULL

    def ev_return(node,env):
        _, e = node

        if e != None:
            return visit(e, env)
        else:
            return NULL

    def ev_fun(node,env):
        _, params, body = node
        return mk_proc(params, body)

    def ev_fun_def(node,env):
        _, name, params, body = node
        proc = mk_proc(params, body)
        define_var(env, name, proc)
        return NULL

    def ev_call(node, env):
        _, f_expr, args = node

        p = visit(f_expr, env)
        if p[0] not in ['proc', 'primitive']:
            err(f'非法函数{p}')

        if p[0] == 'primitive':
            _, f = p
            args = [ val( visit(a, env) ) for a in args]
            return f(*args)
        
        _, params, body = p
        args = [visit(a, env) for a in args]
        
        # 创建新的环境，继承当前环境
        new_env = Environment(env)
        for param, arg in zip(params, args):
            new_env.define_var(param, arg)
        
        return visit(body, new_env)
    # def ev_call(node, env):
    #     _, f_expr, args = node
        
    #     proc = visit(f_expr, env)
    #     if proc[0] not in ['proc', 'primitive']:
    #         err(f'非法函数{proc}')
            
    #     if proc[0] == 'primitive':
    #         _, f = proc
    #         args = [ val( visit(a, env) ) for a in args]
    #         return f(*args)
        
    #     _, params, body = proc
        
    #     args = [ visit(a, env) for a in args]
        
        
    #     f_env = extend_env(params, args, env)
        
    #     v = visit(body, f_env)
        
        
    #     if v[0] == 'return':
    #         v = v[1]
            
    #     return v

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

    def visit(node, env):
        tag = node[0]
        if tag not in visitors:
            err(f'非法节点{node}')
        return visitors[tag](node, env)

    return visit(node, env)

def greet(name):
    print("Hello " + name)
    return NULL

class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.variables = {}
        self.import_external_functions()
    
    def lookup_var(self, name):
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.lookup_var(name)
        error('lookup var', f'未定义变量{name}')
    
    def define_var(self, name, value):
        if name in self.variables:
            error('define var', f'变量已定义{name}')
        self.variables[name] = value
    
    def set_var(self, name, value):
        if name in self.variables:
            self.variables[name] = value
        elif self.parent:
            self.parent.set_var(name, value)
        else:
            error('set var', f'未定义变量{name}')
    
    def mk_primitive_proc(self, f):
        return ['primitive', f]

    def import_external_functions(self):
        # 引入外部函数
        self.define_var('greet', self.mk_primitive_proc(greet))
        # 可以在这里添加更多的外部函数


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
        #测试外部函数
        '''
        greet("me");
        '''
    ]

    for i, test in enumerate(test_cases):
        print(f"\n测试 {i + 1}:")
        tokens = cilly_lexer(test)
        print("tokens:", tokens)

        ast = cilly_parser(tokens)
        print("ast:", ast)

        print("执行结果:")
        reset_environment()  # 重置环境
        v = cilly_eval(ast)
