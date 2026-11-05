/* El motor de la simulación de concurrencia: dos personas, dos agentes y un producto. Es una SIMULACIÓN de las reglas de
   docs/colaboracion.md, no ejecuta Factory ni Git. Puro y determinista: sin reloj ni Math.random; la semilla fija sólo el
   orden de lo que pasa a la vez. Se prueba con node (tests/test_concurrencia.cjs) y lo dibuja la página (concurrencia.html). */
(function (raiz, fabrica) {
  'use strict';
  if (typeof module === 'object' && module.exports) module.exports = fabrica();
  else raiz.Concurrencia = fabrica();
})(this, function () {
  'use strict';

  var ACTORES = {
    Ana: {tipo: 'persona', rama: 'ana'}, 'claude-code': {tipo: 'agente', de: 'Ana', rama: 'ana'},
    Beto: {tipo: 'persona', rama: 'beto'}, codex: {tipo: 'agente', de: 'Beto', rama: 'beto'}
  };
  // Cada regla cita el texto de docs/colaboracion.md que la respalda (una prueba comprueba que la cita exista).
  var REGLAS = [
    {id: 'checkout', texto: 'Cada frente tiene su persona responsable y su propio checkout: dos frentes no comparten carpeta ni rama.',
     cita: 'cada frente tiene una persona responsable, un escritor activo y su propio checkout'},
    {id: 'persona', texto: 'Un agente sólo propone: aprobar, confirmar medidas, revisar y cerrar son decisiones de una persona.',
     cita: 'un agente que actúa con `--agente NOMBRE` sólo propone'},
    {id: 'union', texto: 'Al integrar, los registros de las dos ramas se unen: quedan los eventos de las dos.',
     cita: 'quedan los eventos de las dos y lo que cambió una sola'},
    {id: 'distinto', texto: 'Lo que dos ramas decidieron distinto no lo elige Factory: lo resuelve una persona con decidir-union.',
     cita: 'no lo elige Factory'},
    {id: 'conflicto', texto: 'Un archivo de producto editado por las dos ramas es un conflicto: lo resuelve una persona, no un agente.',
     cita: 'Conflicto textual e incompatibilidad sin conflicto'},
    {id: 'vencida', texto: 'Una revisión o un juicio no valen sobre un producto que cambió desde que se hicieron.',
     cita: 'ninguna revisión o juicio figure vigente sobre un producto que cambió desde que se hizo'}
  ];

  // Los guiones: cada paso lo ejecuta el motor, que decide qué pasa según las reglas. «junto» agrupa lo que ocurre a la vez.
  function e_(quien, archivo, cambio, junto) { return {a: 'editar', quien: quien, archivo: archivo, cambio: cambio, junto: junto}; }
  function d_(quien, decision, cambio, rama, junto) { return {a: 'decidir', quien: quien, decision: decision, cambio: cambio, rama: rama, junto: junto}; }
  var GUIONES = {
    paralelo: [
      e_('claude-code', 'consulta.py', 'consulta', 'g1'), e_('codex', 'pantalla.py', 'pantalla', 'g1'),
      d_('Beto', 'revisar', 'consulta', 'ana'), d_('Ana', 'cerrar', 'consulta', 'ana'),
      {a: 'integrar', quien: 'Ana', rama: 'ana'}, {a: 'traer', quien: 'Beto', rama: 'beto'},
      d_('Ana', 'revisar', 'pantalla', 'beto'), d_('Beto', 'cerrar', 'pantalla', 'beto'),
      {a: 'integrar', quien: 'Beto', rama: 'beto'}],
    'mismo-archivo': [
      e_('claude-code', 'lista.py', 'consulta', 'g1'), e_('codex', 'lista.py', 'pantalla', 'g1'),
      d_('Beto', 'revisar', 'consulta', 'ana', 'g2'), d_('Ana', 'revisar', 'pantalla', 'beto', 'g2'),
      d_('Ana', 'cerrar', 'consulta', 'ana'), {a: 'integrar', quien: 'Ana', rama: 'ana'},
      d_('Beto', 'cerrar', 'pantalla', 'beto'), {a: 'integrar', quien: 'Beto', rama: 'beto'}],
    'decisiones-distintas': [
      {a: 'tomar', quien: 'Ana', cambio: 'informe', rama: 'ana', junto: 'g1'}, {a: 'tomar', quien: 'Beto', cambio: 'informe', rama: 'beto', junto: 'g1'},
      {a: 'integrar', quien: 'Ana', rama: 'ana'}, {a: 'integrar', quien: 'Beto', rama: 'beto'}],
    'revision-vieja': [
      e_('claude-code', 'consulta.py', 'consulta'), d_('Beto', 'revisar', 'consulta', 'ana'),
      e_('codex', 'pantalla.py', 'pantalla'), d_('Ana', 'revisar', 'pantalla', 'beto'), d_('Beto', 'cerrar', 'pantalla', 'beto'),
      {a: 'integrar', quien: 'Beto', rama: 'beto'},
      {a: 'traer', quien: 'Ana', rama: 'ana'}, d_('Beto', 'revisar', 'consulta', 'ana'),
      d_('Ana', 'cerrar', 'consulta', 'ana'), {a: 'integrar', quien: 'Ana', rama: 'ana'}],
    'agente-cierra': [
      e_('claude-code', 'consulta.py', 'consulta'), d_('Beto', 'revisar', 'consulta', 'ana'),
      d_('claude-code', 'cerrar', 'consulta', 'ana'), d_('Ana', 'cerrar', 'consulta', 'ana'),
      {a: 'integrar', quien: 'Ana', rama: 'ana'}]
  };

  var ESCENARIOS = [
    {id: 'paralelo', titulo: 'Dos frentes en paralelo', resumen: 'Ana y Beto trabajan a la vez en frentes distintos, cada uno en su rama.',
     final: 'Cada frente se revisó y se cerró por separado, los registros se unieron solos y main tiene el trabajo de los dos.'},
    {id: 'mismo-archivo', titulo: 'El mismo archivo, dos manos', resumen: 'Los dos agentes editan lista.py sin saberlo.',
     final: 'Git no puede elegir entre dos versiones de lista.py: el conflicto lo resolvió una persona, Oracle volvió a juzgar y la revisión de la rama quedó vieja.'},
    {id: 'decisiones-distintas', titulo: 'Dos ramas, dos decisiones', resumen: 'Las dos personas tomaron el mismo cambio como responsables.',
     final: 'Factory no elige quién es el responsable: lo decidió una persona con decidir-union y quedó en el registro.'},
    {id: 'revision-vieja', titulo: 'Una revisión que queda vieja', resumen: 'Beto revisó el cambio de Ana, y después Beto integró el suyo.',
     final: 'La revisión no valía sobre el producto nuevo: se pidió otra antes de cerrar y de integrar.'},
    {id: 'agente-cierra', titulo: 'El agente quiere cerrar', resumen: 'El agente de Ana intenta cerrar el cambio por su cuenta.',
     final: 'El agente sólo pudo proponer el cierre; lo cerró Ana y el registro dice quién fue cada uno.'}
  ];

  function azar(semilla) { // mulberry32
    var a = semilla >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      var t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  // Lo simultáneo se ordena con la semilla: el mismo resultado, otro orden en el registro.
  function ordenar(guion, semilla) {
    var rnd = azar(semilla), salida = [], i = 0;
    while (i < guion.length) {
      var j = i;
      while (j < guion.length && guion[j].junto && guion[j].junto === guion[i].junto) j++;
      var grupo = guion.slice(i, Math.max(j, i + 1));
      for (var k = grupo.length - 1; k > 0; k--) {
        var m = Math.floor(rnd() * (k + 1)), t = grupo[k]; grupo[k] = grupo[m]; grupo[m] = t;
      }
      salida = salida.concat(grupo);
      i += grupo.length;
    }
    return salida;
  }

  function copia(o) { return JSON.parse(JSON.stringify(o)); }
  function huella(archivos) {
    return Object.keys(archivos).sort().map(function (f) { return f + '@' + archivos[f]; }).join(' ');
  }
  function nuevo(id, semilla) {
    var esc = ESCENARIOS.filter(function (x) { return x.id === id; })[0];
    if (!esc) throw new Error('escenario desconocido: ' + id);
    var base = {'app.py': 'base'};
    function rama(actor) { return {actor: actor, base: copia(base), archivos: copia(base), registro: {}, eventos: [], revisiones: {}}; }
    return {
      escenario: id, semilla: semilla | 0, idx: 0, guion: ordenar(GUIONES[id], semilla | 0),
      tronco: {archivos: copia(base), registro: {}, eventos: []},
      ramas: {ana: rama('Ana'), beto: rama('Beto')},
      registro: [], pendientes: [], conflictos: [], resueltos: {}, espera: null, fin: null
    };
  }

  function anotar(e, quien, que, extra) {
    var r = {n: e.registro.length + 1, quien: quien, tipo: ACTORES[quien] ? ACTORES[quien].tipo : (quien === 'Git' ? 'git' : 'oracle'), que: que};
    for (var k in extra || {}) r[k] = extra[k];
    e.registro.push(r);
    return r;
  }
  function vigencias(e, ramaId) {
    var r = e.ramas[ramaId], h = huella(r.archivos);
    Object.keys(r.revisiones).forEach(function (c) {
      var v = r.revisiones[c];
      if (v.vigente && v.candidato !== h) {
        v.vigente = false;
        anotar(e, 'Factory', 'La revisión de «' + c + '» ya no vale: el producto de «' + ramaId + '» cambió desde que se hizo. Hay que revisar de nuevo.',
               {regla: 'vencida', rama: ramaId, cambio: c});
      }
    });
  }
  // Un evento del registro de una rama. El id lleva la rama y el número de orden dentro de ella: dos ramas que registran la misma
  // decisión del mismo cambio dejan dos eventos, y un evento ya integrado no se duplica si la rama se une otra vez.
  function evento(r, rama, cambio, que, quien) {
    r.eventos.push({id: rama + '-' + (r.eventos.length + 1), rama: rama, cambio: cambio, que: que, quien: quien});
  }
  function cambiados(r) { return Object.keys(r.archivos).filter(function (f) { return r.archivos[f] !== r.base[f]; }); }
  function choca(e, r, f) { return e.tronco.archivos[f] !== r.base[f] && e.tronco.archivos[f] !== r.archivos[f]; }

  // Ejecuta un paso del guion. Devuelve false si queda esperando a una persona.
  function ejecutar(e, p) {
    var yo = ACTORES[p.quien], r = e.ramas[p.rama || yo.rama];
    if (p.a === 'editar') {
      r = e.ramas[yo.rama];
      var veces = r.archivos[p.archivo] && r.archivos[p.archivo].indexOf(yo.rama + '#') === 0 ? +r.archivos[p.archivo].split('#')[1] : 0;
      r.archivos[p.archivo] = yo.rama + '#' + (veces + 1); // la versión sale de la rama, no del orden en que ocurren las cosas
      evento(r, yo.rama, p.cambio, 'editar', p.quien);
      anotar(e, p.quien, p.quien + ' edita ' + p.archivo + ' en su rama «' + yo.rama + '», en su propio checkout.', {regla: 'checkout', rama: yo.rama});
      vigencias(e, yo.rama);
    } else if (p.a === 'tomar') {
      r.registro[p.cambio] = r.registro[p.cambio] || {};
      r.registro[p.cambio].responsable = {valor: p.quien, por: p.quien};
      evento(r, p.rama, p.cambio, 'tomar', p.quien);
      anotar(e, p.quien, p.quien + ' toma el cambio «' + p.cambio + '» como responsable, en su rama «' + p.rama + '».', {rama: p.rama, cambio: p.cambio});
    } else if (p.a === 'decidir') {
      if (yo.tipo === 'agente') {
        anotar(e, p.quien, p.quien + ' intentó «' + p.decision + '» el cambio «' + p.cambio + '»: es una decisión de persona, así que sólo lo propuso.',
               {regla: 'persona', intento: p.decision, cambio: p.cambio});
        e.pendientes.push({quien: p.quien, decision: p.decision, cambio: p.cambio, para: ACTORES[p.quien].de});
      } else if (p.decision === 'cerrar' && !(r.revisiones[p.cambio] && r.revisiones[p.cambio].vigente)) {
        // no se cierra sin una revisión que valga sobre el producto actual (regla «vencida»)
        anotar(e, 'Factory', 'No se puede cerrar «' + p.cambio + '»: ' + (r.revisiones[p.cambio]
               ? 'la revisión ya no vale, el producto cambió desde que se hizo. Hay que revisar de nuevo.' : 'no hay una revisión. Falta revisarlo.'),
               {regla: 'vencida', cambio: p.cambio, rama: p.rama});
      } else {
        r.registro[p.cambio] = r.registro[p.cambio] || {};
        r.registro[p.cambio][p.decision] = {valor: p.decision, por: p.quien};
        evento(r, p.rama, p.cambio, p.decision, p.quien);
        if (p.decision === 'revisar') r.revisiones[p.cambio] = {candidato: huella(r.archivos), por: p.quien, vigente: true};
        e.pendientes.forEach(function (x) { if (x.decision === p.decision && x.cambio === p.cambio && !x.resuelta_por) x.resuelta_por = p.quien; });
        anotar(e, p.quien, p.quien + ' decide «' + p.decision + '» del cambio «' + p.cambio + '»' +
               (p.decision === 'revisar' ? ' sobre el producto de «' + p.rama + '».' : '.'), {decision: p.decision, cambio: p.cambio, rama: p.rama});
      }
    } else if (p.a === 'traer' || p.a === 'integrar') {
      return unir(e, p, r);
    }
    return true;
  }

  function unir(e, p, r) {
    var integra = p.a === 'integrar', t = e.tronco;
    var archivos = cambiados(r);
    for (var i = 0; i < archivos.length; i++) {
      var f = archivos[i];
      if (choca(e, r, f) && !e.resueltos['c:' + e.idx + ':' + f]) {
        e.espera = {tipo: 'conflicto', quien: 'persona', persona: p.quien, archivo: f, regla: 'conflicto',
          texto: 'Conflicto en ' + f + ': las dos ramas lo cambiaron. Un agente no lo resuelve; elige ' + p.quien + '.',
          opciones: [{id: 'main', texto: 'Quedarse con lo de main'}, {id: 'rama', texto: 'Quedarse con lo de la rama'}, {id: 'mezclar', texto: 'Mezclar a mano las dos'}]};
        anotar(e, 'Git', 'Conflicto en ' + f + ' al ' + (integra ? 'integrar «' + p.rama + '» en main' : 'traer main a «' + p.rama + '»') + ': las dos ramas lo cambiaron.',
               {regla: 'conflicto', archivo: f});
        return false;
      }
    }
    var uniones = [];
    if (integra) {
      Object.keys(r.registro).forEach(function (c) {
        Object.keys(r.registro[c]).forEach(function (campo) {
          var mio = r.registro[c][campo], suyo = (t.registro[c] || {})[campo];
          if (suyo && (suyo.valor !== mio.valor || suyo.por !== mio.por)) uniones.push({cambio: c, campo: campo, mio: mio, suyo: suyo});
        });
      });
      for (var j = 0; j < uniones.length; j++) {
        var u = uniones[j];
        if (!e.resueltos['u:' + e.idx + ':' + u.cambio + ':' + u.campo]) {
          e.espera = {tipo: 'union', quien: 'persona', persona: p.quien, cambio: u.cambio, campo: u.campo, regla: 'distinto',
            comando: 'oracle-factory decidir-union ID ' + u.campo + ' nuestro|suyo',
            texto: 'Las dos ramas decidieron distinto el campo «' + u.campo + '» de «' + u.cambio + '»: ' + u.mio.por + ' en la rama, ' + u.suyo.por +
                   ' en main. Factory no elige; decide ' + p.quien + '.',
            opciones: [{id: 'nuestro', texto: 'Vale lo de la rama (' + u.mio.por + ')'}, {id: 'suyo', texto: 'Vale lo de main (' + u.suyo.por + ')'}]};
          anotar(e, 'Factory', 'Al unir los registros, «' + u.campo + '» de «' + u.cambio + '» quedó distinto en las dos ramas.', {regla: 'distinto', cambio: u.cambio});
          return false;
        }
      }
    }
    var movido = Object.keys(t.archivos).some(function (f) { return t.archivos[f] !== r.base[f]; });
    if (integra) {
      archivos.forEach(function (f) {
        var res = e.resueltos['c:' + e.idx + ':' + f];
        if (!choca(e, r, f) || res === 'rama') t.archivos[f] = r.archivos[f];
        else if (res === 'mezclar') t.archivos[f] = 'mezcla';
      });
      r.archivos = copia(t.archivos);
      Object.keys(r.registro).forEach(function (c) {
        t.registro[c] = t.registro[c] || {};
        Object.keys(r.registro[c]).forEach(function (campo) {
          var res = e.resueltos['u:' + e.idx + ':' + c + ':' + campo];
          if (!t.registro[c][campo] || res === 'nuestro') t.registro[c][campo] = r.registro[c][campo];
        });
      });
      var vistos = {};
      t.eventos.forEach(function (x) { vistos[x.id] = true; });
      r.eventos.forEach(function (x) { if (!vistos[x.id]) t.eventos.push(x); });
      r.base = copia(t.archivos);
      anotar(e, p.quien, p.quien + ' integra «' + p.rama + '» en main: ' + (movido ? 'main se había movido, se unió con lo nuevo.' : 'main no se había movido.') +
             ' Los eventos de las dos ramas quedan en el registro.', {regla: 'union', rama: p.rama});
      if (movido) anotar(e, 'Oracle', 'Oracle juzga de nuevo sobre el producto integrado, no sobre el de la rama.', {rama: p.rama});
      vigencias(e, p.rama);
    } else {
      archivos.forEach(function (f) {
        var res = e.resueltos['c:' + e.idx + ':' + f];
        if (choca(e, r, f) && res === 'main') r.archivos[f] = t.archivos[f];
      });
      Object.keys(t.archivos).forEach(function (f) { if (!choca(e, r, f) && r.archivos[f] === r.base[f]) r.archivos[f] = t.archivos[f]; });
      Object.keys(t.archivos).forEach(function (f) { if (r.archivos[f] === undefined) r.archivos[f] = t.archivos[f]; });
      r.base = copia(t.archivos);
      anotar(e, p.quien, p.quien + ' trae main a «' + p.rama + '» antes de seguir.', {regla: 'union', rama: p.rama});
      vigencias(e, p.rama);
    }
    return true;
  }

  function avanzar(e) {
    e.idx++;
    if (e.idx >= e.guion.length) {
      e.fin = {explicacion: ESCENARIOS.filter(function (x) { return x.id === e.escenario; })[0].final};
    }
  }
  function paso(e) {
    if (e.fin || e.espera) return;
    if (ejecutar(e, e.guion[e.idx]) !== false) avanzar(e);
  }
  // La persona resuelve una espera (conflicto o unión). Cualquier otra opción no existe.
  function elegir(e, id) {
    if (!e.espera) return 'No hay nada que decidir ahora.';
    var o = e.espera.opciones.filter(function (x) { return x.id === id; })[0];
    if (!o) return 'Esa opción no existe en este paso.';
    var w = e.espera, p = e.guion[e.idx];
    if (w.tipo === 'conflicto') {
      e.resueltos['c:' + e.idx + ':' + w.archivo] = id;
      e.conflictos.push({archivo: w.archivo, resuelto_por: w.persona, como: id});
      anotar(e, w.persona, w.persona + ' resuelve el conflicto en ' + w.archivo + ': ' + o.texto.toLowerCase() + '.', {decision: 'resolver-conflicto', regla: 'conflicto'});
    } else {
      e.resueltos['u:' + e.idx + ':' + w.cambio + ':' + w.campo] = id;
      anotar(e, w.persona, w.persona + ' decide la unión de «' + w.campo + '»: ' + o.texto.toLowerCase() + '.', {decision: 'decidir-union', regla: 'distinto'});
    }
    e.espera = null;
    if (ejecutar(e, p) !== false) avanzar(e);
    return null;
  }

  return {ACTORES: ACTORES, REGLAS: REGLAS, ESCENARIOS: ESCENARIOS, nuevo: nuevo, paso: paso, elegir: elegir};
});
