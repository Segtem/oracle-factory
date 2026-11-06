/* Las seis páginas a 360 px, con teclado: sin desplazamiento horizontal, menú alcanzable, sin errores ni pedidos externos. Escenario wp4. */
'use strict';
const assert = require('node:assert/strict');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {chromium} = require('playwright');
const PAGINAS = ['index.html', 'desde-cero.html', 'modos.html', 'colaboracion.html', 'concurrencia.html', 'documentacion.html'];

(async () => {
  const browser = await chromium.launch({executablePath: process.env.CHROMIUM || '/usr/bin/chromium'});
  try {
    for (const nombre of PAGINAS) {
      const context = await browser.newContext({viewport: {width: 360, height: 800}});
      const page = await context.newPage();
      const errores = [], externos = [];
      page.on('pageerror', e => errores.push(e.message));
      page.on('console', m => m.type() === 'error' && errores.push(m.text()));
      page.on('request', r => { if (!/^(file|data):/.test(r.url())) externos.push(r.url()); });
      await page.goto(pathToFileURL(path.resolve(__dirname, '../site', nombre)).href);
      await page.waitForTimeout(250);
      const [ancho, vista] = await page.evaluate(() => [document.documentElement.scrollWidth, innerWidth]);
      assert(ancho <= vista, `${nombre}: desplazamiento horizontal ${ancho} > ${vista}`);
      const enlaces = await page.locator('.topbar nav a').count();
      assert.equal(enlaces, 10, `${nombre}: ${enlaces} enlaces en el menú`);
      // Tab recorre el menú: cada enlace recibe el foco, y el foco queda dentro de la pantalla
      await page.locator('.topbar nav a').first().focus();
      const vistos = new Set();
      for (let i = 0; i < enlaces; i++) {
        vistos.add(await page.evaluate(() => document.activeElement.textContent));
        const caja = await page.evaluate(() => { const r = document.activeElement.getBoundingClientRect(); return [r.left, r.right]; });
        assert(caja[0] >= -1 && caja[1] <= 361, `${nombre}: el enlace enfocado queda fuera de la pantalla ${caja}`);
        await page.keyboard.press('Tab');
      }
      assert.equal(vistos.size, enlaces, `${nombre}: Tab no recorre todo el menú: ${[...vistos]}`);
      const [ancho2, vista2] = await page.evaluate(() => [document.documentElement.scrollWidth, innerWidth]);
      assert(ancho2 <= vista2, `${nombre}: desplazamiento horizontal tras recorrer el menú`);
      assert.deepEqual(errores, [], nombre); assert.deepEqual(externos, [], nombre);
      await context.close();
    }
    console.log('ok');
  } catch (e) { console.error(e); process.exitCode = 1; }
  finally { await browser.close(); }
})();
