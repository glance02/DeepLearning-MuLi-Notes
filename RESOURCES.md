# 斋藤《深度学习入门》学习资源

## Knowledge

- [斋藤康毅《深度学习入门：基于Python的理论与实现》](<materials/深度学习入门：基于Python的理论与实现 (斋藤康毅).pdf>)：首要教材；前四章为书内1—119页，对应PDF第26—144页。概念、公式与算法说明优先回到对应小节核对。
- [自己的复现代码](mycode/)：对照实际函数名、输入输出形状、数据预处理与调用关系。它是实践材料，代码存在不等于理解已经核验。
- [已读章节Markdown笔记](notes/斋藤-深度学习入门/00-学习导航.md)：教材与代码的衍生整理，保存已讨论的易混点；用于复习定位。
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

### 第6章当前问题：Adam 的公式与实现

- [Adam 原论文](https://arxiv.org/pdf/1412.6980)：已核对 Algorithm 1（PDF第2页）及第2、3节，包含梯度及梯度平方的指数移动平均、零初始化的偏差校正和参数更新。用户要求根据公式手敲最小实现，不下载整套作者源码；暂不要求论文推导。
- [Adam 一次更新短课](lessons/0010-adam-update.html)与[公式、完整代码速查](reference/adam.html)：显式计算 m_hat、v_hat，对照公式解释变量与初始化层级，并提供单参数例子和即时反馈短题。

### 第6章后半章：阅读与动手范围

- [本地教材6.2起](<materials/深度学习入门：基于Python的理论与实现 (斋藤康毅).pdf#page=201>)：已核对权重初始化、BatchNorm、正则化及超参数验证的小节；Dropout完整类位于PDF218页。用户当前选择先会用Adam，后半章阅读为主，手写关键小实现，完整实验不要求逐行复现。
- 第6.2.2节：[激活值分布逐行注释](reference/activation-distribution.html)与[层间连接短练习](lessons/0011-activation-distribution.html)，对照当前notebook说明数组形状、字典保存、展平和直方图；原代码位于教材PDF202—203页。
- 第6.2.3节：已核对本地教材PDF206—208页（书内181—183页）图6-14、三种ReLU初始化及均值脚注；解释补入[ReLU读图速查](reference/activation-distribution.html#relu-reading)，区分正常归零、正值分布收缩与He的尺度补偿。
- API一手说明：[randn正态采样](https://numpy.org/doc/stable/reference/random/generated/numpy.random.randn.html)、[dot矩阵乘法](https://numpy.org/doc/stable/reference/generated/numpy.dot.html)、[flatten一维副本](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.flatten.html)、[subplot布局](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplot.html)、[hist直方图](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.hist.html)。

### 第6.3节：BatchNorm与旧训练结果的比较

- [教材配套BatchNorm实验配置](https://github.com/oreilly-japan/deep-learning-from-scratch/blob/master/ch06/batch_norm_test.py)：仅在线只读核对，未下载或导入项目。用于核对5个隐藏层、1000个训练样本、SGD学习率0.01及16种权重初始尺度，区分无BN对照组与用户第5章浅网络实验；教材图6-18、6-19位于本地PDF212—213页。

### 第6.4节：过拟合实验依赖的多层网络

- [作者MultiLayerNet定义](https://github.com/oreilly-japan/deep-learning-from-scratch/blob/master/common/multi_layer_net.py)：在线只读核对hidden_size_list驱动的参数和层生成、初始化选择、权值衰减与前后向；用户已自己手敲固定ReLU、He和one-hot接口的最小版。可核对封装思路，不要求补完作者所有功能，也不下载整套源码。

### 2026-11-03阶段整理：第六章尚未完成

- [第六章阶段笔记](notes/斋藤-深度学习入门/06-与学习相关的技巧.md)与[HTML入口](reference/chapter6.html)：整理至6.4.1，下一小节权值衰减待学。
- [MultiLayerNet完整梳理](reference/multi-layer-net.html)：按用户当前源码解释层宽、共享参数、方法调用和优化器更新；复用assets/network-lab.js的维度追踪，不运行浏览器训练。
- 短课[12：参数与层](lessons/0012-multilayernet-parameters.html)、[13：一次更新](lessons/0013-multilayernet-training.html)：两个单独的小目标，每次按需选一项。
- [本次过拟合图](assets/chapter6-overfitting.png)与[当前ReLU/Xavier图](assets/chapter6-activation.png)：直接从Notebook保存输出提取，不重新训练，不把图像读数当作精确最终指标。

## Wisdom (Communities)

当前需求是本地教材复习与代码辅导，暂不扩展社区资源。
