"""使用中心差分计算数值梯度。"""

import numpy as np


def numerical_gradient(f, x):
    """对浮点数组 x 求梯度，支持向量、矩阵及更高维数组。

    f(x) 应返回一个标量。计算时临时修改 x 的各个元素，随后恢复，
    因此也支持书中通过闭包读取网络权重的写法。
    """
    if not np.issubdtype(x.dtype, np.floating):
        raise TypeError("x 必须是浮点数组，例如 np.array([3.0, 4.0])")

    h = 1e-4
    grad = np.zeros_like(x)
    for idx in np.ndindex(x.shape):
        original = x[idx]
        try:
            x[idx] = original + h
            fxh1 = f(x)
            x[idx] = original - h
            fxh2 = f(x)
            grad[idx] = (fxh1 - fxh2) / (2 * h)
        finally:
            x[idx] = original

    return grad
