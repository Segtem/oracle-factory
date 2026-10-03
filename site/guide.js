(() => {
  'use strict';
  const input=document.getElementById('change-id');
  const codeNodes=[...document.querySelectorAll('[data-template]')];
  function update(){
    const raw=input.value.trim(); const valid=/^\d{8}-\d{6}-[a-z0-9_-]+$/.test(raw);
    input.setAttribute('aria-invalid',String(Boolean(raw)&&!valid));
    document.getElementById('id-hint').textContent=valid?'Los comandos ya usan tu id. Verificá que coincida con el de la terminal.':raw?'Pegá el id completo que imprimió Factory, sin espacios.':'Los comandos siguientes usan ID_DEL_CAMBIO hasta que lo ingreses.';
    codeNodes.forEach(node=>{node.textContent=node.dataset.template.replaceAll('ID_DEL_CAMBIO',valid?raw:'ID_DEL_CAMBIO');const button=node.closest('.code-block')?.querySelector('button');if(button)button.disabled=!valid;});
  }
  input.addEventListener('input',update); update();
  document.querySelectorAll('.copy-code').forEach(button=>button.addEventListener('click',async()=>{
    const code=button.parentElement.querySelector('code');
    try{await navigator.clipboard.writeText(code.textContent);button.textContent='Copiado';setTimeout(()=>button.textContent='Copiar',1800);}
    catch{const range=document.createRange();range.selectNodeContents(code);getSelection().removeAllRanges();getSelection().addRange(range);button.textContent='Texto seleccionado';}
  }));
})();
