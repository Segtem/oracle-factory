/* Las guías con la fábrica viva, en Chromium (Playwright): escena y elenco, movimiento reducido, y el texto de siempre.
   node tests/test_web_guias.cjs <escenario>   — un escenario de la spec por corrida; sale 0 si pasa. */
'use strict';
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const {pathToFileURL} = require('node:url');
const {GUIAS, texto} = require('./texto_guias.cjs');

async function abrir(browser, guia, opciones = {}) {
  const context = await browser.newContext({viewport: {width: opciones.ancho || 1440, height: 900},
                                            reducedMotion: opciones.reducido ? 'reduce' : 'no-preference'});
  await context.setOffline(true);
  const page = await context.newPage();
  const errores = [], externos = [];
  page.on('pageerror', e => errores.push(e.message));
  page.on('console', m => { if (m.type() === 'error') errores.push(m.text()); });
  page.on('request', r => { if (/^https?:/.test(r.url())) externos.push(r.url()); });
  await page.goto(pathToFileURL(path.resolve(__dirname, '../site', guia)).href);
  return {page, errores, externos, context};
}

async function bajarHastaElFinal(page) {
  const alto = await page.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y < alto; y += 400) { await page.evaluate(v => scrollTo(0, v), y); await page.waitForTimeout(30); }
  await page.waitForTimeout(300);
}

const ESCENARIOS = {
  async recorrer_cada_guia(browser) {
    for (const guia of GUIAS) {
      const {page, errores, externos, context} = await abrir(browser, guia);
      await bajarHastaElFinal(page);
      const escenas = await page.locator('.pixel-scene').evaluateAll(es => es.map(e => [e.dataset.escena, e.dataset.estado,
        e.getAnimations({subtree: true}).length, !!e.querySelector('svg rect')]));
      assert.equal(escenas.length, 1, guia);
      const [[nombre, estado, animaciones, dibujada]] = escenas;
      assert(dibujada && estado === 'viva' && animaciones > 0, `${guia}: ${nombre} ${estado} ${animaciones}`);
      // Cada guía, su escena propia (agy AGY-002).
      assert.equal(nombre, {'desde-cero.html': 'guia', 'modos.html': 'modos', 'colaboracion.html': 'equipo'}[guia], guia);
      // Al menos tres secciones con un personaje con nombre, cara y globito.
      const secciones = await page.locator('main section').evaluateAll(ss => ss.filter(s => {
        const p = s.querySelector('.personaje[data-nombre]');
        return p && p.querySelector('.cara svg rect') && (p.querySelector('.globo') || {}).textContent.length > 20;
      }).map(s => s.id));
      assert(secciones.length >= 3, `${guia}: ${secciones}`);
      // Ningún personaje animado se va de su lugar (el error de transform de la portada).
      await page.evaluate(() => scrollTo(0, 0));
      const muestras = [];
      for (let i = 0; i < 10; i++) {
        muestras.push(await page.locator('.pixel-scene g.quien, .pixel-scene .viaja2').evaluateAll(gs => gs.map(g => {
          const r = g.getBoundingClientRect(), s = g.closest('.pixel-scene').getBoundingClientRect();
          return [(r.left - s.left) / s.width, (r.top - s.top) / s.height, g.classList.contains('viaja2')];
        })));
        await page.waitForTimeout(150);
      }
      for (let k = 0; k < muestras[0].length; k++) {
        const xs = muestras.map(m => m[k][0]), ys = muestras.map(m => m[k][1]);
        assert(Math.max(...ys) - Math.min(...ys) < 0.15, `${guia}: el sprite ${k} salta en y ${ys}`);
        // Y está parado sobre el suelo o la cinta, no en la esquina de arriba (un transform que pisa su posición).
        assert(ys.every(y => y > 0.3 && y < 0.6), `${guia}: el sprite ${k} no está en su lugar: y ${ys}`);
        if (!muestras[0][k][2]) assert(Math.max(...xs) - Math.min(...xs) < 0.01, `${guia}: el sprite ${k} se va en x ${xs}`);
      }
      // Los secretos son de la portada: en una guía, el código Konami no hace nada ni rompe nada.
      for (const k of ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a']) {
        await page.keyboard.press(k);
      }
      assert.notEqual(await page.evaluate(() => document.body.dataset.fiesta), 'si', guia);
      assert.deepEqual([errores, externos], [[], []], guia);
      await context.close();
    }
  },

  async movimiento_reducido_y_pantalla_chica(browser) {
    for (const guia of GUIAS) {
      const {page, errores, context} = await abrir(browser, guia, {reducido: true, ancho: 320});
      await bajarHastaElFinal(page);
      const escenas = await page.locator('.pixel-scene').evaluateAll(es => es.map(e => [e.dataset.estado,
        e.getAnimations({subtree: true}).length]));
      assert.deepEqual(escenas, [['final', 0]], guia);
      const sube = await page.locator('.pixel-scene .sube').evaluateAll(es => es.map(e => getComputedStyle(e).translate));
      assert(sube.every(t => t === 'none' || t === '0px' || t === '0px 0px'), `${guia}: ${sube}`);
      // La caja de la cinta queda a mitad de camino, quieta.
      const cajas = await page.locator('.pixel-scene .viaja2').evaluateAll(es => es.map(e => getComputedStyle(e).translate));
      assert(cajas.every(t => t === '66px' || t === '66px 0px'), `${guia}: ${cajas}`);
      for (const ancho of [320, 390, 768, 1024, 1440]) {
        await page.setViewportSize({width: ancho, height: 900});
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `${guia} desborda a ${ancho}`);
      }
      assert.deepEqual(errores, [], guia);
      await context.close();
    }
  },

  async comparar_con_la_version_anterior(browser) {
    const antes = JSON.parse(fs.readFileSync(path.join(__dirname, 'datos/guias-texto.json'), 'utf8'));
    for (const guia of GUIAS) {
      const {page, context} = await abrir(browser, guia);
      assert.deepEqual(await texto(page), antes[guia], guia);
      // Lo agregado está marcado y no reemplaza nada: sin data-viva, el texto es el de antes.
      assert(await page.locator('[data-viva]').count() >= 4, guia);
      await context.close();
    }
  }
};

(async () => {
  const nombre = process.argv[2];
  if (!ESCENARIOS[nombre]) {
    console.error(`escenario desconocido: ${nombre}; los hay: ${Object.keys(ESCENARIOS).join(', ')}`);
    process.exit(2);
  }
  const browser = await chromium.launch({executablePath: process.env.CHROMIUM || '/usr/bin/chromium', headless: true});
  try {
    await ESCENARIOS[nombre](browser);
    console.log(`${nombre}: ok`);
  } finally {
    await browser.close();
  }
})().catch(e => { console.error(e); process.exit(1); });
