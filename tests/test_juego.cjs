/* La máquina de estados del minijuego (site/juego.js), con node y sin navegador. */
'use strict';
const assert = require('node:assert/strict');
const J = require('../site/juego.js');

function jugar(...ids) {
  const e = J.nuevo();
  for (const id of ids) assert.equal(J.elegir(e, id), null, `«${id}» en ${e.paso}`);
  return e;
}
const quien = e => e.registro.map(r => r.quien);
const ids = e => J.opciones(e).filter(o => o.disponible).map(o => o.id);

// Una partida que cierra en verde: alcance, medidas, corrección, riesgo con motivo, aprobar, cerrar.
let e = jugar('aceptar', 'acordar', 'corregir', 'riesgo', 'motivo0', 'aprobar', 'cerrar');
assert.equal(e.oracle, 'verde');
assert.equal(e.fin, 'cerrado');
assert.equal(e.motivo, J.MOTIVOS[0]);
assert(e.registro.some(r => r.quien === 'Vos (persona)' && r.que.includes('Aceptaste el riesgo') && r.que.includes(J.MOTIVOS[0])));
assert(e.registro.every(r => r.quien !== 'Vos (persona)' || /^(Aceptaste|Acordaste|Le pediste|Aprobaste|Cerraste)/.test(r.que)));
assert(quien(e).includes('Agente (construyó)') && quien(e).includes('codex (revisor)') && quien(e).includes('Oracle'));

// Aprobar con el hallazgo abierto no está disponible, dice por qué y no cambia el estado.
e = jugar('aceptar', 'acordar', 'corregir');
assert.equal(e.paso, 'revision');
const antes = JSON.stringify(e);
assert.match(J.elegir(e, 'aprobar'), /No disponible: queda 1 hallazgo medio abierto/);
assert.equal(JSON.stringify(e), antes);
assert(!ids(e).includes('aprobar'));
J.elegir(e, 'descartar'); J.elegir(e, 'motivo1');
assert(ids(e).includes('aprobar') && !ids(e).includes('riesgo'));

// Pedir cambios también resuelve el hallazgo, y la partida puede terminar en verde.
e = jugar('aceptar', 'acordar', 'corregir', 'cambios', 'aprobar');
assert.equal(e.oracle, 'verde');

// Medidas sin acordar: sin juicio, y no se puede cerrar.
e = jugar('aceptar', 'sin', 'corregir', 'riesgo', 'motivo0', 'aprobar');
assert.equal(e.oracle, 'sin_juicio');
assert.match(J.elegir(e, 'cerrar'), /sin juicio/);
assert.match(e.registro.at(-1).que, /no tiene medidas acordadas/);
J.elegir(e, 'terminar');
assert.equal(e.fin, 'abierto');

// Sin corregir el caso que falla: rojo.
e = jugar('aceptar', 'acordar', 'seguir', 'cambios', 'aprobar');
assert.equal(e.oracle, 'rojo');
assert.match(J.elegir(e, 'cerrar'), /rojo/);

// Pedir otra propuesta: una vez; la segunda no está disponible.
e = jugar('otra');
assert.match(J.elegir(e, 'otra'), /ya ajustó/);
assert.equal(J.elegir(e, 'nada'), 'Esa opción no existe en este paso.');

// Cada paso tiene su situación y al menos una opción disponible hasta el final.
e = J.nuevo();
for (const id of ['aceptar', 'acordar', 'corregir', 'riesgo', 'motivo0', 'aprobar', 'cerrar']) {
  assert(J.situacion(e).length > 20, e.paso);
  assert(ids(e).length > 0, e.paso);
  J.elegir(e, id);
}
assert.equal(J.opciones(e).length, 0);
// Toda opción no disponible dice por qué, en cada paso de cada camino (agy-web-viva-1).
for (const camino of [['aceptar', 'acordar', 'corregir', 'riesgo', 'motivo0', 'aprobar'], ['otra', 'aceptar', 'sin', 'seguir', 'cambios', 'aprobar']]) {
  e = J.nuevo();
  for (const id of camino) {
    for (const o of J.opciones(e).filter(o => !o.disponible)) {
      assert.equal(typeof o.porque, 'string', `${e.paso}: ${o.id}`);
      assert.equal(J.elegir(e, o.id), o.porque);
    }
    J.elegir(e, id);
  }
}
console.log('juego: ok');
