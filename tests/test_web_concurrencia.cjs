/* La página de la simulación en Chromium con Playwright. Escenarios cw1–cw3. Uso: node tests/test_web_concurrencia.cjs NOMBRE */
'use strict';
const assert = require('node:assert/strict');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {chromium} = require('playwright');
const URL_PAGINA = pathToFileURL(path.resolve(__dirname, '../site/concurrencia.html')).href;
const IDS = ['paralelo', 'mismo-archivo', 'decisiones-distintas', 'revision-vieja', 'agente-cierra'];

async function abrir(browser, opciones) {
  const context = await browser.newContext(opciones || {});
  const page = await context.newPage();
  const errores = [], externos = [];
  page.on('pageerror', e => errores.push(e.message));
  page.on('console', m => m.type() === 'error' && errores.push(m.text()));
  page.on('request', r => { if (!r.url().startsWith('file:') && !r.url().startsWith('data:')) externos.push(r.url()); });
  await page.goto(URL_PAGINA);
  await page.waitForSelector('#sim-registro', {state: 'attached'});
  return {page, errores, externos, context};
}
const filas = page => page.locator('#sim-registro li').count();

const ESCENARIOS = {
  // cw1: lo que cuenta la escena es lo que dicen las reglas.
  async agente_no_cierra(browser) {
    const {page, errores, externos, context} = await abrir(browser);
    await page.selectOption('#sim-escenario', 'agente-cierra');
    for (let i = 0; i < 5; i++) await page.click('#sim-paso');
    assert(await page.locator('#sim-fin').isVisible());
    const texto = await page.locator('#sim-registro').innerText();
    assert(/claude-code[^\n]*intentó «cerrar»[^\n]*sólo lo propuso/.test(texto), texto);
    assert(/Ana[^\n]*decide «cerrar»/.test(texto), texto);
    assert(!/claude-code[^\n]*decide «cerrar»/.test(texto));
    assert.deepEqual(errores, []); assert.deepEqual(externos, []);
    await context.close();
  },
  // cw2: cada escenario, hasta el final; el conflicto lo resuelve una persona.
  async recorrer_cada_escenario(browser) {
    const {page, errores, context} = await abrir(browser);
    for (const id of IDS) {
      await page.selectOption('#sim-escenario', id);
      await page.fill('#sim-semilla', '2'); await page.dispatchEvent('#sim-semilla', 'change');
      assert.equal(await filas(page), 0, `${id} no empieza vacío`);
      let guardia = 0, esperas = 0;
      while (!(await page.locator('#sim-fin').isVisible()) && guardia++ < 40) {
        if (await page.locator('#sim-espera').isVisible()) {
          esperas++;
          assert(await page.locator('#sim-paso').isDisabled(), 'se puede avanzar sin que una persona elija');
          const antes = await filas(page);
          await page.click('#sim-paso', {force: true, trial: false}).catch(() => {});
          assert.equal(await filas(page), antes, 'el registro creció sin elegir');
          await page.locator('#sim-espera-opciones button').first().click();
        } else await page.click('#sim-paso');
      }
      const fin = await page.locator('#sim-fin').innerText();
      assert(fin.startsWith('Final: ') && fin.length > 30, `${id}: ${fin}`);
      assert.equal(esperas, {'mismo-archivo': 1, 'decisiones-distintas': 1}[id] || 0, `${id}: esperas`);
      const li = await page.locator('#sim-registro li').evaluateAll(ls => ls.map(l => l.querySelector('.sim-quien').textContent));
      assert(li.every(q => /\((persona|agente|git|oracle)\)/.test(q)), `${id}: ${li}`);
    }
    // reproducir hasta el final solo
    await page.selectOption('#sim-escenario', 'paralelo');
    await page.selectOption('#sim-vel', '400');
    await page.click('#sim-play');
    assert.equal(await page.getAttribute('#sim-play', 'aria-pressed'), 'true');
    await page.waitForSelector('#sim-fin:not([hidden])', {timeout: 15000});
    assert.equal(await page.getAttribute('#sim-play', 'aria-pressed'), 'false');
    assert.deepEqual(errores, []);
    await context.close();
  },
  // cw3: teclado, registro anunciado, movimiento reducido y pantalla chica.
  async usar_con_teclado(browser) {
    const {page, errores, context} = await abrir(browser);
    assert.equal(await page.getAttribute('#sim-registro', 'aria-live'), 'polite');
    await page.selectOption('#sim-escenario', 'mismo-archivo');
    const alcanzados = new Set();
    await page.focus('#sim-escenario');
    for (let i = 0; i < 6; i++) { alcanzados.add(await page.evaluate(() => document.activeElement.id)); await page.keyboard.press('Tab'); }
    for (const id of ['sim-escenario', 'sim-semilla', 'sim-vel', 'sim-paso', 'sim-play', 'sim-reiniciar']) assert(alcanzados.has(id), `Tab no llega a ${id}: ${[...alcanzados]}`);
    await page.focus('#sim-paso');
    const etiquetas = new Set([await page.getAttribute('#sim-escena', 'aria-label')]);
    for (let i = 0; i < 6; i++) { await page.keyboard.press('Enter'); etiquetas.add(await page.getAttribute('#sim-escena', 'aria-label')); }
    assert(etiquetas.size >= 4, [...etiquetas].join(' | '));
    assert(await page.locator('#sim-espera').isVisible(), 'no apareció el conflicto');
    await page.locator('#sim-espera-opciones button').first().focus();
    await page.keyboard.press('Enter');
    assert(!(await page.locator('#sim-espera').isVisible()));
    assert.equal(await page.evaluate(() => document.activeElement.id), 'sim-reiniciar', 'el foco no volvió a los controles (el escenario ya terminó)');
    // el foco no queda atrapado: Tab recorre la página y sale
    let salio = false;
    for (let i = 0; i < 40 && !salio; i++) { await page.keyboard.press('Tab'); salio = await page.evaluate(() => !document.activeElement.closest('.sim-controles')); }
    assert(salio, 'el foco quedó atrapado en los controles');
    await page.click('#sim-reiniciar');
    assert.equal(await filas(page), 0);
    assert.deepEqual(errores, []);
    await context.close();
  },
  async movimiento_reducido_y_pantalla_chica(browser) {
    const {page, errores, context} = await abrir(browser, {reducedMotion: 'reduce', viewport: {width: 360, height: 800}});
    for (const id of IDS) {
      await page.selectOption('#sim-escenario', id);
      assert(await page.locator('#sim-fin').isVisible(), `${id}: no muestra el final`);
      assert((await page.locator('#sim-fin').innerText()).length > 30);
      assert((await filas(page)) >= 4, id);
      const animaciones = await page.evaluate(() => document.getAnimations().filter(a => a.playState === 'running').length);
      assert.equal(animaciones, 0, `${id}: hay ${animaciones} animaciones con movimiento reducido`);
      const [ancho, vista] = await page.evaluate(() => [document.documentElement.scrollWidth, innerWidth]);
      assert(ancho <= vista, `${id}: desplazamiento horizontal ${ancho} > ${vista}`);
    }
    await page.selectOption('#sim-escenario', 'mismo-archivo');
    assert(await page.locator('#sim-nota').isVisible(), 'no avisa que eligió por la persona');
    assert.match(await page.locator('#sim-nota').innerText(), /eligió la primera opción/);
    assert.deepEqual(errores, []);
    await context.close();
  }
};

(async () => {
  const nombre = process.argv[2];
  if (!ESCENARIOS[nombre]) { console.error('escenario desconocido: ' + nombre); process.exit(2); }
  const browser = await chromium.launch({executablePath: process.env.CHROMIUM || '/usr/bin/chromium'});
  try { await ESCENARIOS[nombre](browser); console.log('ok'); }
  catch (e) { console.error(e); process.exitCode = 1; }
  finally { await browser.close(); }
})();
