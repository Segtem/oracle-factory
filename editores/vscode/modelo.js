'use strict';
// El árbol de la vista, armado sólo con la salida JSON de la CLI: sin `vscode`, para probarlo con node.
// Un nodo: {etiqueta, descripcion?, tooltip?, icono?, abrir? (ruta relativa al proyecto), comando? (texto
// para la terminal), hijos? (nodos), cambio? (id: los hijos se piden a la CLI al desplegarlo)}.

const PREFIJO = 'oracle-factory ';

function citar(texto) {
    // ponytail: comillas simples sin escapar una ' interna; alcanza para rutas de CLI comunes.
    return /^[\w@%+=:,./-]+$/.test(texto) ? texto : `'${texto}'`;
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

function revision(rev) {
    if (!rev) return {etiqueta: 'Revisión: pendiente', icono: 'circle-outline'};
    return {etiqueta: `Revisión: ${rev.decision}`, abrir: rev.informe || undefined,
            descripcion: `${rev.hallazgos_abiertos} hallazgos abiertos${rev.vigente ? '' : ' · ya no vigente'}`,
            tooltip: [rev.revisor, rev.informe].filter(Boolean).join('\n'), icono: rev.vigente ? 'eye' : 'warning'};
}

function veredicto(oracle) {
    if (!oracle) return {etiqueta: 'Veredicto: pendiente', icono: 'circle-outline'};
    const bien = oracle.codigo === 0;
    return {etiqueta: `Veredicto: ${bien ? 'exitoso' : `código ${oracle.codigo}`}`, abrir: oracle.informe || undefined,
            descripcion: oracle.vigente ? '' : 'ya no vigente', icono: bien && oracle.vigente ? 'pass' : 'error'};
}

function artefacto(a) {
    const abre = a.situacion === 'existe' || a.situacion === 'historico';
    return {etiqueta: a.ruta.split('/').pop(), descripcion: abre ? a.gate : `${a.gate} · ${a.situacion}`,
            tooltip: [a.ruta, a.nota].filter(Boolean).join('\n'), abrir: abre ? a.ruta : undefined,
            icono: abre ? 'file' : 'warning'};
}

function hijosCambio(estado, donde, cli) {
    const pasos = [estado.proximo_paso, ...(estado.alternativas || [])].filter(Boolean);
    return [
        ...pasos.map((p, i) => ({...paso(p, cli), descripcion: i ? 'alternativa' : 'próximo paso'})),
        {etiqueta: 'Requisitos', descripcion: String(estado.requisitos.length), icono: 'checklist',
         hijos: estado.requisitos.map(requisito)},
        revision(estado.revision),
        veredicto(estado.oracle),
        {etiqueta: 'Artefactos', descripcion: String(donde.artefactos.length), icono: 'files',
         hijos: donde.artefactos.map(artefacto)},
    ];
}

module.exports = {raiz, hijosCambio, comandoDe};
