(() => {
  'use strict';
  const presets = {
    small: { sizes: [4, 3, 5, 2], batch: 6 },
    mnist: { sizes: [784, 100, 100, 100, 100, 100, 100, 10], batch: 100 }
  };
  const shape = (n, d) => `(${n}, ${d})`;
  const methods = {
    init: {
      title: '__init__：创建参数与层对象',
      code: 'all_size_list = [input_size] + hidden_size_list + [output_size]\n# 相邻两项决定 W 的形状；b 的长度等于输出节点数\nself.layers["Affine" + str(i)] = Affine(W, b)',
      effect: '参数在这里随机初始化一次。Affine 中的 W、b 与 params 中的数组是同一份；构造网络还没有训练。'
    },
    predict: {
      title: 'predict：依次执行每层 forward',
      code: 'for layer in self.layers.values():\n    x = layer.forward(x)\nreturn x',
      effect: '返回每个样本的类别得分。得分可以为负，尚未经过 SoftmaxWithLoss；不会更新权重。'
    },
    loss: {
      title: 'loss：得分 → 概率与交叉熵',
      code: 'y = self.predict(x)\nreturn self.last_layer.forward(y, t)',
      effect: '先完成一次前向计算，再用 one-hot 标签计算标量损失 L。各层同时保存反向传播需要的中间值。'
    },
    accuracy: {
      title: 'accuracy：统计预测正确的比例',
      code: 'y = np.argmax(self.predict(x), axis=1)\nt = np.argmax(t, axis=1)\nreturn np.mean(y == t)',
      effect: '预测得分和 one-hot 标签分别转为类别编号，再比较。它评价当前参数，不做参数更新。'
    },
    gradient: {
      title: 'gradient：先前向，再反向，收集梯度',
      code: 'self.loss(x, t)\ndout = self.last_layer.backward(1)\nlayers = list(self.layers.values())\nlayers.reverse()\nfor layer in layers:\n    dout = layer.backward(dout)\n# 最后收集每个 Affine 的 dW、db',
      effect: '返回 grads 字典，键与 params 对应，数组形状相同。先 loss 会刷新本批数据的缓存；得到梯度后，参数仍未更新。'
    },
    update: {
      title: 'SGD.update：梯度用于真正修改参数',
      code: 'grads = network.gradient(x_batch, t_batch)\noptimizer.update(network.params, grads)\n# SGD 内部：\nparams[key] -= self.lr * grads[key]',
      effect: '这一步属于优化器，在 MultiLayerNet 类外调用。原地 -= 修改共享数组，下一次前向计算就会使用更新后的参数。'
    }
  };
  document.querySelectorAll('[data-network-lab]').forEach(root => {
    const $ = selector => root.querySelector(selector);
    let selected = root.dataset.stage || 'init';
    const render = () => {
      const preset = presets[$('[data-network-preset]')?.value || 'small'];
      const sizes = preset.sizes;
      const batch = preset.batch;
      const affineCount = sizes.length - 1;
      const rows = [];
      const nodes = [];
      let parameterCount = 0;
      const layerNames = [];
      for (let i = 1; i < sizes.length; i++) {
        const previous = sizes[i - 1], next = sizes[i];
        const output = i === affineCount;
        parameterCount += previous * next + next;
        rows.push(`<tr><td>Affine${i}</td><td>W${i}: ${shape(previous, next)}</td><td>b${i}: (${next},)</td><td>${shape(batch, previous)} → ${shape(batch, next)}</td></tr>`);
        nodes.push(`<div class="net-node${output ? ' output' : ''}"><strong>Affine${i}${output ? ' / 输出层' : ` + Relu${i}`}</strong><span>${shape(batch, previous)} → ${shape(batch, next)}</span><small>${output ? '保留类别得分' : 'ReLU 后形状不变'}</small></div>`);
        layerNames.push(`Affine${i}`);
        if (!output) layerNames.push(`Relu${i}`);
      }
      if ($('[data-network-shape]')) $('[data-network-shape]').textContent = `层宽列表 [${sizes.join(', ')}] · 批量 N=${batch}`;
      if ($('[data-network-stats]')) $('[data-network-stats]').textContent = `${affineCount - 1} 个隐藏层 · ${affineCount} 组 W/b · ${parameterCount.toLocaleString('en-US')} 个可学习参数`;
      if ($('[data-network-rows]')) $('[data-network-rows]').innerHTML = rows.join('');
      if ($('[data-network-map]')) $('[data-network-map]').innerHTML = nodes.join('');
      if (!$('[data-call-title]')) return;
      const method = methods[selected];
      $('[data-call-title]').textContent = method.title;
      const codeBlock = $('[data-call-code]');
      codeBlock.textContent = method.code;
      globalThis.highlightPythonBlock?.(codeBlock);
      $('[data-call-effect]').textContent = method.effect;
      let flow;
      if (selected === 'init') flow = 'params：W1/b1… → 对应 Affine；self.layers：' + layerNames.join(' → ') + '；last_layer 单独保存。';
      if (selected === 'predict') flow = `x ${shape(batch, sizes[0])} → ` + layerNames.join(' → ') + ` → 得分 ${shape(batch, sizes.at(-1))}`;
      if (selected === 'loss') flow = `得分 ${shape(batch, sizes.at(-1))} + 标签 t ${shape(batch, sizes.at(-1))} → SoftmaxWithLoss → 标量 L`;
      if (selected === 'accuracy') flow = `得分与 one-hot 标签 → 两个 (${batch},) 类别编号数组 → 比较 → 一个准确率数值`;
      if (selected === 'gradient') flow = '先 loss；然后 SoftmaxWithLoss.backward(1) → ' + layerNames.slice().reverse().join(' → ') + ' → grads（与参数同形）';
      if (selected === 'update') flow = `${affineCount} 组 W/b 的梯度 → SGD.update → params 中的同一份数组 → 下次前向`;
      $('[data-call-flow]').textContent = flow;
      root.querySelectorAll('[data-network-stage]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.networkStage === selected)));
    };
    $('[data-network-preset]')?.addEventListener('change', render);
    root.querySelectorAll('[data-network-stage]').forEach(button => button.addEventListener('click', () => { selected = button.dataset.networkStage; render(); }));
    render();
  });
})();
