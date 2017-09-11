def identity(x):
    return x

@magic_trampoline
def factorial(n, m=1):
    if n < 2:
        return identity(m)
    else:
        return factorial(n-1, m*n)
