# 列表
a = [1, 2, 3, 4, 5]
print(a)

len(a)
a[4]
a[4] = 100
print(a)

a[0:2]  # 1,2
a[1:]  # 2,3,4,100
a[:3]  # 1,2,3
a[:-1]  # 1,2,3,4
a[:-2]  # 1,2,3

# 字典
me = {"height": 180}
me["height"]
me["weight"] = 70
print(me)

# if 语句
hungry = True
if hungry:
    print("I am hungry")
else:
    print("I am not hungry")

hungry = False

# for 循环
for i in range(3):
    print(i)


# 函数
def hello(object):
    print("hello world " + object)


hello("cat")
