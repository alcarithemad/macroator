def trampoline_decorator(wrapped_func):
    import functools

    def call_from_trampoline(call):
        while isinstance(call, dict) and 'func' in call:
            func = call['func']
            if hasattr(func, 'wrapped'):
                func = func.wrapped
            args = list(call['args'])
            kwargs = dict(call['keywords'])
            if call['*args']:
                args.extend(call['*args'])
            if call['**kwargs']:
                kwargs.update(dict(call['**kwargs']))
            call = func(*args, **kwargs)
        return call
    @functools.wraps(wrapped_func)
    def f(*a, **kw):
        return call_from_trampoline(wrapped_func(*a, **kw))

    f.wrapped = wrapped_func
    return f
