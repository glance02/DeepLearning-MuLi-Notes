(() => {
  'use strict';
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const fmt = (n, digits = 4) => Number(n).toFixed(digits);
  const softmax = scores => { const m = Math.max(...scores); const e = scores.map(v => Math.exp(v - m)); const s = e.reduce((a,b) => a+b, 0); return e.map(v => v/s); };
  const argmax = values => values.indexOf(Math.max(...values));
  const sum = values => values.reduce((a,b) => a+b, 0);
  const svg = (node, content) => { node.innerHTML = content; };
  const attrs = (x, y, value, extra = '') => `<text x="${x}" y="${y}" ${extra}>${value}</text>`;

  const search = $('#reference-search');
  if (search) {
    const cards = $$('[data-ref]');
    search.addEventListener('input', () => {
      const terms = search.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
      let count = 0;
      for (const card of cards) {
        const haystack = `${card.textContent} ${card.dataset.keywords || ''}`.toLowerCase();
        card.hidden = !terms.every(term => haystack.includes(term));
        if (!card.hidden) count++;
      }
      for (const section of $$('.chapter-section')) section.hidden = !$$('[data-ref]', section).some(card => !card.hidden);
      $('#search-status').textContent = terms.length ? `找到 ${count} 条相关笔记；清空输入可回到全部内容。` : '输入概念或函数名，例如：广播、softmax、伪参数、epoch。';
      $('#overview').hidden = !!terms.length;
    });
    search.addEventListener('keydown', event => { if (event.key === 'Escape') { search.value=''; search.dispatchEvent(new Event('input')); } });
    for (const link of $$('a[href]')) link.addEventListener('click', () => {
      const destination=new URL(link.href);
      if (search.value && destination.pathname===location.pathname && destination.hash) { search.value=''; search.dispatchEvent(new Event('input')); }
    });
  }
  for (const button of $$('[data-print]')) button.addEventListener('click', () => window.print());
  let printDetails = [];
  window.addEventListener('beforeprint', () => { printDetails = $$('details').filter(node => !node.open); printDetails.forEach(node => node.open = true); });
  window.addEventListener('afterprint', () => printDetails.forEach(node => node.open = false));
  for (const quiz of $$('.quiz')) {
    quiz.addEventListener('submit', event => {
      event.preventDefault();
      const selected = $('input:checked', quiz);
      const feedback = $('.feedback', quiz);
      if (!selected) { feedback.textContent = '先选一个答案，再核对。'; feedback.removeAttribute('data-correct'); return; }
      const correct = selected.value === quiz.dataset.answer;
      feedback.dataset.correct = String(correct);
      feedback.textContent = `${correct ? '答对了。' : '再想一步。'}${quiz.dataset.explanation}`;
    });
    quiz.addEventListener('reset', () => { const feedback = $('.feedback', quiz); feedback.textContent = ''; feedback.removeAttribute('data-correct'); });
  }

  const shapes = $('[data-lab="shapes"]');
  if (shapes) {
    const render = () => {
      const [n,d,h] = ['n','d','h'].map(key => Number($(`[name=${key}]`, shapes).value));
      $('[data-shape-code]', shapes).textContent = `x.shape  = (${n}, ${d})\nW1.shape = (${d}, ${h})\nb1.shape = (${h},)\n\na1 = np.dot(x, W1) + b1\na1.shape = (${n}, ${h})\nz1.shape = (${n}, ${h})`;
      svg($('svg', shapes), `<defs><marker id="shape-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10" fill="#12675f"/></marker></defs>` +
        [[20,40,125,100,'X',`${n} × ${d}`],[220,40,125,100,'W₁',`${d} × ${h}`],[430,40,150,100,'A₁',`${n} × ${h}`]].map(([x,y,w,z,title,shape]) => `<rect x="${x}" y="${y}" width="${w}" height="${z}" rx="5" fill="${title==='A₁'?'#eaf3ed':'white'}" stroke="#91b4a2"/>${attrs(x+w/2,y+38,title,'text-anchor="middle" style="font-size:22px"')}${attrs(x+w/2,y+70,shape,'text-anchor="middle"')}`).join('') +
        attrs(180,98,'×','text-anchor="middle" style="font-size:25px"') + `<path d="M360 90 H413" stroke="#12675f" stroke-width="2" marker-end="url(#shape-arrow)"/>` + attrs(387,63,'+ b₁','text-anchor="middle"') + attrs(300,178,`内侧维度 ${d} 对齐；偏置 (${h},) 加到每个样本。`,'text-anchor="middle"'));
    };
    $$('select', shapes).forEach(node => node.addEventListener('change', render)); render();
  }

  const gates = $('[data-lab="gates"]');
  if (gates) {
    const points = [[0,0],[0,1],[1,0],[1,1]];
    const targets = {AND:[0,0,0,1],OR:[0,1,1,1],NAND:[1,1,1,0],XOR:[0,1,1,0]};
    const presets = {AND:[.5,.5,-.7],OR:[.5,.5,-.2],NAND:[-.5,-.5,.7],XOR:[.5,.5,-.7]};
    const render = () => {
      const goal = $('[name=gate]', gates).value;
      const [w1,w2,b] = ['w1','w2','bias'].map(key => Number($(`[name=${key}]`, gates).value));
      ['w1','w2','bias'].forEach((key,i) => $(`[data-value=${key}]`, gates).textContent = fmt([w1,w2,b][i],1));
      const results = points.map(([x,y]) => { const a = (Math.round(w1*10)*x+Math.round(w2*10)*y+Math.round(b*10))/10; return {a,pred:a>0?1:0}; });
      const correct = results.filter((v,i) => v.pred===targets[goal][i]).length;
      $('[data-gate-result]', gates).textContent = `${goal}：${correct}/4 个输入判对。${goal==='XOR' ? '调整参数试试，单条直线无法把两条对角上的类别同时分开。' : '观察偏置怎样移动边界，权重怎样改变边界方向。'}`;
      $('[data-gate-table]', gates).innerHTML = points.map(([x,y],i) => `<tr><td>(${x}, ${y})</td><td>${fmt(results[i].a,2)}</td><td>${results[i].pred}</td><td>${targets[goal][i]}</td><td>${results[i].pred===targets[goal][i]?'✓':'×'}</td></tr>`).join('');
      const sx = x => 75+x*220, sy = y => 290-y*220;
      let boundary = '';
      if (Math.abs(w2)>1e-10) boundary=`<path d="M${sx(-.2)} ${sy((-b+w1*.2)/w2)} L${sx(1.2)} ${sy((-b-w1*1.2)/w2)}" stroke="#12675f" stroke-width="2"/>`;
      else if (Math.abs(w1)>1e-10) boundary=`<path d="M${sx(-b/w1)} 30 V330" stroke="#12675f" stroke-width="2"/>`;
      svg($('svg', gates), `<defs><clipPath id="gate-clip"><rect x="31" y="25" width="310" height="310"/></clipPath></defs><path d="M45 310 H330 M55 325 V35" stroke="#bcc9bf"/>${attrs(325,333,'x₁')}${attrs(25,38,'x₂')}<g clip-path="url(#gate-clip)">${boundary}</g>` + points.map(([x,y],i) => `<circle cx="${sx(x)}" cy="${sy(y)}" r="25" fill="${targets[goal][i]?'#dcece0':'#fff'}" stroke="${results[i].pred===targets[goal][i]?'#12675f':'#b34a49'}" stroke-width="${results[i].pred===targets[goal][i]?2:4}"/>${attrs(sx(x),sy(y)+5,targets[goal][i],'text-anchor="middle" style="font-size:17px"')}${attrs(sx(x),sy(y)+43,`(${x}, ${y})`,'text-anchor="middle"')}`).join('') + attrs(380,95,`${fmt(w1,1)} x₁ + ${fmt(w2,1)} x₂`,'style="font-size:17px"') + attrs(380,126,`+ ${fmt(b,1)} = 0`,'style="font-size:17px"') + attrs(380,177,'圆内数字：目标输出') + attrs(380,205,'红色外圈：当前判错') + attrs(380,233,'直线：加权和为 0 的边界'));
    };
    $$('input', gates).forEach(node => node.addEventListener('input', render));
    $('[name=gate]', gates).addEventListener('change', () => { const preset=presets[$('[name=gate]',gates).value]; ['w1','w2','bias'].forEach((key,i) => $(`[name=${key}]`,gates).value=preset[i]); render(); });
    render();
  }

  const scores = $('[data-lab="scores"]');
  if (scores) {
    const render = () => {
      const a = [0,1,2].map(i => Number($(`[name=score${i}]`,scores).value));
      const target = Number($('[name=target]',scores).value);
      const p = softmax(a), pred=argmax(p), loss=-Math.log(p[target]+1e-7), mean=(loss-Math.log(.8+1e-7))/2;
      [0,1,2].forEach(i => $(`[data-value=score${i}]`,scores).textContent=fmt(a[i],1));
      $('[data-loss]',scores).textContent=fmt(loss,3); $('[data-mean]',scores).textContent=fmt(mean,3); $('[data-pred]',scores).textContent=`${pred} / ${pred===target?'正确':'错误'}`;
      $('[data-prob-code]',scores).textContent=`z = [${a.map(v=>fmt(v,1)).join(', ')}]\ny = [${p.map(v=>fmt(v,4)).join(', ')}]\nt = [${[0,1,2].map(i=>i===target?1:0).join(', ')}]\ny.argmax() = ${pred}\ny.sum()    = ${fmt(sum(p),4)}`;
      svg($('svg',scores), [0,1,2].map(i => `<rect x="105" y="${25+i*64}" width="360" height="30" rx="3" fill="#edf1e9"/><rect x="105" y="${25+i*64}" width="${p[i]*360}" height="30" rx="3" fill="${i===target?'#12675f':'#9db9a5'}"/>${attrs(18,46+i*64,`类别 ${i}${i===target?' ★':''}`)}${attrs(485,46+i*64,fmt(p[i],4))}`).join(''));
    };
    $$('input',scores).forEach(node=>node.addEventListener('input',render)); $('[name=target]',scores).addEventListener('change',render); render();
  }

  const gradient = $('[data-lab="gradient"]');
  if (gradient) {
    let x=[3,4], stage=0, grads=[null,null], plus=null, minus=null, base=[3,4], updates=0;
    const h=1e-4, f=v=>sum(v.map(t=>t*t));
    const descriptions=['当前位置是 [3, 4]。下一步只给第一个分量加 h。','第一个分量 +h，第二个保持不变；记录 L₊。','第一个分量 −h，第二个仍不变；记录 L₋。','第一个分量恢复原值，得到第一个偏导数。','第二个分量 +h，第一个保持原值；记录新的 L₊。','第二个分量 −h，第一个仍不变；记录新的 L₋。','全部恢复原值，两个偏导数已收集。现在可以真正更新参数。'];
    const render = () => {
      const lr=Number($('[name=lr]',gradient).value);
      $('[data-value=lr]',gradient).textContent=fmt(lr,2);
      $('[data-gradient-status]',gradient).textContent=stage===0 ? `第 ${updates+1} 次求梯度从 [${base.map(v=>fmt(v,4)).join(', ')}] 开始。下一步只给第一个分量加 h。` : descriptions[stage];
      $('[data-point]',gradient).textContent=`[${x.map(v=>fmt(v,4)).join(', ')}]`;
      $('[data-fvalue]',gradient).textContent=fmt(f(x),8);
      $('[data-gradvalue]',gradient).textContent=`[${grads.map(v=>v===null?'—':fmt(v,4)).join(', ')}]`;
      $('[data-gradient-code]',gradient).textContent=`h = 0.0001\n当前参数 = [${x.map(v=>fmt(v,4)).join(', ')}]\nL_plus  = ${plus===null?'尚未计算':fmt(plus,8)}\nL_minus = ${minus===null?'尚未计算':fmt(minus,8)}\ngrad = [${grads.map(v=>v===null?'尚未计算':fmt(v,6)).join(', ')}]`;
      $('[data-gradient-step]',gradient).disabled=stage===6; $('[data-gradient-update]',gradient).disabled=stage!==6;
      $$('[data-phase]',gradient).forEach(node=>node.classList.toggle('active',Number(node.dataset.phase)===Math.floor(stage/3)));
      const proposal=stage===6?base.map((v,i)=>v-lr*grads[i]):base;
      const r=Math.max(5,Math.ceil(Math.max(...base.map(Math.abs),...proposal.map(Math.abs)))+1), sx=v=>280+v/r*200, sy=v=>160-v/r*120;
      svg($('svg',gradient), `<defs><marker id="grad-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10" fill="#12675f"/></marker></defs>` + [1,2,3,4].map(k=>`<ellipse cx="280" cy="160" rx="${k/r*200}" ry="${k/r*120}" fill="none" stroke="#e0e6dc"/>`).join('') + `<path d="M35 160 H530 M280 20 V300" stroke="#bdc9bf"/>${attrs(516,183,'x₀')}${attrs(293,25,'x₁')}<circle cx="${sx(base[0])}" cy="${sy(base[1])}" r="6" fill="#12675f"/>` + (stage===6?`<path d="M${sx(base[0])} ${sy(base[1])} L${sx(base[0]-grads[0]*lr)} ${sy(base[1]-grads[1]*lr)}" stroke="#12675f" stroke-width="2" marker-end="url(#grad-arrow)"/>`:'') + attrs(25,320,stage===6?'箭头展示按当前学习率更新的位置；点击「应用更新」才真正移动。':'扰动很小，主要观察上方数值；原始位置保持为绿色圆点。'));
    };
    $('[data-gradient-step]',gradient).addEventListener('click',()=>{
      stage++;
      if(stage===1){x[0]=base[0]+h;plus=f(x);}
      if(stage===2){x[0]=base[0]-h;minus=f(x);}
      if(stage===3){x[0]=base[0];grads[0]=(plus-minus)/(2*h);plus=null;minus=null;}
      if(stage===4){x[1]=base[1]+h;plus=f(x);}
      if(stage===5){x[1]=base[1]-h;minus=f(x);}
      if(stage===6){x[1]=base[1];grads[1]=(plus-minus)/(2*h);}
      render();
    });
    $('[data-gradient-update]',gradient).addEventListener('click',()=>{
      const lr=Number($('[name=lr]',gradient).value); x=x.map((v,i)=>v-lr*grads[i]);base=[...x];stage=0;grads=[null,null];plus=null;minus=null;updates++;render();
    });
    $('[data-gradient-reset]',gradient).addEventListener('click',()=>{x=[3,4];base=[3,4];stage=0;grads=[null,null];plus=null;minus=null;updates=0;render();});
    $('[name=lr]',gradient).addEventListener('input',render);render();
  }

  const batch = $('[data-lab="batch"]');
  if(batch){
    const data=[{x:[1,0],t:0},{x:[.8,.2],t:0},{x:[0,1],t:1},{x:[.2,.8],t:1},{x:[-1,-1],t:2},{x:[-.7,-.8],t:2}];
    let W=[[.2,-.1,0],[-.1,.2,0]], ids=[], phase=0, steps=0, g=null, lossBefore=null, lossAfter=null, seed=2718;
    const random=()=>{seed=(1664525*seed+1013904223)>>>0;return seed/4294967296;};
    const loss=()=>sum(ids.map(id=>{const row=data[id];const p=softmax([0,1,2].map(j=>row.x[0]*W[0][j]+row.x[1]*W[1][j]));return -Math.log(p[row.t]+1e-7);}))/ids.length;
    const render=()=>{
      $('[data-batch-board]',batch).innerHTML=data.map((row,i)=>{const count=ids.filter(v=>v===i).length;return `<div class="sample${count?' chosen':''}"><span>编号 ${i}</span><b>类 ${row.t}</b><span>${count?`抽中 ×${count}`:'未抽中'}</span></div>`;}).join('');
      $('[data-batch-ids]',batch).textContent=ids.length?`[${ids.join(', ')}]`:'尚未抽样';
      $('[data-batch-count]',batch).textContent=steps;
      $('[data-batch-loss]',batch).textContent=lossAfter===null?'—':fmt(lossAfter,4);
      $('[data-batch-code]',batch).textContent=`batch_mask = ${ids.length?'['+ids.join(', ')+']':'尚未抽样'}\nx_batch.shape = ${ids.length?'(2, 2)':'—'}\nt_batch.shape = ${ids.length?'(2, 3)':'—'}\ngrad.shape = ${g?'(2, 3)':'—'}\n${g?'grad = ['+g.map(row=>'['+row.map(v=>fmt(v,4)).join(', ')+']').join(',\n        ')+']':'grad = 尚未求导'}`;
      $('[data-batch-action]',batch).textContent=['抽取下一批','固定这批，求梯度','应用一次参数更新'][phase];
      $('[data-batch-status]',batch).textContent=phase===0?(steps?`第 ${steps} 次更新完成。同批损失 ${fmt(lossBefore,4)} → ${fmt(lossAfter,4)}。下一次点击才重新抽样。`:'先抽2个样本编号；这里默认有放回抽样。'):phase===1?'这批样本已固定。下一步对6个权重逐个做中心差分，所有损失计算使用同一批图像与标签。':'已得到完整梯度，当前权重仍是求导前的值；下一步才执行 W -= 0.1 * grad。';
      $$('[data-batch-phase]',batch).forEach(node=>node.classList.toggle('active',Number(node.dataset.batchPhase)===phase));
    };
    $('[data-batch-action]',batch).addEventListener('click',()=>{
      if(phase===0){ids=[Math.floor(random()*6),Math.floor(random()*6)];g=null;lossBefore=loss();lossAfter=null;phase=1;}
      else if(phase===1){g=W.map(row=>row.map(()=>0));for(let r=0;r<2;r++)for(let c=0;c<3;c++){const old=W[r][c];W[r][c]=old+1e-4;const p=loss();W[r][c]=old-1e-4;const m=loss();g[r][c]=(p-m)/2e-4;W[r][c]=old;}phase=2;}
      else{W=W.map((row,r)=>row.map((v,c)=>v-.1*g[r][c]));lossAfter=loss();steps++;phase=0;}render();
    });
    $('[data-batch-reset]',batch).addEventListener('click',()=>{W=[[.2,-.1,0],[-.1,.2,0]];ids=[];phase=0;steps=0;g=null;lossBefore=null;lossAfter=null;seed=2718;render();});render();
  }
})();
