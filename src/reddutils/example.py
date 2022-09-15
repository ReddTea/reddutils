def func(foo, bar):
    return foo * bar

def add_one(number):
    return number + 1

def fib2(n):    # write Fibonacci series up to n
    a, b = 0, 1
    while a < n:
        print(a, end=' ')
        a, b = b, a+b
    print()
