/* El minijuego de decisiones: una máquina de estados pura, sin DOM, con las reglas de la CLI de Factory.
   Quien juega es la persona; el agente propone y construye, codex revisa y Oracle juzga. viva.js la dibuja. */
(function (raiz) {
  'use strict';

  var MOTIVOS = [
    'El mensaje de error se mejora en otro cambio; hoy no confunde a nadie.',
    'Es un detalle de estilo y el pedido no lo incluye.'
  ];

  function nuevo() {
    return {paso: 'pedido', propuestas: 1, medidas: null, corregido: null, hallazgo: 'abierto', motivo: null,
            revision: null, oracle: null, registro: [], fin: null};
  }

  function anotar(e, quien, que) {
    e.registro.push({quien: quien, que: que});
  }

  // Lo que la persona puede elegir ahora: [{id, texto, disponible, porque}].
  function opciones(e) {
    switch (e.paso) {
      case 'pedido':
        return [{id: 'aceptar', texto: 'Aceptar esta spec', disponible: true},
                {id: 'otra', texto: 'Pedir otra propuesta', disponible: e.propuestas < 2,
                 porque: e.propuestas < 2 ? null : 'El agente ya ajustó la propuesta: aceptala o volvé a empezar.'}];
      case 'medidas':
        return [{id: 'acordar', texto: 'Acordar las medidas', disponible: true},
                {id: 'sin', texto: 'Dejarlas sin acordar', disponible: true}];
      case 'pruebas':
        return [{id: 'corregir', texto: 'Pedirle al agente que lo corrija', disponible: true},
                {id: 'seguir', texto: 'Seguir igual', disponible: true}];
      case 'revision':
        var abierto = e.hallazgo === 'abierto';
        return [{id: 'aprobar', texto: 'Aprobar', disponible: !abierto,
                 porque: abierto ? 'No disponible: queda 1 hallazgo medio abierto. Aceptalo como riesgo, descartalo o pedí la corrección.' : null},
                {id: 'riesgo', texto: 'Aceptar el riesgo', disponible: abierto},
                {id: 'descartar', texto: 'Descartar el hallazgo', disponible: abierto},
                {id: 'cambios', texto: 'Pedir cambios', disponible: true}];
      case 'motivo':
        return MOTIVOS.map(function (m, i) { return {id: 'motivo' + i, texto: m, disponible: true}; });
      case 'cierre':
        var verde = e.oracle === 'verde';
        return [{id: 'cerrar', texto: 'Cerrar el cambio', disponible: verde,
                 porque: verde ? null : (e.oracle === 'rojo' ? 'No disponible: Oracle dio rojo.'
                                                             : 'No disponible: el requisito quedó sin juicio.')},
                {id: 'terminar', texto: 'Ver el registro', disponible: true}];
      default:
        return [];
    }
  }

  function juzgar(e) {
    if (!e.medidas) {
      e.oracle = 'sin_juicio';
      anotar(e, 'Oracle', 'Sin juicio: el requisito no tiene medidas acordadas, así que no hay contra qué comparar.');
    } else if (!e.corregido) {
      e.oracle = 'rojo';
      anotar(e, 'Oracle', 'Rojo: notas.resultados encontró 1 caso que falla (un título de sólo espacios se guarda).');
    } else {
      e.oracle = 'verde';
      anotar(e, 'Oracle', 'Verde: los 3 casos se ejecutaron y pasaron, con las medidas que acordaste.');
    }
    e.paso = 'cierre';
  }

  // Aplica la elección de la persona; una opción no disponible no cambia nada y devuelve su porqué.
  function elegir(e, id) {
    var o = opciones(e).filter(function (x) { return x.id === id; })[0];
    if (!o) return 'Esa opción no existe en este paso.';
    if (!o.disponible) return o.porque;
    switch (e.paso) {
      case 'pedido':
        if (id === 'otra') {
          e.propuestas += 1;
          anotar(e, 'Agente (propuso)', 'Rehízo la propuesta: también rechaza títulos de sólo espacios.');
          return null;
        }
        anotar(e, 'Vos (persona)', 'Aceptaste el alcance: ninguna nota se guarda con el título vacío.');
        e.paso = 'medidas';
        return null;
      case 'medidas':
        e.medidas = id === 'acordar';
        anotar(e, 'Vos (persona)', e.medidas ? 'Acordaste las medidas que propuso el agente: notas.casos_ejecutados y notas.resultados.'
                                            : 'Dejaste las medidas sin acordar.');
        anotar(e, 'Agente (construyó)', 'Escribió el validador y sus pruebas.');
        e.paso = 'pruebas';
        return null;
      case 'pruebas':
        e.corregido = id === 'corregir';
        anotar(e, 'Vos (persona)', e.corregido ? 'Le pediste al agente que corrija el caso de sólo espacios; lo corrigió.'
                                              : 'Seguiste con el caso de sólo espacios sin corregir.');
        anotar(e, 'codex (revisor)', 'Hallazgo medio: el mensaje de error no dice qué campo falta.');
        e.paso = 'revision';
        return null;
      case 'revision':
        if (id === 'riesgo' || id === 'descartar') {
          e.hallazgo = id === 'riesgo' ? 'riesgo' : 'descartado';
          e.paso = 'motivo';
          return null;
        }
        if (id === 'cambios') {
          anotar(e, 'Vos (persona)', 'Pediste cambios: el agente mejoró el mensaje y agy no encontró nada en otra vuelta.');
          e.hallazgo = 'corregido';
          return null;
        }
        e.revision = 'aprobada';
        anotar(e, 'Vos (persona)', 'Aprobaste la revisión, sin hallazgos abiertos.');
        juzgar(e);
        return null;
      case 'motivo':
        e.motivo = MOTIVOS[Number(id.slice(6))];
        anotar(e, 'Vos (persona)', (e.hallazgo === 'riesgo' ? 'Aceptaste el riesgo' : 'Descartaste el hallazgo')
               + ' con el motivo: «' + e.motivo + '»');
        e.paso = 'revision';
        return null;
      case 'cierre':
        if (id === 'cerrar') anotar(e, 'Vos (persona)', 'Cerraste el cambio: la spec se fusionó y la tarea quedó cerrada.');
        e.fin = id === 'cerrar' ? 'cerrado' : 'abierto';
        e.paso = 'fin';
        return null;
    }
    return null;
  }

  // Qué dice el agente (o quien corresponda) en cada paso.
  function situacion(e) {
    return {
      pedido: e.propuestas < 2 ? 'Pedido: «que ninguna nota tenga el título vacío». El agente propone la spec: rechazar el título vacío.'
                               : 'El agente ajustó la propuesta: rechazar el título vacío y el de sólo espacios.',
      medidas: 'El agente propone medir con notas.casos_ejecutados y notas.resultados. ¿Las acordás?',
      pruebas: 'El agente construyó el validador. Las pruebas encontraron un caso que falla: un título de sólo espacios se guarda.',
      revision: e.hallazgo === 'abierto' ? 'codex revisó el código: 1 hallazgo medio, «el mensaje de error no dice qué campo falta».'
                                         : 'El hallazgo quedó resuelto (' + e.hallazgo + '). Ya podés decidir la revisión.',
      motivo: '¿Con qué motivo? Queda registrado a tu nombre.',
      cierre: e.oracle === 'verde' ? 'Oracle juzgó la evidencia: verde. Podés cerrar.'
            : e.oracle === 'rojo' ? 'Oracle juzgó la evidencia: rojo. No se puede cerrar.'
                                  : 'Oracle no pudo juzgar: no hay medidas acordadas.',
      fin: e.fin === 'cerrado' ? 'Cambio cerrado. Así quedó el registro.' : 'El cambio quedó abierto. Así quedó el registro.'
    }[e.paso];
  }

  var api = {nuevo: nuevo, opciones: opciones, elegir: elegir, situacion: situacion, MOTIVOS: MOTIVOS};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else raiz.Juego = api;
})(this);
