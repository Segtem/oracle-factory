'use strict';
// El tablero de comando: el HTML del panel, armado sólo con el JSON de `oracle-factory tablero --json`.
// Puro (sin `vscode`), para probarlo con node. Todo texto que viene del registro o de los informes se escapa.

const ACCIONES = {
    cambio_creado: 'Cambio creado', spec_aprobada: 'Spec aprobada', spec_aceptada_en_conversacion: 'Spec aceptada en la conversación',
    requisitos_importados: 'Requisitos importados', medidas_propuestas: 'Medidas propuestas', medidas_confirmadas: 'Medidas confirmadas',
    medidas_elegidas: 'Medidas elegidas', revision_lanzada: 'Revisor lanzado', revision_pedida: 'Revisión pedida',
    revision_propuesta: 'Revisión propuesta', revision_registrada: 'Revisión registrada', revision_cancelada: 'Revisión sin registrar',
    oracle_ejecutado: 'Juicio de Oracle', cierre: 'Cerrado', archivado: 'Archivado', abandono: 'Abandonado',
    abandono_propuesto: 'Abandono propuesto',
    tomado: 'Tomado', soltado: 'Soltado', agente_sumado: 'Agente sumado', mensaje: 'Mensaje',
};
const ETAPAS = [['acuerdo', 'Spec'], ['medidas', 'Medidas'], ['construcción y revisión', 'Revisión'], ['juicio', 'Juicio'], ['cierre', 'Cierre']];
const SEVERIDADES = ['critica', 'alta', 'media', 'baja', 'informativa'];

function esc(texto) {
    return String(texto == null ? '' : texto).replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
}

function hora(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    return isNaN(d) ? esc(iso) : d.toLocaleString('es-AR', {day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'});
}

function horas(h) {
    if (h == null) return '—';
    return h < 1 ? `${Math.round(h * 60)} min` : `${h.toFixed(1).replace('.', ',')} h`;
}

// Un enlace que abre un archivo (y una línea) del proyecto: lo resuelve la extensión, que comprueba que esté adentro.
function abrir(archivo, linea, texto) {
    if (!archivo) return esc(texto);
    return `<button type="button" class="enlace" data-abrir="${esc(archivo)}"${linea ? ` data-linea="${Number(linea)}"` : ''}>${esc(texto)}</button>`;
}

function paso(p, comoAlternativa) {
    if (!p) return '';
    const boton = p.comando ? `<button type="button" class="terminal" data-comando="${esc(p.comando)}">Escribir en la terminal</button>` : '';
    return `<div class="paso${p.decision_de_la_persona ? ' tuya' : ''}${comoAlternativa ? ' alternativa' : ''}">
<p class="etiqueta">${p.decision_de_la_persona ? 'TE NECESITA' : comoAlternativa ? 'TAMBIÉN' : 'LO QUE SIGUE'}</p>
<p><code>${esc(p.texto)}</code></p>${boton}</div>`;
}

function etapas(cambio) {
    const hechas = new Set(cambio.metricas.fases.map(f => f.fase));
    return `<ol class="etapas" aria-label="Fases">${ETAPAS.map(([clave, nombre]) =>
        `<li class="${hechas.has(clave) ? 'hecha' : ''}">${nombre}</li>`).join('')}</ol>`;
}

function hallazgos(cambio) {
    if (!cambio.hallazgos.length) return '<p class="vacio">Sin hallazgos de revisores en el candidato vigente.</p>';
    const filas = cambio.hallazgos.map(h => `<tr class="sev-${esc(h.severidad)}">
<td><span class="sev">${esc(h.severidad)}</span></td><td>${esc(h.revisor)}</td>
<td>${abrir(h.archivo, h.linea, h.archivo ? `${h.archivo}${h.linea ? ':' + h.linea : ''}` : '(sin archivo)')}</td>
<td>${esc(h.titulo)}</td><td>${h.estado === 'aceptado' ? 'riesgo aceptado' : 'abierto'}</td></tr>`).join('');
    return `<table><thead><tr><th>Severidad</th><th>Revisor</th><th>Dónde</th><th>Hallazgo</th><th>Estado</th></tr></thead><tbody>${filas}</tbody></table>`;
}

function quien(cambio) {
    const q = cambio.quien;
    if (!q) return '';
    const r = q.responsable
        ? `<b>${esc(q.responsable.persona)}</b> desde ${hora(q.responsable.desde)}`
        : '<span class="aviso-texto">sin responsable</span> (<code>oracle-factory tomar ID</code>)';
    const agentes = q.agentes.map(a => `<li><b>${esc(a.nombre)}</b>${a.declarado ? ' (declarado)' : ''}${a.ultima_accion
        ? ` · ${esc(ACCIONES[a.ultima_accion] || a.ultima_accion)} ${hora(a.cuando)}` : ''}</li>`).join('');
    const revisores = q.revisores_en_curso.map(v => `<li>revisando: <b>${esc(v.revisor)}</b> sobre ${esc(v.candidato)} desde ${hora(v.cuando)}</li>`).join('');
    return `<div class="quien"><p>Responsable: ${r}</p>${agentes || revisores ? `<ul>${agentes}${revisores}</ul>` : ''}</div>`;
}

function commits(cambio) {
    const lista = cambio.commits || [];
    if (!lista.length) return '<p class="vacio">Ningún commit unido todavía: los nuevos llevan «Cambio: ID» con el hook de <code>oracle-factory hooks</code>.</p>';
    const filas = lista.map(c => `<tr><td><button type="button" class="enlace" data-commit="${esc(c.sha)}">${esc(c.corto)}</button></td>
<td>${esc(c.asunto)}</td><td>${esc(c.autor)}</td><td>${hora(c.fecha)}</td>
<td>${esc([c.union, c.candidato && 'candidato', c.revisado && 'revisado', c.evidencia && 'evidencia'].filter(Boolean).join(' · '))}</td></tr>`).join('');
    return `<table><thead><tr><th>Commit</th><th>Asunto</th><th>Autor</th><th>Cuándo</th><th>Unión</th></tr></thead><tbody>${filas}</tbody></table>`;
}

function requisitos(cambio) {
    if (!cambio.requisitos.length) return '<p class="vacio">Todavía no hay requisitos importados.</p>';
    return `<ul class="requisitos">${cambio.requisitos.map(r => {
        const quien = r.decision ? `decidió ${esc(r.decision.actor)} (${esc(r.decision.tipo_actor)})`
            : r.propuesta ? `propuesta de ${esc(r.propuesta.actor)}, sin confirmar` : 'sin decisión de medidas';
        const medidas = r.medidas.map(m => abrir(m.archivo, null, m.id)).join(' · ') || 'sin medida';
        return `<li>${abrir(r.archivo, null, r.id.split('.').pop())} <span class="quien">${quien}</span><br><small>${medidas}</small></li>`;
    }).join('')}</ul>`;
}

function linea(cambio) {
    const eventos = cambio.linea_de_tiempo.slice().reverse();
    return `<ol class="linea">${eventos.map(e => {
        const d = e.detalle || {};
        const extra = [d.revisor, d.resultado, d.hallazgos != null ? `${d.hallazgos} hallazgos` : null, d.decision,
                       d.codigo != null ? `código ${d.codigo}` : null, d.causa, d.texto, d.via].filter(x => x != null && x !== '').map(esc).join(' · ');
        return `<li class="actor-${esc(e.tipo_actor)}"><time>${hora(e.cuando)}</time> <b>${esc(ACCIONES[e.accion] || e.accion)}</b>
<span class="quien">${esc(e.actor)}${e.tipo_actor === 'sin_identificar' ? ' ⚠' : ''}</span>${extra ? `<small>${extra}</small>` : ''}</li>`;
    }).join('')}</ol>`;
}

function barras(cuenta) {
    const total = SEVERIDADES.reduce((s, k) => s + (cuenta[k] || 0), 0);
    if (!total) return '<p class="vacio">Sin hallazgos.</p>';
    return `<div class="barra" role="img" aria-label="${SEVERIDADES.map(k => `${k}: ${cuenta[k] || 0}`).join(', ')}">${
        SEVERIDADES.filter(k => cuenta[k]).map(k => `<span class="sev-${k}" style="width:${(100 * cuenta[k] / total).toFixed(1)}%">${cuenta[k]}</span>`).join('')}</div>`;
}

function metricas(m) {
    const fases = m.fases.map(f => `<li>${esc(f.fase)}: <b>${horas(f.horas)}</b></li>`).join('') || '<li>Ninguna fase cerrada todavía.</li>';
    const a = m.decisiones_por_actor;
    return `<div class="metricas">
<div><h4>Tiempo por fase</h4><ul>${fases}</ul></div>
<div><h4>Revisión</h4><p><b>${m.vueltas_de_revision}</b> vueltas · <b>${m.riesgos_aceptados}</b> riesgos aceptados</p>${barras(m.hallazgos_por_severidad)}</div>
<div><h4>Quién decidió</h4><p><b>${a.persona}</b> persona · <b>${a.agente}</b> agente${a.sin_identificar ? ` · <b class="aviso-texto">${a.sin_identificar}</b> sin autor` : ''}</p></div>
<div><h4>Requisitos</h4><p><b>${m.requisitos.medidos}</b> de ${m.requisitos.total} medidos${m.requisitos.cumplidos != null ? ` · <b>${m.requisitos.cumplidos}</b> cumplen` : ''}</p></div>
</div>`;
}

// La sesión de Live Share: quién está y con qué rol. Sin Live Share o sin sesión, una línea.
function sesion(s) {
    const boton = (accion, texto) => `<button type="button" class="terminal" data-sesion="${accion}">${texto}</button>`;
    if (!s || s.estado === 'sin-live-share')
        return `<p class="sesion vacio">Sin Live Share: para trabajar de a dos, instalalo y compartí la sesión. ${boton('instalar', 'Instalar Live Share')}</p>`;
    if (s.estado === 'sin-sesion')
        return `<p class="sesion">Sin sesión de Live Share. ${boton('compartir', 'Compartir sesión')} ${boton('unirse', 'Unirse a una sesión')}</p>`;
    const gente = [`<li><b>${esc(s.yo)}</b> (vos, ${esc(s.rol)})</li>`, ...s.otros.map(o => `<li><b>${esc(o.nombre)}</b> (${esc(o.rol)})</li>`)];
    return `<div class="sesion"><h2>En la sesión</h2><ul>${gente.join('')}</ul>${s.invitado
        ? '<p class="vacio">Ves el tablero de quien comparte; los comandos se escriben en su terminal «Factory».</p>' : ''}${
        s.rol === 'anfitrión' ? `<p>Para que alguien entre, pasale el enlace${s.enlace ? `: <code>${esc(s.enlace)}</code>` : ''}. ${
            boton('copiar', 'Copiar enlace')} ${boton('terminar', 'Terminar sesión')}</p>` : boton('terminar', 'Salir de la sesión')}</div>`;
}

// El chat del cambio: los mensajes del registro; en una sesión de Live Share, una caja para escribir.
function chat(c, s) {
    const mensajes = c.linea_de_tiempo.filter(e => e.accion === 'mensaje').map(e =>
        `<li><time>${hora(e.cuando)}</time> <b>${esc(e.actor)}</b>${e.detalle && e.detalle.via ? ` <small>(${esc(e.detalle.via)}${e.detalle.guardado_por ? `, guardado por ${esc(e.detalle.guardado_por)}` : ''})</small>` : ''}: ${esc(e.detalle && e.detalle.texto)}</li>`).join('');
    const caja = s && s.estado === 'activa'
        ? `<form class="escribir" data-cambio="${esc(c.id)}"><input name="texto" maxlength="2000" aria-label="Mensaje para ${esc(c.id)}" placeholder="Escribí un mensaje (queda en el cambio: sin secretos)"><button type="submit">Enviar</button></form>`
        : `<p class="vacio">Desde la terminal: <code>oracle-factory mensaje ${esc(c.id)} "…"</code>; en una sesión de Live Share, acá.</p>`;
    return `${mensajes ? `<ol class="chat">${mensajes}</ol>` : '<p class="vacio">Sin mensajes.</p>'}${caja}`;
}

function cambio(c, s) {
    const avisos = c.avisos.length ? `<ul class="avisos">${c.avisos.map(a => `<li>⚠ ${esc(a)}</li>`).join('')}</ul>` : '';
    return `<section class="cambio" data-cambio="${esc(c.id)}">
<header><h2>${esc(c.titulo)}</h2><p class="id">${esc(c.id)} · ${esc(c.fase)} · modo ${esc(c.modo)}${c.candidato ? ` · candidato ${esc(c.candidato)}` : ''}</p>${etapas(c)}</header>
${quien(c)}${paso(c.proximo_paso, false)}${c.alternativas.map(a => paso(a, true)).join('')}${avisos}
<h3>Hallazgos</h3>${hallazgos(c)}
<h3>Requisitos</h3>${requisitos(c)}
<h3>Commits (${(c.commits || []).length})</h3>${commits(c)}
<h3>Chat</h3>${chat(c, s)}
<h3>Métricas</h3>${metricas(c.metricas)}
<details><summary>Línea de tiempo (${c.linea_de_tiempo.length})</summary>${linea(c)}</details>
</section>`;
}

function proyecto(p) {
    const revisores = Object.entries(p.hallazgos_por_revisor).map(([r, cuenta]) =>
        `<li><b>${esc(r)}</b> ${barras(cuenta)}</li>`).join('') || '<li>Sin informes todavía.</li>';
    const v = p.primera_vuelta;
    return `<section class="proyecto"><h2>El proyecto</h2><div class="metricas">
<div><h4>Cambios</h4><p><b>${p.cambios.abiertos}</b> abiertos · <b>${p.cambios.cerrados}</b> cerrados · <b>${p.cambios.abandonados}</b> abandonados</p></div>
<div><h4>Hasta el cierre</h4><p>mediana <b>${horas(p.mediana_horas_hasta_cierre)}</b></p></div>
<div><h4>Primera vuelta</h4><p>${v.proporcion == null ? '—' : `<b>${v.en_una_vuelta}</b> de ${v.cerrados_con_revision} cerraron en una vuelta`}</p></div>
<div><h4>Quién está en qué</h4><ul class="revisores">${Object.entries(p.por_responsable || {}).map(([persona, ids]) =>
    `<li><b>${esc(persona)}</b>: ${ids.map(esc).join(', ')}</li>`).join('')}${(p.sin_responsable || []).length
    ? `<li><span class="aviso-texto">sin responsable</span>: ${p.sin_responsable.map(esc).join(', ')}</li>` : ''}</ul></div>
<div><h4>Qué encontró cada revisor</h4><ul class="revisores">${revisores}</ul></div>
</div></section>`;
}

function estilo() {
    return `body{font-family:var(--vscode-font-family);color:var(--vscode-foreground);background:var(--vscode-editor-background);padding:0 18px 40px;max-width:1100px}
h1{font-size:20px;display:flex;gap:10px;align-items:center}h2{font-size:17px;margin:0}h3{font-size:13px;letter-spacing:.06em;text-transform:uppercase;margin:22px 0 8px;opacity:.85}h4{margin:0 0 4px;font-size:12px;opacity:.8}
.cambio,.proyecto{border:2px solid var(--vscode-panel-border,#555);padding:14px 16px;margin:16px 0;box-shadow:4px 4px 0 var(--vscode-panel-border,#555)}
.id{font-family:var(--vscode-editor-font-family);font-size:12px;opacity:.8;margin:4px 0 10px}
.etapas{display:flex;gap:4px;list-style:none;padding:0;margin:0}.etapas li{padding:3px 8px;border:1px solid var(--vscode-panel-border,#555);font-size:11px;opacity:.6}.etapas li.hecha{opacity:1;background:var(--vscode-testing-iconPassed,#2e7d32);color:var(--vscode-editor-background)}
.paso{border-left:4px solid var(--vscode-panel-border,#888);padding:6px 12px;margin:12px 0}.paso.tuya{border-left-color:var(--vscode-charts-yellow,#e0b000);background:color-mix(in srgb,var(--vscode-charts-yellow,#e0b000) 12%,transparent)}.paso.alternativa{opacity:.85}
.etiqueta{font-size:11px;letter-spacing:.08em;margin:0;font-weight:700}code{font-family:var(--vscode-editor-font-family);word-break:break-all}
button{font:inherit;cursor:pointer}button.terminal{background:var(--vscode-button-background);color:var(--vscode-button-foreground);border:0;padding:5px 10px}
button.enlace{background:none;border:0;padding:0;color:var(--vscode-textLink-foreground);text-decoration:underline;text-align:left}
button:focus-visible{outline:2px solid var(--vscode-focusBorder);outline-offset:2px}
.avisos{list-style:none;padding:8px 12px;border:1px solid var(--vscode-charts-orange,#d97706);margin:10px 0}.aviso-texto{color:var(--vscode-charts-orange,#d97706)}
table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;padding:4px 6px;border-bottom:1px solid var(--vscode-panel-border,#444);vertical-align:top}
.sev{font-size:11px;font-weight:700;text-transform:uppercase}.sev-critica .sev,.sev-alta .sev{color:var(--vscode-charts-red,#d32f2f)}.sev-media .sev{color:var(--vscode-charts-orange,#d97706)}
.metricas{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px}.metricas ul{margin:0;padding-left:18px}.metricas p{margin:0}
.barra{display:flex;height:16px;margin-top:6px;border:1px solid var(--vscode-panel-border,#555)}.barra span{font-size:10px;text-align:center;color:#fff;overflow:hidden}
.barra .sev-critica{background:#7f1d1d}.barra .sev-alta{background:#d32f2f}.barra .sev-media{background:#d97706}.barra .sev-baja{background:#2563eb}.barra .sev-informativa{background:#6b7280}
.revisores{list-style:none;padding:0}.requisitos{padding-left:18px}.requisitos li{margin:4px 0}.quien{opacity:.75;font-size:12px}
.linea{list-style:none;padding:0;font-size:13px}.linea li{padding:4px 0 4px 10px;border-left:3px solid var(--vscode-panel-border,#555)}.linea li.actor-persona{border-left-color:var(--vscode-charts-green,#2e7d32)}.linea li.actor-agente{border-left-color:var(--vscode-charts-blue,#2563eb)}.linea li.actor-sin_identificar{border-left-color:var(--vscode-charts-orange,#d97706)}
.linea time{font-family:var(--vscode-editor-font-family);opacity:.7}.linea small{display:block;opacity:.8}.vacio{opacity:.7}
.quien{margin:8px 0}.quien p{margin:0}.quien ul{margin:4px 0 0;padding-left:18px;font-size:13px}
.sesion{border:1px dashed var(--vscode-panel-border,#555);padding:6px 12px;margin:10px 0}.sesion h2{font-size:14px}.sesion ul{margin:4px 0;padding-left:18px}
.chat{list-style:none;padding:0;font-size:13px}.chat li{padding:3px 0}.escribir{display:flex;gap:6px;margin-top:6px}.escribir input{flex:1;background:var(--vscode-input-background);color:var(--vscode-input-foreground);border:1px solid var(--vscode-input-border,#555);padding:4px}
.marca{width:28px;height:28px;image-rendering:pixelated}`;
}

function marca() {
    // La fábrica de la web en pixel art, chiquita.
    return `<svg class="marca" viewBox="0 0 16 16" shape-rendering="crispEdges" aria-hidden="true"><rect x="1" y="7" width="14" height="8" fill="#5f8f4e"/><rect x="3" y="2" width="3" height="6" fill="#182a25"/><rect x="10" y="4" width="2" height="4" fill="#182a25"/><rect x="3" y="10" width="2" height="2" fill="#ebc36f"/><rect x="7" y="10" width="2" height="2" fill="#ebc36f"/><rect x="11" y="10" width="2" height="2" fill="#ebc36f"/></svg>`;
}

// La página entera. `nonce` y `cspSource` los da la extensión: sin red, y sólo corre el script de la página.
function html(datos, {nonce, cspSource}) {
    const cuerpo = datos.cambios.length ? datos.cambios.map(c => cambio(c, datos.sesion)).join('')
        : '<p class="vacio">No hay cambios abiertos. Empezá uno con <code>oracle-factory nuevo</code>.</p>';
    return `<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src ${cspSource} data:; style-src 'nonce-${nonce}'; script-src 'nonce-${nonce}';">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Tablero de Factory</title>
<style nonce="${nonce}">${estilo()}</style></head><body>
<h1>${marca()} Tablero de Factory</h1>
${sesion(datos.sesion)}
${cuerpo}
${proyecto(datos.proyecto)}
<script nonce="${nonce}">
const vscode = acquireVsCodeApi();
document.addEventListener('click', ev => {
  const b = ev.target.closest('button');
  if (!b) return;
  if (b.dataset.abrir) vscode.postMessage({tipo: 'abrir', archivo: b.dataset.abrir, linea: b.dataset.linea ? Number(b.dataset.linea) : null});
  if (b.dataset.comando) vscode.postMessage({tipo: 'terminal', comando: b.dataset.comando});
  if (b.dataset.commit) vscode.postMessage({tipo: 'commit', sha: b.dataset.commit});
  if (b.dataset.sesion) vscode.postMessage({tipo: 'sesion', accion: b.dataset.sesion});
});
document.addEventListener('submit', ev => {
  const f = ev.target.closest('form.escribir');
  if (!f) return;
  ev.preventDefault();
  const texto = f.elements.texto.value.trim();
  if (texto) vscode.postMessage({tipo: 'mensaje', cambio: f.dataset.cambio, texto});
  f.elements.texto.value = '';
});
</script></body></html>`;
}

function error(mensaje, {nonce}) {
    return `<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'nonce-${nonce}';">
<style nonce="${nonce}">body{font-family:var(--vscode-font-family);color:var(--vscode-foreground);padding:18px}</style></head>
<body><h1>Tablero de Factory</h1><p>${esc(mensaje)}</p></body></html>`;
}

module.exports = {html, error, esc};
