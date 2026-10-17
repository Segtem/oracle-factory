/* El texto de las guías como lo lee una persona, sin lo que agrega la fábrica viva ([data-viva]).
   node tests/texto_guias.cjs > tests/datos/guias-texto.json   — congela el de antes del cambio web-guias. */
'use strict';
const {chromium} = require('playwright');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const GUIAS = ['desde-cero.html', 'modos.html', 'colaboracion.html'];

async function texto(page) {
  return page.evaluate(() => [...document.querySelectorAll('main h1, main h2, main h3, main h4, main p, main li, main td, main th, main pre, main summary, main dt, main dd')]
    .filter(e => !e.closest('[data-viva]') && !e.closest('script'))
    .map(e => e.textContent.replace(/\s+/g, ' ').trim()).filter(Boolean));
}

async function leer(browser) {
  const page = await browser.newPage();
  const salida = {};
  for (const g of GUIAS) {
    await page.goto(pathToFileURL(path.resolve(__dirname, '../site', g)).href);
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
