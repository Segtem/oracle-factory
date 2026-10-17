/* El texto de las guías como lo lee una persona, sin lo que agrega la fábrica viva ([data-viva]).
   node tests/texto_guias.cjs > tests/datos/guias-texto.json   — congela el de antes del cambio web-guias. */
'use strict';
const {chromium} = require('playwright');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const GUIAS = ['desde-cero.html', 'modos.html', 'colaboracion.html'];

// Todo nodo de texto de la guía, en orden (codex CG-001: no sólo algunos elementos), salvo scripts y lo agregado.
async function texto(page) {
  return page.evaluate(() => {
    const salida = [], recorrido = document.createTreeWalker(document.querySelector('main'), NodeFilter.SHOW_TEXT);
    for (let n = recorrido.nextNode(); n; n = recorrido.nextNode()) {
      const e = n.parentElement;
      if (e.closest('[data-viva], script, style')) continue;
      // Los comandos, tal cual: un salto de línea de menos cambia lo que se ejecuta (agy AGY-001, codex CG-001).
      const s = e.closest('pre, code') ? n.textContent : n.textContent.replace(/\s+/g, ' ').trim();
      if (s) salida.push(s);
    }
    return salida;
  });
}

async function leer(browser) {
  const page = await browser.newPage();
  const salida = {};
  for (const g of GUIAS) {
    await page.goto(pathToFileURL(path.resolve(process.env.SITIO || path.join(__dirname, '../site'), g)).href);
    salida[g] = await texto(page);
  }
  await page.close();
  return salida;
}

module.exports = {GUIAS, texto, leer};

if (require.main === module) {
  (async () => {
    const browser = await chromium.launch({executablePath: process.env.CHROMIUM || '/usr/bin/chromium'});
    try { process.stdout.write(JSON.stringify(await leer(browser), null, 1) + '\n'); } finally { await browser.close(); }
  })().catch(e => { console.error(e); process.exit(1); });
}
