(() => {
  'use strict';
  const change = document.getElementById('change-id');
  const requirement = document.getElementById('requisito-id');
  const nodes = [...document.querySelectorAll('[data-template]')];
  function update() {
    const id = change.value.trim();
    const rid = requirement.value.trim();
    const validId = /^\d{8}-\d{6}-[a-z0-9_-]+$/.test(id);
    const validRid = /^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$/.test(rid);
    change.setAttribute('aria-invalid', String(Boolean(id) && !validId));
    requirement.setAttribute('aria-invalid', String(Boolean(rid) && !validRid));
    document.getElementById('id-hint').textContent = validId ? 'Los comandos ya usan tu id. Verificá que coincida con el de la terminal.' : id ? 'Pegá el id completo que imprimió Factory, sin espacios.' : 'Los comandos usan ID_DEL_CAMBIO hasta que lo ingreses.';
    document.getElementById('requisito-hint').textContent = validRid ? 'Los comandos ya usan este requisito. Comprobá que pertenezca al cambio.' : rid ? 'Pegá el id completo del requisito que imprimió importar o medir --listar.' : 'La asociación usa ID_DEL_REQUISITO hasta que lo ingreses.';
    nodes.forEach(node => {
      const template = node.dataset.template;
      node.textContent = template.replaceAll('ID_DEL_CAMBIO', validId ? id : 'ID_DEL_CAMBIO').replaceAll('ID_DEL_REQUISITO', validRid ? rid : 'ID_DEL_REQUISITO');
      const button = node.closest('.code-block')?.querySelector('button');
      if (button) button.disabled = (template.includes('ID_DEL_CAMBIO') && !validId) || (template.includes('ID_DEL_REQUISITO') && !validRid);
    });
  }
  change.addEventListener('input', update);
  requirement.addEventListener('input', update);
  update();
  document.querySelectorAll('.copy-code').forEach(button => button.addEventListener('click', async () => {
    const code = button.parentElement.querySelector('code');
    try {
      await navigator.clipboard.writeText(code.textContent);
      button.textContent = 'Copiado';
      setTimeout(() => button.textContent = 'Copiar', 1800);
    } catch {
      const range = document.createRange();
      range.selectNodeContents(code);
      getSelection().removeAllRanges();
      getSelection().addRange(range);
      button.textContent = 'Texto seleccionado';
    }
  }));
})();
