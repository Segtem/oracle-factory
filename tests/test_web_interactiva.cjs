/* La portada interactiva en Chromium (Playwright): el recorrido, los tres ejemplos, los tres pasos y la accesibilidad.
   node tests/test_web_interactiva.cjs <escenario>   — un escenario de la spec por corrida; sale 0 si pasa. */
'use strict';
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const URL_INICIO = pathToFileURL(path.resolve(__dirname, '../site/index.html')).href;
const PASOS = ['pedido', 'spec', 'aprobacion', 'medidas', 'codigo', 'evidencia', 'revision', 'juicio', 'cierre'];
const DE_PERSONA = new Set(['aprobacion', 'medidas', 'revision', 'cierre']);
const NUEVAS = '#empezar, #camino, #ejemplos';

async function abrir(browser, opciones = {}) {
  const context = await browser.newContext({viewport: {width: opciones.ancho || 1440, height: 900},
                                            reducedMotion: opciones.reducido ? 'reduce' : 'no-preference',
                                            javaScriptEnabled: opciones.sinJs ? false : true});
  await context.setOffline(true);
  await context.addInitScript(() => {
    Object.defineProperty(navigator, 'clipboard', {value: {writeText: async t => { window.__copiado = t; }}});
  });
  const page = await context.newPage();
  const errores = [], externos = [];
  page.on('pageerror', e => errores.push(e.message));
  page.on('console', m => { if (m.type() === 'error') errores.push(m.text()); });
  page.on('request', r => { if (!/^(file|data):/.test(r.url())) externos.push(r.url()); });
  await page.goto(URL_INICIO);
  return {page, errores, externos};
}

// El paso que se ve: el único <li> visible del recorrido.
async function pasoVisible(page) {
  const visibles = await page.locator('#camino-pasos > li').evaluateAll(ls => ls.filter(l => l.offsetParent !== null).map(l => ({
    paso: l.dataset.paso, actor: (l.querySelector('.actor') || {}).innerText || '', comando: (l.querySelector('.comando code') || {}).innerText || '',
    queda: (l.querySelector('.queda') || {}).innerText || '', persona: l.classList.contains('decision-persona')})));
  return visibles;
}

async function comprobarPaso(page, i) {
  const visibles = await pasoVisible(page);
  assert.equal(visibles.length, 1, JSON.stringify(visibles));
  const [v] = visibles;
  assert.equal(v.paso, PASOS[i]);
  assert(v.actor.length > 8 && v.comando.startsWith('oracle-factory') && v.queda.length > 20, JSON.stringify(v));
  assert.equal(await page.locator('#camino-contador').innerText(), `Paso ${i + 1} de 9`);
  assert.equal(await page.locator('[data-escena="camino"]').getAttribute('data-paso'), PASOS[i]);
  // Las decisiones de una persona se distinguen a la vista: el visor cambia de color y el sello se ve.
  const visor = page.locator('#camino-visor');
  assert.equal(await visor.getAttribute('data-persona'), DE_PERSONA.has(PASOS[i]) ? 'si' : 'no');
  const sello = page.locator(`#camino-pasos > li[data-paso="${PASOS[i]}"] .sello`);
  assert.equal((await sello.count()) > 0 && await sello.isVisible(), DE_PERSONA.has(PASOS[i]));
  return visor.evaluate(e => getComputedStyle(e).borderTopColor);
}

// Los controles del recorrido y de los ejemplos, con su nombre accesible.
const nombreAccesible = e => (e.getAttribute('aria-label') || (e.labels && [...e.labels].map(l => l.innerText).join(' ')) || e.innerText || '').trim();

function luminancia([r, g, b]) {
  const c = [r, g, b].map(v => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; });
  return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
}

const ESCENARIOS = {
  async avanzar_y_retroceder(browser) {
    const {page, errores} = await abrir(browser);
    assert.deepEqual(await pasoVisible(page), []);  // empieza en la presentación: Siguiente lleva al primer paso
    assert(await page.locator('#camino-intro').isVisible());
    assert.equal(await page.locator('#camino-anterior').getAttribute('aria-disabled'), 'true');
    const colores = {};
    for (let i = 0; i < 9; i++) {
      await page.locator('#camino-siguiente').click();
      colores[PASOS[i]] = await comprobarPaso(page, i);
    }
    assert.equal(new Set(PASOS.filter(p => DE_PERSONA.has(p)).map(p => colores[p])).size, 1);
    assert(!PASOS.filter(p => !DE_PERSONA.has(p)).some(p => colores[p] === colores.aprobacion), JSON.stringify(colores));
    assert.equal(await page.locator('#camino-siguiente').getAttribute('aria-disabled'), 'true');
    await page.locator('#camino-siguiente').click({force: true});  // en el último paso, Siguiente no hace nada
    await comprobarPaso(page, 8);
    await page.locator('#camino-anterior').click();
    await comprobarPaso(page, 7);
    // El mapa de los nueve pasos también lleva a cada uno, y marca el actual.
    await page.locator('#camino-mapa button').nth(2).click();
    await comprobarPaso(page, 2);
    assert.equal(await page.locator('#camino-mapa button').nth(2).getAttribute('aria-current'), 'step');
    assert.match(await page.locator('#camino-anuncio').innerText(), /Paso 3 de 9/);
    assert.deepEqual(errores, []);
  },

  async con_el_teclado(browser) {
    const {page, errores} = await abrir(browser);
    await page.locator('#camino-visor').focus();
    for (let i = 0; i < 4; i++) await page.keyboard.press('ArrowRight');
    await comprobarPaso(page, 3);
    await page.keyboard.press('ArrowLeft');
    await comprobarPaso(page, 2);
    await page.keyboard.press('ArrowDown');
    await comprobarPaso(page, 3);
    await page.keyboard.press('ArrowUp');
    await comprobarPaso(page, 2);
    await page.keyboard.press('End');
    await comprobarPaso(page, 8);
    await page.keyboard.press('Home');
    await comprobarPaso(page, 0);
    // Las flechas también sirven con el foco en un botón del recorrido, y el foco no se pierde al llegar al final.
    await page.locator('#camino-siguiente').focus();
    for (let i = 0; i < 12; i++) await page.keyboard.press('Enter');
    await comprobarPaso(page, 8);
    assert.equal(await page.evaluate(() => document.activeElement.id), 'camino-siguiente');
    await page.keyboard.press('ArrowLeft');
    await comprobarPaso(page, 7);
    assert.deepEqual(errores, []);
  },

  async sin_javascript(browser) {
    const {page} = await abrir(browser, {sinJs: true});
    const pasos = await page.locator('#camino-pasos > li').evaluateAll(ls => ls.map(l => [l.dataset.paso, l.offsetParent !== null,
      !!l.querySelector('code') && l.querySelector('code').offsetParent !== null]));
    assert.deepEqual(pasos, PASOS.map(p => [p, true, true]));
    // Sin script no hay controles que no anden: los botones aparecen sólo con JavaScript.
    assert.equal(await page.locator('#camino-siguiente').isVisible(), false);
    assert.equal(await page.locator(`${NUEVAS.split(', ').map(s => s + ' button:not(.huevo)').join(', ')}`).evaluateAll(bs => bs.filter(b => b.offsetParent !== null).length), 0);  // los secretos de la escena ya estaban
    // Los dos estados de cada ejemplo se leen.
    for (const sel of ['#ej-romper [data-caso="sano"]', '#ej-romper [data-caso="roto"]', '#ej-sensor [data-caso="aprobado"]',
                       '#ej-sensor [data-caso="cambiado"]', '#ej-sensor [data-caso="reaprobado"]', '#mutacion-tabla']) {
      assert(await page.locator(sel).isVisible(), sel);
    }
    assert((await page.locator('#ej-romper').innerText()).includes('return bool(titulo)'));
    for (const ancho of [320, 390]) {
      await page.setViewportSize({width: ancho, height: 800});
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `desborda a ${ancho} sin JS`);
    }
  },

  async romper_el_codigo(browser) {
    const {page, errores} = await abrir(browser);
    const ej = page.locator('#ej-romper');
    const llave = page.getByRole('switch', {name: 'Romper el código'});
    assert.equal(await llave.getAttribute('aria-checked'), 'false');
    const veredicto = () => ej.locator('.veredicto:visible');
    assert.equal(await veredicto().getAttribute('data-veredicto'), 'verde');
    assert.match(await ej.locator('.archivo-codigo:visible').innerText(), /return bool\(titulo\.strip\(\)\)/);
    await llave.click();
    assert.equal(await llave.getAttribute('aria-checked'), 'true');
    assert.equal(await ej.getAttribute('data-roto'), 'si');
    assert.equal(await veredicto().getAttribute('data-veredicto'), 'rojo');
    const [r, g, b] = (await veredicto().evaluate(e => getComputedStyle(e).backgroundColor)).match(/\d+/g).map(Number);
    assert(r > g + 40 && r > b + 40, `el veredicto no se ve rojo: ${r},${g},${b}`);
    const visible = await ej.innerText();
    assert.match(visible, /return bool\(titulo\)\n/);
    assert.match(visible, /salen del commit/);
    assert.match(visible, /no del archivo escrito a mano/);
    assert.match(visible, /"caso": "espacios",\s*"codigo": 1/);
    assert(visible.includes('oracle-factory --agente claude-code evidencia ID'));
    assert(visible.includes('FACTORY BLOQUEADA: Oracle no confirmó cada requisito'));
    // El archivo a mano sigue «todo verde»: no cambia con el código.
    assert.doesNotMatch(await ej.locator('.hechos-a-mano').innerText(), /"codigo": 1/);
    assert.equal(await page.locator('[data-escena="romper"]').getAttribute('data-roto'), 'si');
    // Con el teclado vuelve a estar sano.
    await llave.focus();
    await page.keyboard.press('Space');
    assert.equal(await llave.getAttribute('aria-checked'), 'false');
    assert.equal(await veredicto().getAttribute('data-veredicto'), 'verde');
    assert.deepEqual(errores, []);
  },

  async cambiar_el_sensor(browser) {
    const {page, errores} = await abrir(browser);
    const ej = page.locator('#ej-sensor');
    const campo = page.getByRole('textbox', {name: /comando del sensor/i});
    const original = await campo.inputValue();
    assert.equal(original, '{python} examples/notas/sensor.py --salida {salida}/hechos.json');
    const estado = () => ej.locator('.estado:visible').getAttribute('data-caso');
    assert.equal(await estado(), 'aprobado');
    await campo.fill(original + ' --solo-rapidas');
    assert.equal(await estado(), 'cambiado');
    let visible = await ej.innerText();
    assert(visible.includes('FACTORY BLOQUEADA: el sensor declarado no es uno que haya aprobado una persona'), visible);
    assert(visible.includes('oracle-factory aprobar-sensor'));
    assert.match(visible, /de una persona/);
    assert.match(visible, /"--solo-rapidas"/);  // la declaración que se ve es la nueva
    // Un agente no puede aprobarlo; una persona sí.
    assert(visible.includes('es de una persona, sin --agente; claude-code puede proponerla, no tomarla'));
    await ej.getByRole('button', {name: 'Aprobarlo como persona'}).click();
    assert.equal(await estado(), 'reaprobado');
    visible = await ej.innerText();
    assert(visible.includes('Sensor aprobado por Ana Gómez. Quedó en .factory/sensor-aprobado.json.'));
    assert(visible.includes('Hechos producidos por Factory'));
    assert.match(visible, /Último sensor aprobado/);
    // Otro cambio vuelve a negarse; el original sigue aprobado.
    await campo.fill(original + ' --otra-cosa');
    assert.equal(await estado(), 'cambiado');
    await campo.fill(original);
    assert.equal(await estado(), 'aprobado');
    await campo.fill(original + ' --solo-rapidas');
    assert.equal(await estado(), 'aprobado');  // ya lo aprobó una persona
    await ej.getByRole('button', {name: 'Volver al sensor de antes'}).click();
    assert.equal(await campo.inputValue(), original);
    assert.equal(await page.locator('[data-escena="sensor"]').getAttribute('data-sensor'), 'aprobado');
    assert.deepEqual(errores, []);
  },

  async la_mutacion(browser) {
    const {page, errores} = await abrir(browser);
    const ej = page.locator('#ej-mutacion');
    const porcentaje = () => ej.locator('#mutacion-porcentaje').innerText();
    const medida = ej.locator('#mutacion-medida');
    assert.equal(await ej.locator('input[type=checkbox]:checked').count(), 5);
    assert.equal(await porcentaje(), '100%');
    assert.equal(await medida.getAttribute('data-cumple'), 'si');
    await ej.getByRole('checkbox', {name: /largo_81/}).uncheck();
    assert.equal(await porcentaje(), '80%');
    assert.equal(await medida.getAttribute('data-cumple'), 'si');  // 80 alcanza
    await ej.getByRole('checkbox', {name: /una_letra/}).uncheck();
    assert.equal(await porcentaje(), '60%');
    assert.equal(await medida.getAttribute('data-cumple'), 'no');
    assert.match(await medida.innerText(), /no se cumple/);
    assert.match(await ej.locator('.hechos-mutacion').innerText(), /"muertos": 3,\s*"porcentaje": 60/);
    assert.equal(await page.locator('[data-escena="mutacion"] .mutante.muerto').count(), 3);
    assert.equal(await page.locator('[data-escena="mutacion"] .mutante:not(.muerto)').count(), 2);
    // El módulo de pruebas que se ve es el que quedó.
    const modulo = await ej.locator('.modulo-pruebas').innerText();
    assert(!modulo.includes('test_largo_81') && modulo.includes('test_vacio'), modulo);
    // Sacar las que no suman nada no cambia el porcentaje: justo_80 no mata a ninguno que no maten las demás.
    await ej.getByRole('checkbox', {name: /justo_80/}).uncheck();
    assert.equal(await porcentaje(), '60%');
    for (const n of ['vacio', 'con_texto']) await ej.getByRole('checkbox', {name: new RegExp(n)}).uncheck();
    assert.equal(await porcentaje(), '0%');
    await ej.getByRole('checkbox', {name: /largo_81/}).check();
    assert.equal(await porcentaje(), '60%');
    assert.deepEqual(errores, []);
  },

  async copiar_un_comando(browser) {
    const {page, errores} = await abrir(browser);
    // Cada comando de las secciones nuevas tiene su botón para copiar, con un nombre que dice qué copia.
    const sinBoton = await page.locator(`${NUEVAS.split(', ').map(s => s + ' .comando').join(', ')}`).evaluateAll(cs => cs
      .filter(c => !(c.querySelector('button.copiar') && c.querySelector('button.copiar').getAttribute('aria-label').startsWith('Copiar')))
      .map(c => c.innerText));
    assert.deepEqual(sinBoton, []);
    const bloque = page.locator('#ej-romper .comando').filter({hasText: 'evidencia ID'}).first();
    const boton = bloque.locator('button.copiar');
    await boton.click();
    assert.equal(await page.evaluate(() => window.__copiado), 'oracle-factory --agente claude-code evidencia ID');
    assert.equal(await boton.innerText(), 'Copiado');
    assert.match(await page.locator('#copiado-anuncio').innerText(), /Copiado/);
    // También los tres pasos del principio, con el teclado; un comando de dos líneas se copia entero.
    const primero = page.locator('#tres-pasos .comando button.copiar').first();
    await primero.focus();
    await page.keyboard.press('Enter');
    const copiado = await page.evaluate(() => window.__copiado);
    assert.equal(copiado, await page.locator('#tres-pasos .comando code').first().innerText());
    assert(copiado.includes('\n') && copiado.includes('oracle-factory init'), copiado);
    assert.deepEqual(errores, []);
  },

  async lo_primero_que_se_ve(browser) {
    for (const ancho of [1440, 390]) {
      const {page, errores} = await abrir(browser, {ancho});
      const orden = await page.locator('main > section').evaluateAll(s => s.slice(0, 3).map(x => x.id));
      assert.deepEqual(orden, ['empezar', 'camino', 'ejemplos']);
      const [h1, frase] = await page.evaluate(() => [document.querySelector('#empezar h1').getBoundingClientRect().top,
        document.querySelector('#empezar .frase').getBoundingClientRect().bottom]);
      assert(h1 < 300 && frase < 900, `qué es Factory no entra en la primera pantalla a ${ancho}: ${h1}, ${frase}`);
      assert.equal(await page.locator('#tres-pasos > li').count(), 3);
      assert(await page.locator('#para-quien-si').isVisible() && await page.locator('#para-quien-no').isVisible());
      assert.deepEqual(errores, []);
    }
  },

  async accesible(browser) {
    for (const reducido of [false, true]) {
      const {page, errores} = await abrir(browser, {reducido});
      // Los dibujos: una imagen con su texto; el SVG de adentro no se anuncia.
      const escenas = await page.locator(`${NUEVAS.split(', ').map(s => s + ' .pixel-scene').join(', ')}`).evaluateAll(es => es.map(e => [
        e.dataset.escena, e.getAttribute('role'), (e.getAttribute('aria-label') || '').length, !!e.querySelector('svg[aria-hidden="true"] rect')]));
      assert(escenas.length >= 5, JSON.stringify(escenas));
      for (const [n, rol, largo, svg] of escenas) assert(rol === 'img' && largo > 30 && svg, n);
      // Cada control tiene nombre accesible y se alcanza con Tab.
      const controles = await page.locator(`${NUEVAS.split(', ').map(s => `${s} button, ${s} input, ${s} [tabindex="0"]`).join(', ')}`)
        .evaluateAll((es, f) => es.filter(e => e.offsetParent !== null).map(e => [e.id || e.outerHTML.slice(0, 60), new Function('return ' + f)()(e)]),
                     nombreAccesible.toString());
      assert(controles.length >= 15, JSON.stringify(controles));
      assert.deepEqual(controles.filter(([, nombre]) => !nombre), []);
      await page.locator('#empezar').evaluate(e => { e.setAttribute('tabindex', '-1'); e.focus(); });
      const alcanzados = new Set();
      for (let i = 0; i < 120; i++) {
        await page.keyboard.press('Tab');
        const [enNuevas, clave, contorno] = await page.evaluate(() => {
          const a = document.activeElement;
          return [!!a.closest('#empezar, #camino, #ejemplos'), a.id || a.outerHTML.slice(0, 60), getComputedStyle(a).outlineStyle];
        });
        if (enNuevas) { alcanzados.add(clave); assert.notEqual(contorno, 'none', `sin foco visible: ${clave}`); }
      }
      const faltan = controles.map(([c]) => c).filter(c => !alcanzados.has(c));
      assert.deepEqual(faltan, []);
      // Con «reducir movimiento», nada se anima, ni al tocar.
      await page.locator('#camino-siguiente').click();
      await page.getByRole('switch', {name: 'Romper el código'}).click();
      await page.locator('#ej-mutacion input[type=checkbox]').first().uncheck();
      await page.waitForTimeout(50);
      const animadas = await page.locator(`${NUEVAS.split(', ').map(s => s + ' .pixel-scene').join(', ')}`).evaluateAll(es => es.map(e => [e.dataset.escena,
        e.getAnimations({subtree: true}).length]));
      if (reducido) assert.deepEqual(animadas.filter(([, n]) => n), []);
      else assert(animadas.every(([, n]) => n > 0), JSON.stringify(animadas));
      // Contraste del texto de las secciones nuevas: 4.5 a 1 (3 a 1 el texto grande).
      const pares = await page.locator(`${NUEVAS}`).evaluateAll(secs => {
        const fondo = e => { for (; e; e = e.parentElement) { const c = getComputedStyle(e).backgroundColor; if (!/rgba\(.*, 0\)|transparent/.test(c)) return c; } return 'rgb(255, 255, 255)'; };
        const salida = [];
        for (const s of secs) for (const e of s.querySelectorAll('*')) {
          if (e.offsetParent === null || e.closest('svg')) continue;
          if (![...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) continue;
          const st = getComputedStyle(e);
          salida.push([e.tagName + '.' + e.className, st.color, fondo(e), parseFloat(st.fontSize), parseInt(st.fontWeight, 10)]);
        }
        return salida;
      });
      const malos = pares.filter(([, c, f, tam, peso]) => {
        const [a, b] = [c, f].map(x => luminancia(x.match(/\d+(\.\d+)?/g).slice(0, 3).map(Number)));
        const ratio = (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
        return ratio < (tam >= 24 || (tam >= 18.66 && peso >= 700) ? 3 : 4.5);
      });
      assert.deepEqual(malos, []);
      for (const ancho of [320, 390, 768]) {
        await page.setViewportSize({width: ancho, height: 900});
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false, `desborda a ${ancho}`);
      }
      assert.deepEqual(errores, []);
    }
  },

  async sin_recursos_de_afuera(browser) {
    const {page, errores, externos} = await abrir(browser);
    await page.evaluate(() => scrollTo(0, document.documentElement.scrollHeight));
    await page.waitForTimeout(300);
    assert.deepEqual(externos, []);
    const recursos = await page.evaluate(() => performance.getEntriesByType('resource').map(r => r.name).filter(n => !/^(file|data):/.test(n)));
    assert.deepEqual(recursos, []);
    assert.deepEqual(errores, []);
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
