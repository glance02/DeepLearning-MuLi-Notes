# 斋藤《深度学习入门》学习资源

## Knowledge

- [斋藤康毅《深度学习入门：基于Python的理论与实现》](<materials/深度学习入门：基于Python的理论与实现 (斋藤康毅).pdf>)：首要教材；前四章为书内1—119页，对应PDF第26—144页。概念、公式与算法说明优先回到对应小节核对。
- [自己的复现代码](mycode/)：对照实际函数名、输入输出形状、数据预处理与调用关系。它是实践材料，代码存在不等于理解已经核验。
- [第1—5章Markdown笔记](notes/斋藤-深度学习入门/00-学习导航.md)：教材与代码的衍生整理，保存已讨论的易混点；用于复习定位。
- [学习记录](learning-records/)：根据用户独立回答记录理解证据，用于调整复习难度，不作为算法知识的一手来源。
- [HTML手边册](reference/index.html)：按概念和函数名快速回查，内含教材页码与可选短练习入口。

### 网站部署实战（配套学习网站）

- [网站部署实战总入口](reference/site-deployment.html)：根据本项目 2026-10-30 的实际工作整理；用于从整体链路定位代码和维护命令。
- [本项目操作说明](deploy/README.md)与[实现代码](scripts/)：核对发布内容、构建过程、软链接切换与定时任务的真实行为。部署记录不是掌握证据。
- [Git 官方 git pull](https://git-scm.com/docs/git-pull)：核对拉取与 `--ff-only`；首次只读 DESCRIPTION 和该选项。
- [Nginx 官方入门指南](https://nginx.org/en/docs/beginners_guide.html)：理解静态文件、根目录、请求路径和 reload。
- [systemd 官方 timer](https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html)：核对 timer 触发 service、`OnCalendar` 和错过日程后的补跑。
- [Python 官方 venv](https://docs.python.org/3/library/venv.html)：理解项目依赖环境和可重建性。
- [Python 官方 os.replace](https://docs.python.org/3/library/os.html#os.replace)：核对同一文件系统上的原子替换，理解本项目入口切换。
- [Python 官方 mkdtemp](https://docs.python.org/3/library/tempfile.html#tempfile.mkdtemp)与[Linux 路径查找手册](https://man7.org/linux/man-pages/man7/path_resolution.7.html)：解释本次发布目录 0700 导致 Nginx 无法读取的故障。
- [Python-Markdown 扩展](https://python-markdown.github.io/extensions/)与[Arithmatex](https://facelessuser.github.io/pymdown-extensions/extensions/arithmatex/)：核对笔记转网页和公式处理。

### 第5章当前问题：乘法层反向传播

- [教材配套 MulLayer 源码](https://github.com/oreilly-japan/deep-learning-from-scratch/blob/master/ch05/layer_naive.py)：已核对 `forward` 保存输入、`backward` 交叉相乘并返回两份导数；对应自己的 `mycode/chapter5.ipynb`。
- [教材配套苹果价格示例](https://github.com/oreilly-japan/deep-learning-from-scratch/blob/master/ch05/buy_apple.py)：查看多个乘法层前向计算和反向传递的调用顺序。
- [乘法层速查](reference/mul-layer-backward.html)与[短课](lessons/0007-mul-layer-backward.html)：本次问题的配套材料。

### 第5章当前问题：Affine 反向传播

- [教材配套 Affine 类](https://github.com/oreilly-japan/deep-learning-from-scratch/blob/master/common/layers.py#L38-L64)：核对 `dx=dout@W.T`、`dW=x.T@dout` 与偏置梯度沿样本轴求和。
- [Stanford CS231n 反向传播讲义](https://cs231n.github.io/optimization-2/)：链式法则、分支导数相加与矩阵运算的向量化梯度；注意其示例矩阵方向可能与教材不同，本地推导统一使用 `Y=XW+b`。
- [Affine 逐元素推导短课](lessons/0008-affine-backward.html)与[公式速查](reference/affine-backward.html)：从单样本的两输入、三输出展开，推导输入、权重和偏置梯度，再推广到批量。

### 第5章全章整理（2026-10-31）

- [本地教材第5章](<materials/深度学习入门：基于Python的理论与实现 (斋藤康毅).pdf#page=146>)：已核对书内121—161页（PDF146—186页）的小节范围和关键实现；优先按教材复习。
- [第5章完整笔记](notes/斋藤-深度学习入门/05-误差反向传播法.md)、[HTML手册](reference/chapter5.html)与[反向流程短练习](lessons/0009-backprop-review.html)：覆盖计算图、链式法则、各层、组装、梯度确认和本次实验，连接已有0007、0008短课。
- [教材 TwoLayerNet](https://github.com/oreilly-japan/deep-learning-from-scratch/blob/master/ch05/two_layer_net.py)、[梯度确认](https://github.com/oreilly-japan/deep-learning-from-scratch/blob/master/ch05/gradient_check.py)与[训练循环](https://github.com/oreilly-japan/deep-learning-from-scratch/blob/master/ch05/train_neuralnet.py)：核对教材的层顺序、梯度收集及参数更新。

## Wisdom (Communities)

当前需求是本地教材复习与代码辅导，暂不扩展社区资源。
