import torch

x = torch.arange(12)

# 改变一个数组的形状
X = x.reshape(3, 4)
X

# 创建全0或者全1的数组
torch.zeros((2, 3, 4))
torch.ones((2, 3, 4))

# 通过列表来创建数组
torch.tensor([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

# 基本的数学运算
x = torch.tensor([1.0, 2, 3, 4])
y = torch.tensor([2.0, 2, 2, 2])
x + y, x - y, x * y, x / y, torch.exp(x)

# 把多个张量连接在一起
X = torch.arange(12, dtype=torch.float32).reshape((3, 4))
Y = torch.tensor([[2, 1, 4, 3], [1, 2, 3, 4], [4, 3, 2, 1]])
torch.cat((X, Y), dim=0), torch.cat((X, Y), dim=1)

# 按元素判断
X == Y

# 求和
X.sum(), X

# 广播机制
a = torch.arange(3).reshape((3, 1))
b = torch.arange(2).reshape((1, 2))
a + b

# 元素的访问和读写
X, X[-1], X[1:3]
X[1, 2] = 9
X

# 为多个元素赋相同的值
X[0:2, :] = 12
X

# 转换为numpy张量
A = X.numpy()
B = torch.Tensor(A)
type(A), type(B)
