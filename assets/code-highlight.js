(() => {
  'use strict';
  const highlightPythonBlock = block => {
    const source = block.textContent;
    block.innerHTML = hljs.highlight(source, { language: 'python', ignoreIllegals: true }).value;
    block.classList.add('hljs', 'language-python');
  };
  globalThis.highlightPythonBlock = highlightPythonBlock;
  document.querySelectorAll('pre code.language-python').forEach(highlightPythonBlock);
})();
