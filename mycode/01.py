a = int(input("set a num\n"))

a += 1

print(a)


def calculate(x, y):
    return x + y


def subtraction(x, y):
    return x - y


# res = a + 20
result = calculate(a, 20)

# ans = res - a = a + 20 - a = 20
ans = subtraction(result, a)

print(ans)
