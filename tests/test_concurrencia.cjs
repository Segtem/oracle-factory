/* El motor de la simulación de concurrencia (site/concurrencia.js), con node y sin navegador. Escenarios cc1–cc3. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const C = require('../site/concurrencia.js');

const IDS = ['paralelo', 'mismo-archivo', 'decisiones-distintas', 'revision-vieja', 'agente-cierra'];
const PERSONAS = new Set(['Ana', 'Beto']);

// Corre un escenario hasta el final; ante una espera elige la opción dada (o la primera) como lo haría una persona.
function correr(id, semilla, elegir) {
  const e = C.nuevo(id, semilla);
  let guardia = 0;
  while (!e.fin && guardia++ < 200) {
    if (e.espera) { assert.equal(C.elegir(e, (elegir || (o => o[0]))(e.espera.opciones.map(o => o.id), e)), null); continue; }
    C.paso(e);
  }
  assert(e.fin, `${id} no terminó`);
  return e;
}
const resultado = e => JSON.stringify({
  tronco: e.tronco.archivos, registro: e.tronco.registro, vencidas: e.registro.filter(r => r.regla === 'vencida').length,
  decisiones: e.registro.filter(r => r.decision).map(r => `${r.quien}:${r.decision}`).sort()});

// cc1: las reglas.
{
  assert.deepEqual(C.nuevo('paralelo', 1).registro, []);
  for (const id of IDS) {
    const e = correr(id, 1);
    for (const r of e.registro) {
      // toda decisión de persona la toma una persona; un agente sólo propone
      if (r.decision) assert(PERSONAS.has(r.quien), `${id}: «${r.decision}» decidida por ${r.quien}`);
      assert(r.tipo === 'persona' || r.tipo === 'agente' || r.tipo === 'git' || r.tipo === 'oracle', r.tipo);
      if (r.regla) assert(C.REGLAS.some(x => x.id === r.regla), `regla desconocida ${r.regla}`);
    }
  }
  // un agente intenta cerrar: no se ejecuta, queda como propuesta y el registro lo dice con su nombre
  const e = correr('agente-cierra', 1);
  const intento = e.registro.find(r => r.tipo === 'agente' && r.regla === 'persona');
  assert(intento && intento.quien === 'claude-code' && /propuso|propone/.test(intento.que), JSON.stringify(intento));
  assert(!e.registro.some(r => r.tipo === 'agente' && r.decision), 'un agente decidió');
  assert.equal(e.pendientes.length, 1);
  assert.equal(e.pendientes[0].quien, 'claude-code');
  assert(e.registro.some(r => r.decision === 'cerrar' && r.quien === 'Ana' && r.tipo === 'persona'));
  // dos ramas con los mismos archivos sin pisarse: los eventos de las dos quedan
  const p = correr('paralelo', 1);
  assert.equal(p.conflictos.length, 0);
  assert(p.tronco.eventos.some(x => x.rama === 'ana') && p.tronco.eventos.some(x => x.rama === 'beto'));
  // el mismo archivo editado por dos es un conflicto, y no se resuelve solo
  const m = C.nuevo('mismo-archivo', 1);
  let paradas = 0;
  while (!m.fin) {
    if (m.espera) { paradas++; assert.equal(m.espera.tipo, 'conflicto'); assert.equal(m.espera.quien, 'persona'); const n = m.registro.length;
      C.paso(m); assert.equal(m.registro.length, n, 'el avance siguió sin que una persona eligiera');
      assert.equal(C.elegir(m, 'agente-elige'), 'Esa opción no existe en este paso.'); assert(m.espera);
      assert.equal(C.elegir(m, m.espera.opciones[0].id), null); continue; }
    C.paso(m);
  }
  assert.equal(paradas, 1);
  assert.equal(m.conflictos.length, 1);
  assert.equal(m.conflictos[0].resuelto_por, 'Beto'); // quien integra es quien resuelve
  // lo decidido distinto por dos ramas no lo elige el motor: decidir-union, de una persona
  const d = C.nuevo('decisiones-distintas', 1);
  while (!d.fin && !d.espera) C.paso(d);
  assert.equal(d.espera.tipo, 'union');
  assert(d.espera.comando.startsWith('oracle-factory decidir-union'));
  assert.equal(C.elegir(d, d.espera.opciones[0].id), null);
  assert(d.registro.some(r => r.decision === 'decidir-union' && PERSONAS.has(r.quien)));
  // lo que elige la persona cambia el resultado: en la unión, nuestro (la rama que integra) o suyo (main)
  for (const [op, quien] of [['nuestro', 'Beto'], ['suyo', 'Ana']]) {
    const u = correr('decisiones-distintas', 1, () => op);
    assert.equal(u.tronco.registro.informe.responsable.por, quien, op);
  }
  // y en el conflicto: main, la rama o una mezcla
  for (const [op, version] of [['main', 'ana#1'], ['rama', 'beto#1'], ['mezclar', 'mezcla']]) {
    const c = correr('mismo-archivo', 1, () => op);
    assert.equal(c.tronco.archivos['lista.py'], version, op);
    assert.equal(c.conflictos[0].como, op);
  }
  // una revisión pierde su vigencia si el producto cambió después de hacerla
  const v = correr('revision-vieja', 1);
  const vencida = v.registro.find(r => r.regla === 'vencida');
  assert(vencida, 'la revisión no quedó vieja');
  const idx = v.registro.indexOf(vencida);
  assert(v.registro.slice(0, idx).some(r => r.decision === 'revisar'), 'se venció sin haber sido hecha');
  assert(v.registro.slice(idx + 1).some(r => r.decision === 'revisar'), 'no se pidió la revisión de nuevo');
  assert(!v.registro.slice(idx + 1).some(r => r.decision === 'cerrar' && v.registro.indexOf(r) < v.registro.lastIndexOf(v.registro.filter(x => x.decision === 'revisar').pop())), 'se cerró con la revisión vencida');
}

// cc1 (ronda 1, CC-1 y CC-2): cerrar exige una revisión vigente; los eventos de dos ramas no se pisan por tener el mismo nombre.
{
  const con = (...guion) => { const e = C.nuevo('paralelo', 1); e.guion = guion; e.idx = 0; e.fin = null;
    while (!e.fin) { if (e.espera) C.elegir(e, e.espera.opciones[0].id); else C.paso(e); } return e; };
  const ed = (quien, archivo, cambio) => ({a: 'editar', quien, archivo, cambio});
  const de = (quien, decision, cambio, rama) => ({a: 'decidir', quien, decision, cambio, rama});
  const cerro = e => e.registro.some(r => r.decision === 'cerrar');
  // nunca revisado: no se cierra, y el registro lo dice
  let e = con(ed('claude-code', 'x.py', 'x'), de('Ana', 'cerrar', 'x', 'ana'));
  assert(!cerro(e));
  assert(e.registro.some(r => r.regla === 'vencida' && r.tipo === 'oracle' && /No se puede cerrar «x»/.test(r.que)), JSON.stringify(e.registro));
  assert.equal(e.tronco.registro.x, undefined);
  // revisado, pero el producto cambió después: la revisión venció y tampoco se cierra
  e = con(ed('claude-code', 'x.py', 'x'), de('Beto', 'revisar', 'x', 'ana'), ed('claude-code', 'y.py', 'x'), de('Ana', 'cerrar', 'x', 'ana'));
  assert(!cerro(e));
  assert(e.registro.some(r => /No se puede cerrar «x»/.test(r.que) && /vieja|venció|ya no vale/.test(r.que)));
  // revisado de nuevo después del cambio: se cierra
  e = con(ed('claude-code', 'x.py', 'x'), de('Beto', 'revisar', 'x', 'ana'), ed('claude-code', 'y.py', 'x'), de('Beto', 'revisar', 'x', 'ana'), de('Ana', 'cerrar', 'x', 'ana'));
  assert(cerro(e));
  // un agente que propone cerrar sigue sin cerrar, aunque haya revisión
  e = con(ed('claude-code', 'x.py', 'x'), de('Beto', 'revisar', 'x', 'ana'), de('claude-code', 'cerrar', 'x', 'ana'));
  assert(!cerro(e));
  // CC-3 y CC-4: un agente sólo edita y trae main; todo lo demás (tomar, decidir, integrar) lo propone, y nada cambia
  for (const accion of [{a: 'tomar', quien: 'claude-code', rama: 'ana', cambio: 'x'}, {a: 'integrar', quien: 'codex', rama: 'beto'},
                        {a: 'decidir', quien: 'codex', decision: 'revisar', cambio: 'x', rama: 'beto'}, {a: 'decidir', quien: 'claude-code', decision: 'aprobar-spec', cambio: 'x', rama: 'ana'}]) {
    const antes = con(ed('claude-code', 'x.py', 'x'));
    const x = con(ed('claude-code', 'x.py', 'x'), accion);
    assert.equal(JSON.stringify(x.tronco), JSON.stringify(antes.tronco), JSON.stringify(accion) + ': cambió main');
    assert.equal(JSON.stringify(x.ramas.ana.registro) + JSON.stringify(x.ramas.beto.registro) + JSON.stringify(x.ramas.ana.revisiones) + JSON.stringify(x.ramas.beto.revisiones),
                 '{}{}{}{}', JSON.stringify(accion) + ': cambió un registro');
    assert(x.registro.some(r => r.tipo === 'agente' && r.regla === 'persona' && r.quien === accion.quien && /sólo lo propuso/.test(r.que)), JSON.stringify(accion));
    assert.equal(x.pendientes.length, 1);
    assert(!x.registro.some(r => r.decision || /integra «|toma el cambio/.test(r.que)), JSON.stringify(accion) + ': se ejecutó');
  }
  // un agente puede traer main a su rama (es trabajo de desarrollo)
  e = con(ed('codex', 'p.py', 'p'), {a: 'integrar', quien: 'Beto', rama: 'beto'}, {a: 'traer', quien: 'claude-code', rama: 'ana'});
  assert(e.registro.some(r => r.quien === 'claude-code' && /trae main/.test(r.que)));
  // dos ramas que registran la misma decisión del mismo cambio: los dos eventos llegan a main
  e = con(de('Ana', 'revisar', 'informe', 'ana'), de('Beto', 'revisar', 'informe', 'beto'),
          {a: 'integrar', quien: 'Ana', rama: 'ana'}, {a: 'integrar', quien: 'Beto', rama: 'beto'});
  const revisares = e.tronco.eventos.filter(x => x.cambio === 'informe' && x.que === 'revisar');
  assert.deepEqual(revisares.map(x => x.rama).sort(), ['ana', 'beto'], JSON.stringify(e.tronco.eventos));
  assert.equal(new Set(e.tronco.eventos.map(x => x.id)).size, e.tronco.eventos.length, 'ids repetidos');
  // la misma decisión dos veces en una rama: los dos eventos
  e = con(ed('claude-code', 'x.py', 'x'), de('Beto', 'revisar', 'x', 'ana'), ed('claude-code', 'y.py', 'x'), de('Beto', 'revisar', 'x', 'ana'), {a: 'integrar', quien: 'Ana', rama: 'ana'});
  assert.equal(e.tronco.eventos.filter(x => x.que === 'revisar').length, 2);
  assert.equal(new Set(e.tronco.eventos.map(x => x.id)).size, e.tronco.eventos.length, 'ids repetidos en una misma rama');
}

// cc2: los escenarios.
{
  assert.deepEqual(C.ESCENARIOS.map(x => x.id), IDS);
  for (const x of C.ESCENARIOS) assert(x.titulo && x.resumen && x.final && x.final.length < 220, x.id);
  for (const id of IDS) {
    const e = correr(id, 3);
    assert.equal(e.fin.explicacion, C.ESCENARIOS.find(x => x.id === id).final);
    assert(e.registro.length >= 4);
    assert(e.registro.every((r, i) => r.n === i + 1 && r.quien && r.que));
  }
  assert.throws(() => C.nuevo('no-existe', 1), /escenario/);
}

// cc3: determinismo.
{
  for (const id of IDS) {
    assert.equal(JSON.stringify(correr(id, 7).registro), JSON.stringify(correr(id, 7).registro), `${id} no es determinista`);
    const base = resultado(correr(id, 1));
    for (let s = 2; s <= 30; s++) assert.equal(resultado(correr(id, s)), base, `${id}: el resultado cambia con la semilla ${s}`);
  }
  const ordenes = new Set();
  for (let s = 1; s <= 30; s++) ordenes.add(JSON.stringify(correr('paralelo', s).registro.map(r => r.que)));
  assert(ordenes.size > 1, 'la semilla no cambia el orden de lo simultáneo');
}

// citas: cada regla cita un texto que está en docs/colaboracion.md
{
  const doc = fs.readFileSync(path.join(__dirname, '../docs/colaboracion.md'), 'utf8');
  assert(C.REGLAS.length >= 6);
  for (const r of C.REGLAS) assert(r.id && r.texto && r.cita && doc.includes(r.cita), `la cita de «${r.id}» no está en docs/colaboracion.md`);
}
console.log('ok');
