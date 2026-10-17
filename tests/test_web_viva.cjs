/* La portada viva en Chromium (Playwright): escenas, personajes, minijuego y easter eggs.
   node tests/test_web_viva.cjs <escenario>   — un escenario de la spec por corrida; sale 0 si pasa. */
'use strict';
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const URL_INICIO = pathToFileURL(path.resolve(__dirname, '../site/index.html')).href;

async function abrir(browser, opciones = {}) {
  const context = await browser.newContext({viewport: {width: opciones.ancho || 1440, height: 900},
                                            reducedMotion: opciones.reducido ? 'reduce' : 'no-preference'});
  await context.setOffline(true);
  const page = await context.newPage();
  const errores = [], externos = [];
  page.on('pageerror', e => errores.push(e.message));
  page.on('console', m => { if (m.type() === 'error') errores.push(m.text()); });
  page.on('request', r => { if (/^https?:/.test(r.url())) externos.push(r.url()); });
  await page.goto(URL_INICIO);
  return {page, errores, externos};
}

// El texto que lee una persona: títulos y párrafos, sin lo que agregan los secretos.
const textoVisible = page => page.evaluate(() => [...document.querySelectorAll('main h1, main h2, main h3, main p')]
  .filter(e => !e.closest('[data-huevo]') && !e.closest('#juego')).map(e => e.innerText).join('\n'));

async function bajarHastaElFinal(page) {
  const alto = await page.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y < alto; y += 400) { await page.evaluate(v => scrollTo(0, v), y); await page.waitForTimeout(40); }
  await page.waitForTimeout(300);
}

const ESCENARIOS = {
  async recorrer_la_portada(browser) {
    const {page, errores, externos} = await abrir(browser);
    await bajarHastaElFinal(page);
    // Cada sección de main tiene su escena de pixel art (el recorrido, su canvas).
    const secciones = await page.locator('main > section').evaluateAll(s => s.map(x => [x.id || x.className,
      !!x.querySelector('.pixel-scene svg rect, canvas')]));
    assert(secciones.length >= 9, JSON.stringify(secciones));
    assert.deepEqual(secciones.filter(([, tiene]) => !tiene), []);
    // Al entrar en pantalla, cada escena quedó viva y anima algo.
    const escenas = await page.locator('.pixel-scene').evaluateAll(es => es.map(e => [e.dataset.escena, e.dataset.estado,
      e.getAnimations({subtree: true}).length]));
    assert(escenas.length >= 8);
    for (const [nombre, estado, animaciones] of escenas) {
      assert.equal(estado, 'viva', nombre);
      assert(animaciones > 0, `${nombre} sin animación`);
    }
    // Un personaje que rebota o salta se queda en su lugar: nunca se va a otro punto de la escena.
    await page.evaluate(() => scrollTo(0, 0));
    const muestras = [];
    for (let i = 0; i < 12; i++) {
      muestras.push(await page.locator('.pixel-scene .saluda, .pixel-scene .trabaja, .pixel-scene .salta').evaluateAll(gs =>
        gs.map(g => { const r = g.getBoundingClientRect(), s = g.closest('.pixel-scene').getBoundingClientRect();
                      return [(r.left - s.left) / s.width, (r.top - s.top) / s.height]; })));
      await page.waitForTimeout(180);
    }
    for (let k = 0; k < muestras[0].length; k++) {
      const xs = muestras.map(m => m[k][0]), ys = muestras.map(m => m[k][1]);
      assert(Math.max(...xs) - Math.min(...xs) < 0.01 && Math.max(...ys) - Math.min(...ys) < 0.15,
             `el personaje ${k} se va de su lugar: x ${xs.map(v => v.toFixed(2))} y ${ys.map(v => v.toFixed(2))}`);
    }
    // Los personajes con nombre y su globito: los seis del elenco, también fuera de él.
    const personajes = await page.locator('.personaje').evaluateAll(ps => ps.map(p => [p.dataset.nombre,
      p.querySelector('.cara svg rect') !== null, (p.querySelector('.globo') || {}).innerText || '']));
    const nombres = new Set(personajes.map(([n]) => n));
    for (const n of ['Vos', 'Agente', 'codex', 'agy', 'Oracle', 'Clue']) assert(nombres.has(n), n);
    assert(personajes.every(([, cara, globo]) => cara && globo.length > 20), JSON.stringify(personajes));
    assert(personajes.filter(([n]) => n === 'Vos' || n === 'Agente').length >= 4); // aparecen a lo largo de la página
    // Las herramientas del kit con su sprite.
    assert.equal(await page.locator('.tool-icon[data-sprite] svg').count(), 6);
    assert.deepEqual([errores, externos], [[], []]);
  },

  async movimiento_reducido_y_pantalla_chica(browser) {
    const {page, errores} = await abrir(browser, {reducido: true, ancho: 320});
    await bajarHastaElFinal(page);
    const escenas = await page.locator('.pixel-scene').evaluateAll(es => es.map(e => [e.dataset.escena, e.dataset.estado,
      e.getAnimations({subtree: true}).length]));
    assert(escenas.length >= 8);
    for (const [nombre, estado, animaciones] of escenas) {
      assert.equal(estado, 'final', nombre);
      assert.equal(animaciones, 0, `${nombre} se anima con movimiento reducido`);
    }
    // El estado final: las banderas arriba y lo que brota, visible.
    const finales = await page.locator('.sube, .brota').evaluateAll(es => es.map(e => [getComputedStyle(e).translate,
      getComputedStyle(e).opacity]));
    assert(finales.length >= 7 && finales.every(([t, o]) => (t === 'none' || t === '0px' || t === '0px 0px') && o === '1'),
           JSON.stringify(finales));
    for (const ancho of [320, 390, 768, 1024, 1440]) {
      await page.setViewportSize({width: ancho, height: 900});
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `desborda a ${ancho}`);
    }
    assert.deepEqual(errores, []);
  },

  async una_partida_que_cierra_en_verde(browser) {
    const {page, errores} = await abrir(browser);
    const juego = page.locator('#juego');
    const elegir = async texto => juego.getByRole('button', {name: texto, exact: true}).click();
    await elegir('Aceptar esta spec');
    await elegir('Acordar las medidas');
    await elegir('Pedirle al agente que lo corrija');
    await elegir('Aceptar el riesgo');
    const motivo = await juego.locator('#juego-opciones button').first().innerText();
    await juego.locator('#juego-opciones button').first().click();
    await elegir('Aprobar');
    assert.equal(await juego.getAttribute('data-oracle'), 'verde');
    await elegir('Cerrar el cambio');
    const registro = await page.locator('#juego-registro li').allInnerTexts();
    assert(registro.length >= 8, registro.join('\n'));
    const mias = registro.filter(l => l.startsWith('Vos (persona)'));
    assert(mias.length >= 5);
    assert(mias.some(l => l.includes('Aceptaste el riesgo') && l.includes(motivo)), registro.join('\n'));
    assert(registro.some(l => l.startsWith('Oracle') && l.includes('Verde')));
    assert(registro.some(l => l.startsWith('Agente')) && registro.some(l => l.startsWith('codex')));
    assert(await page.locator('#juego-otra').isVisible());
    assert.deepEqual(errores, []);
  },

  async aprobar_con_un_hallazgo_abierto_y_medidas_sin_acordar(browser) {
    const {page, errores} = await abrir(browser);
    const juego = page.locator('#juego');
    const boton = texto => juego.getByRole('button', {name: texto, exact: true});
    await boton('Aceptar esta spec').click();
    await boton('Dejarlas sin acordar').click();
    await boton('Pedirle al agente que lo corrija').click();
    // Aprobar está, pero no disponible: dice por qué y no avanza.
    assert.equal(await boton('Aprobar').getAttribute('aria-disabled'), 'true');
    await boton('Aprobar').click({force: true});  // no disponible: Playwright no lo cliquearía, una persona sí
    assert.match(await page.locator('#juego-porque').innerText(), /No disponible: queda 1 hallazgo medio abierto/);
    assert.equal(await juego.getAttribute('data-paso'), 'revision');
    await boton('Descartar el hallazgo').click();
    await juego.locator('#juego-opciones button').first().click();
    await boton('Aprobar').click();
    // Sin medidas acordadas, el requisito queda sin juicio y no se puede cerrar.
    assert.equal(await juego.getAttribute('data-oracle'), 'sin_juicio');
    assert.match(await page.locator('#juego-situacion').innerText(), /no hay medidas acordadas/);
    await boton('Cerrar el cambio').click({force: true});
    assert.match(await page.locator('#juego-porque').innerText(), /sin juicio/);
    await boton('Ver el registro').click();
    assert.match((await page.locator('#juego-registro').innerText()), /Sin juicio: el requisito no tiene medidas acordadas/);
    assert.deepEqual(errores, []);
  },

  async jugar_solo_con_teclado(browser) {
    const {page, errores} = await abrir(browser);
    // Tab hasta la primera opción del juego.
    let dentro = false;
    for (let i = 0; i < 200 && !dentro; i++) {
      await page.keyboard.press('Tab');
      dentro = await page.evaluate(() => !!document.activeElement.closest('#juego-opciones'));
    }
    assert(dentro, 'Tab nunca llegó al minijuego');
    const foco = () => page.evaluate(() => document.activeElement.innerText);
    // Aceptar; acordar; corregir; en la revisión, las flechas llevan a «Aceptar el riesgo»; motivo; aprobar; cerrar.
    assert.equal(await foco(), 'Aceptar esta spec');
    await page.keyboard.press('Enter');
    assert.equal(await foco(), 'Acordar las medidas');
    await page.keyboard.press('Enter');
    await page.keyboard.press('Enter');
    assert.equal(await foco(), 'Aceptar el riesgo');  // el foco salta la opción no disponible
    await page.keyboard.press('ArrowLeft');
    assert.equal(await foco(), 'Aprobar');             // pero las flechas la alcanzan
    await page.keyboard.press('Enter');
    assert.match(await page.locator('#juego-porque').innerText(), /No disponible/);
    await page.keyboard.press('ArrowRight');
    await page.keyboard.press('Enter');
    await page.keyboard.press('ArrowDown');
    await page.keyboard.press('ArrowUp');
    await page.keyboard.press('Enter');
    assert.equal(await foco(), 'Aprobar');
    await page.keyboard.press('Enter');
    assert.equal(await foco(), 'Cerrar el cambio');
    await page.keyboard.press('Enter');
    assert(await page.locator('#juego-registro').isVisible());
    assert.equal(await foco(), 'Jugar otra vez');
    await page.keyboard.press('Enter');
    assert.equal(await foco(), 'Aceptar esta spec');
    assert.deepEqual(errores, []);
  },

  async encontrar_los_tres(browser) {
    for (const reducido of [false, true]) {
      const {page, errores} = await abrir(browser, {reducido});
      const antes = await textoVisible(page);
      const escena = page.locator('[data-escena="inicio"]');
      // La chimenea, con teclado: el foco queda en ella.
      await page.locator('#chimenea').focus();
      for (let i = 0; i < 5; i++) await page.keyboard.press('Enter');
      assert.equal(await escena.getAttribute('data-humo'), '5');
      assert.match(await page.locator('#globo-secreto').innerText(), /a pleno/);
      assert.equal(await page.evaluate(() => document.activeElement.id), 'chimenea');
      // El gato, con el mouse.
      await page.locator('#gato').click();
      assert.equal(await escena.getAttribute('data-gato'), '1');
      assert.match(await page.locator('#globo-secreto').innerText(), /Miau/);
      // Konami, desde un enlace con foco: el foco no se mueve y la fiesta se anuncia.
      await page.locator('.topbar nav a').first().focus();
      for (const k of ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a']) {
        await page.keyboard.press(k);
      }
      assert.equal(await page.evaluate(() => document.body.dataset.fiesta), 'si');
      assert.equal(await page.locator('#anuncio').innerText(), 'Modo fiesta en la fábrica.');
      assert.equal(await page.evaluate(() => document.activeElement.textContent), 'Cuatro caminos');
      // Nada tapa el texto ni lo cambia; con movimiento reducido, nada se anima.
      assert.equal(await textoVisible(page), antes);
      const tapado = await page.evaluate(() => {
        const g = document.getElementById('globo-secreto').getBoundingClientRect();
        return [...document.querySelectorAll('main h1, main h2, main p')].filter(e => !e.closest('[data-huevo]'))
          .some(e => { const r = e.getBoundingClientRect(); return r.width && !(r.right < g.left || r.left > g.right || r.bottom < g.top || r.top > g.bottom); });
      });
      assert.equal(tapado, false);
      assert.equal(await page.locator('#globo-secreto').evaluate(e => getComputedStyle(e).pointerEvents), 'none');
      if (reducido) assert.equal(await escena.evaluate(e => e.getAnimations({subtree: true}).length), 0);
      else assert((await page.locator('#confeti rect').count()) > 0);
      assert.deepEqual(errores, []);
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
