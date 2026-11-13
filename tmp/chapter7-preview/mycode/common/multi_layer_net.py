from collections import OrderedDict

import numpy as np

from common.layers import Affine, Relu, SoftmaxWithLoss


class MultiLayerNet:
    def __init__(self, input_size, hidden_size_list, output_size):
        self.input_size = input_size
        self.hidden_size_list = hidden_size_list
        self.output_size = output_size
        self.hidden_layer_num = len(hidden_size_list)

        self.params = {}

        # 吧输入层、隐藏层、输出层节点连起来
        all_size_list = [input_size] + hidden_size_list + [output_size]

        for i in range(1, len(all_size_list)):
            input_num = all_size_list[i - 1]
            output_num = all_size_list[i]

            # He初始化
            scale = np.sqrt(2.0 / input_num)

            self.params["W" + str(i)] = scale * np.random.randn(input_num, output_num)
            self.params["b" + str(i)] = np.zeros(output_num)

        # 组装隐藏层
        self.layers = OrderedDict()

        for i in range(1, self.hidden_layer_num + 1):
            self.layers["Affine" + str(i)] = Affine(
                self.params["W" + str(i)], self.params["b" + str(i)]
            )
            self.layers["Relu" + str(i)] = Relu()

        # 添加输出层
        i = self.hidden_layer_num + 1
        self.layers["Affine" + str(i)] = Affine(
            self.params["W" + str(i)], self.params["b" + str(i)]
        )

        self.last_layer = SoftmaxWithLoss()

    def predict(self, x):
        for layer in self.layers.values():
            x = layer.forward(x)

        return x

    def loss(self, x,t):
        y = self.predict(x)
        return self.last_layer.forward(y,t)

    def accuracy(self, x,t):
        y = self.predict(x)
        y = np.argmax(y,axis=1)
        t = np.argmax(t, axis=1)

        return np.mean(y == t)

    def gradient(self, x,t):
        # 前向传播
        self.loss(x,t)

        # 从损失层开始反向传播
        dout = self.last_layer.backward(1)

        layers = list(self.layers.values())
        layers.reverse()

        for layer in layers:
            dout = layer.backward(dout)

        # 手机每个Affine层的参数梯度
        grads = {}

        for i in range(1,self.hidden_layer_num +2):
            grads["W" + str(i)] = self.layers["Affine" + str(i)].dW
            grads["b" + str(i)] = self.layers["Affine" + str(i)].db

        return grads