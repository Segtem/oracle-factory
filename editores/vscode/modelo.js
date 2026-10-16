'use strict';
// El árbol de la vista, armado sólo con la salida JSON de la CLI: sin `vscode`, para probarlo con node.
// Un nodo: {etiqueta, descripcion?, tooltip?, icono?, abrir? (archivo, relativo al proyecto), mostrar? (carpeta),
// comando? (texto para la terminal), hijos? (nodos), cambio? (id: los hijos se piden a la CLI al desplegarlo)}.
// `tipo(ruta)` lo da la extensión: 'archivo', 'carpeta' o null (no está); sólo se ofrece lo que está.

const PREFIJO = 'oracle-factory ';

function citar(texto) {
    // Entre comillas simples, con cada ' como '\'': lo leen igual bash, zsh y fish.
    return /^[\w@%+=:,./-]+$/.test(texto) ? texto : `'${texto.replace(/'/g, "'\\''")}'`;
}

function abrible(ruta, tipo) {
    if (typeof ruta !== 'string' || !ruta) return {};
    const t = tipo(ruta);
    return t === 'archivo' ? {abrir: ruta} : t === 'carpeta' ? {mostrar: ruta} : {};
}

// Un paso es un comando si empieza con la CLI; se reescribe con la que usa la extensión.
function comandoDe(paso, cli) {
    return typeof paso === 'string' && paso.startsWith(PREFIJO) ? `${citar(cli)} ${paso.slice(PREFIJO.length)}` : null;
}

function quien(decision) {
    return decision ? `${decision.actor} (${decision.tipo_actor}, ${decision.forma})` : null;
}

function raiz(resumen) {
    const abiertos = resumen.abiertos || [];
    if (!abiertos.length) return [{etiqueta: 'No hay cambios abiertos', icono: 'info'}];
    return abiertos.map(c => ({
        etiqueta: c.titulo || c.id, descripcion: c.fase, cambio: c.id, icono: 'git-pull-request',
        tooltip: [c.id, `modo ${c.modo}`, ...(c.pendientes || []).map(p => `pendiente: ${p}`)].join('\n'),
    }));
}

function paso(texto, cli) {
    const comando = comandoDe(texto, cli);
    return comando ? {etiqueta: comando, comando, icono: 'terminal', tooltip: 'Escribir en la terminal sin ejecutarlo'}
                   : {etiqueta: texto, icono: 'edit', tooltip: 'No es un comando: hacelo vos'};
}

function requisito(r) {
    const hijos = r.medidas.map(m => ({etiqueta: m, icono: 'symbol-ruler'}));
    if (r.decision) hijos.push({etiqueta: `decidió ${quien(r.decision)}`, icono: 'person'});
    else if (r.propuesta) hijos.push({etiqueta: `propuesta de ${quien(r.propuesta)}, sin confirmar`, icono: 'question'});
    else hijos.push({etiqueta: 'sin decisión de medidas', icono: 'warning'});
    return {etiqueta: r.id.split('.').pop(), descripcion: r.medidas.length ? `${r.medidas.length} medidas` : 'sin medida',
            tooltip: r.id, icono: r.decision ? 'pass' : 'circle-outline', hijos};
}

function revision(rev, tipo) {
    if (!rev) return {etiqueta: 'Revisión: pendiente', icono: 'circle-outline'};
    return {etiqueta: `Revisión: ${rev.decision}`, ...abrible(rev.informe, tipo),
            descripcion: `${rev.hallazgos_abiertos} hallazgos abiertos${rev.vigente ? '' : ' · ya no vigente'}`,
            tooltip: [rev.revisor, rev.informe].filter(x => typeof x === 'string').join('\n'), icono: rev.vigente ? 'eye' : 'warning'};
}

function veredicto(oracle, tipo) {
    if (!oracle) return {etiqueta: 'Veredicto: pendiente', icono: 'circle-outline'};
    const bien = oracle.codigo === 0;
    return {etiqueta: `Veredicto: ${bien ? 'exitoso' : `código ${oracle.codigo}`}`, ...abrible(oracle.informe, tipo),
            descripcion: oracle.vigente ? '' : 'ya no vigente', icono: bien && oracle.vigente ? 'pass' : 'error'};
}

function artefacto(a, tipo) {
    const destino = a.situacion === 'existe' || a.situacion === 'historico' ? abrible(a.ruta, tipo) : {};
    const situacion = destino.abrir || destino.mostrar ? null : a.situacion === 'existe' ? 'ya no está' : a.situacion;
    return {etiqueta: a.ruta.split('/').pop(), descripcion: situacion ? `${a.gate} · ${situacion}` : a.gate,
            tooltip: [a.ruta, a.nota].filter(Boolean).join('\n'), ...destino,
            icono: destino.abrir ? 'file' : destino.mostrar ? 'folder' : 'warning'};
}

function hijosCambio(estado, donde, cli, tipo) {
    const pasos = [estado.proximo_paso, ...(estado.alternativas || [])].filter(Boolean);
    return [
        ...pasos.map((p, i) => ({...paso(p, cli), descripcion: i ? 'alternativa' : 'próximo paso'})),
        {etiqueta: 'Requisitos', descripcion: String(estado.requisitos.length), icono: 'checklist',
         hijos: estado.requisitos.map(requisito)},
        revision(estado.revision, tipo),
        veredicto(estado.oracle, tipo),
        {etiqueta: 'Artefactos', descripcion: String(donde.artefactos.length), icono: 'files',
         hijos: donde.artefactos.map(a => artefacto(a, tipo))},
    ];
}

module.exports = {raiz, hijosCambio, comandoDe};
