/* Dos VS Code falsos —anfitriona e invitado— con la extensión cargada en cada uno y un Live Share falso que los
   conecta en memoria. Recorre: el invitado entra, abre el tablero, cambia un registro, elige un hallazgo y un comando,
   manda un mensaje, y se va.
   node tests/liveshare_en_node.cjs <carpeta de la extensión> <proyecto> <oracle-factory> <hallazgo JSON {archivo, linea}> <cambio>
   Imprime JSON con lo que vio cada uno. */
'use strict';
const Module = require('module');
const path = require('path');
const fs = require('fs');
const [extension, proyecto, cliRuta, hallazgoJson, cambio] = process.argv.slice(2);
const hallazgo = JSON.parse(hallazgoJson);
const espera = ms => new Promise(r => setTimeout(r, ms));

// --- el Live Share falso: un servicio por nombre, y los dos lados enganchados ----------------------------------------
function emisor() {
    const oyentes = [];
    const e = f => { oyentes.push(f); return {dispose() {}}; };
    e.disparar = x => oyentes.forEach(f => f(x));
    return e;
}
const servicios = {};
function liveShare(rol, usuario) {
    const api = {
        session: {role: rol, user: {displayName: usuario}, id: 's1'},
        peers: [],
        onDidChangeSession: emisor(), onDidChangePeers: emisor(),
        async shareService(nombre) {
            const s = servicios[nombre] = {pedidos: {}, avisos: [], isServiceAvailable: true,
                onDidChangeIsServiceAvailable: emisor(),
                onRequest(n, f) { this.pedidos[n] = f; }, onNotify() {},
                notify(n, args) { this.avisos.filter(a => a.n === n).forEach(a => a.f(args)); }};
            return s;
        },
        async getSharedService(nombre) {
            const s = servicios[nombre];
            return {isServiceAvailable: Boolean(s), onDidChangeIsServiceAvailable: emisor(),
                    onNotify(n, f) { s.avisos.push({n, f}); }, notify() {},
                    async request(n, args) { return JSON.parse(JSON.stringify(await s.pedidos[n](args, null))); }};
        },
    };
    return api;
}

// --- un VS Code falso por persona --------------------------------------------------------------------------------
function vscodeFalso({carpeta, uriCarpeta, comando, ls}) {
    const r = {terminal: [], abiertos: [], diffs: [], errores: [], comandos: {}, vigias: [], panel: null, pintadas: 0};
    const nada = () => ({dispose() {}});
    r.vscode = {
        EventEmitter: class { constructor() { this.event = nada; } fire() {} },
        TreeItem: class {}, TreeItemCollapsibleState: {None: 0, Collapsed: 1}, ThemeIcon: class {}, ViewColumn: {One: 1},
        Uri: {file: p => ({fsPath: p, scheme: 'file'}),
              joinPath: (base, ...partes) => ({fsPath: path.posix.join(base.fsPath, ...partes), scheme: base.scheme})},
        Range: class { constructor(l, c) { this.start = {line: l, character: c}; } },
        extensions: ls ? {getExtension: id => id === 'ms-vsliveshare.vsliveshare'
            ? {isActive: true, exports: {getApi: async () => ls}} : undefined} : undefined,
        workspace: {
            workspaceFolders: [{uri: uriCarpeta || {fsPath: carpeta, scheme: 'file'}}],
            getConfiguration: () => ({get: clave => (clave === 'comando' ? comando : undefined)}),
            createFileSystemWatcher: () => {
                const v = {cambios: [], onDidChange: f => { v.cambios.push(f); return nada(); }, onDidCreate: nada, onDidDelete: nada, dispose() {}};
                r.vigias.push(v);
                return v;
            },
            openTextDocument: async a => (a && a.content !== undefined ? {contenido: a.content} : {uri: a}),
        },
        window: {
            terminals: [],
            registerTreeDataProvider: nada,
            showErrorMessage: m => { r.errores.push(m); },
            createTerminal(opciones) {
                const t = {...opciones, exitStatus: undefined, show() {}, sendText: (texto, enter) => r.terminal.push({texto, enter})};
                this.terminals.push(t);
                return t;
            },
            showTextDocument: async (doc, opciones) => {
                if (doc.contenido !== undefined) return r.diffs.push(doc.contenido.split('\n')[0]);
                r.abiertos.push({uri: doc.uri.fsPath, esquema: doc.uri.scheme, linea: opciones.selection ? opciones.selection.start.line + 1 : null});
            },
            createWebviewPanel: () => {
                let html = '', recibir = null;
                r.panel = {webview: {cspSource: 'vscode-resource:', onDidReceiveMessage: f => { recibir = f; return nada(); },
                                     get html() { return html; }, set html(h) { html = h; r.pintadas++; }},
                           onDidDispose: nada, reveal() {}, recibir: m => recibir(m)};
                return r.panel;
            },
        },
        commands: {registerCommand: (id, f) => { r.comandos[id] = f; return nada(); }},
    };
    return r;
}

// Carga la extensión con su propio `vscode` (cada persona tiene su copia de los módulos).
const requerir = Module.prototype.require;
let actual = null;
Module.prototype.require = function (nombre) { return nombre === 'vscode' ? actual : requerir.apply(this, arguments); };
function cargar(falso) {
    for (const k of Object.keys(require.cache)) if (k.startsWith(path.resolve(extension))) delete require.cache[k];
    actual = falso.vscode;
    const ext = require(path.resolve(extension, 'extension.js'));
    ext.activate({subscriptions: [], extension: {id: 'cs50-taller.oracle-factory'}});
    return ext;
}

async function hasta(cond, que) {
    for (let i = 0; i < 200 && !cond(); i++) await espera(25);
    if (!cond()) throw new Error(`no pasó: ${que}`);
}

(async () => {
    const vistas = {};
    const lsAnfitriona = liveShare(1, 'Ana Anfitriona');
    const ana = vscodeFalso({carpeta: proyecto, comando: cliRuta, ls: lsAnfitriona});
    cargar(ana);
    await espera(50);
    await ana.comandos['factory.tablero']();
    await hasta(() => ana.panel.webview.html.includes('En la sesión'), 'la anfitriona ve su sesión');
    vistas.anaSola = ana.panel.webview.html;

    // El invitado entra: no tiene Factory (su comando no existe) ni el proyecto en disco.
    const lsInvitado = liveShare(2, 'Iván Invitado');
    lsInvitado.peers = [{user: {displayName: 'Ana Anfitriona'}, role: 1}];
    lsAnfitriona.peers = [{user: {displayName: 'Iván Invitado'}, role: 2}];
    lsAnfitriona.onDidChangePeers.disparar({added: lsAnfitriona.peers, removed: []});
    const ivan = vscodeFalso({carpeta: '/no/existe', uriCarpeta: {fsPath: '/', scheme: 'vsls'}, comando: '/no/existe/oracle-factory', ls: lsInvitado});
    cargar(ivan);
    await espera(50);
    await ivan.comandos['factory.tablero']();
    await hasta(() => ivan.panel.webview.html.includes(cambio), 'el invitado ve el tablero de la anfitriona');
    await hasta(() => ana.panel.webview.html.includes('Iván Invitado'), 'la anfitriona ve al invitado');
    vistas.ivan = ivan.panel.webview.html;
    vistas.anaConIvan = ana.panel.webview.html;

    // Cambia un registro de la anfitriona: su vigía avisa, ella rehace y el invitado pide otra vez.
    const registro = path.join(proyecto, '.factory/cambios', cambio, 'factory.json');
    const datos = JSON.parse(fs.readFileSync(registro, 'utf8'));
    datos.titulo = 'Un título que cambió en la sesión';
    fs.writeFileSync(registro, JSON.stringify(datos));
    for (const v of ana.vigias) for (const f of v.cambios) f();
    await hasta(() => ivan.panel.webview.html.includes('Un título que cambió en la sesión'), 'el invitado ve el cambio');

    // El invitado elige un hallazgo, un camino que sube, y un comando.
    await ivan.panel.recibir({tipo: 'abrir', archivo: hallazgo.archivo, linea: hallazgo.linea});
    await ivan.panel.recibir({tipo: 'abrir', archivo: '../../etc/passwd', linea: 1});
    await ivan.panel.recibir({tipo: 'terminal', comando: `oracle-factory estado ${cambio}`});
    await ivan.panel.recibir({tipo: 'terminal', comando: `oracle-factory estado ${cambio}\ntouch pwned`});

    // Un mensaje del invitado: lo guarda la anfitriona con el nombre de Live Share.
    await ivan.panel.recibir({tipo: 'mensaje', cambio, texto: 'revisá el hook <b>ya</b>'});
    for (const v of ana.vigias) for (const f of v.cambios) f();
    await hasta(() => ivan.panel.webview.html.includes('revisá el hook'), 'el invitado ve su mensaje');
    await hasta(() => ana.panel.webview.html.includes('revisá el hook'), 'la anfitriona ve el mensaje');
    vistas.ivanConMensaje = ivan.panel.webview.html;

    // El invitado se va.
    lsAnfitriona.peers = [];
    lsAnfitriona.onDidChangePeers.disparar({added: [], removed: [{user: {displayName: 'Iván Invitado'}, role: 2}]});
    await hasta(() => !ana.panel.webview.html.includes('Iván Invitado</b> (invitado)'), 'la anfitriona ve que se fue');
    vistas.anaSinIvan = ana.panel.webview.html;

    process.stdout.write(JSON.stringify({vistas, ivan: {abiertos: ivan.abiertos, terminal: ivan.terminal, errores: ivan.errores},
                                         ana: {terminal: ana.terminal, errores: ana.errores}}));
})().catch(e => { console.error(e); process.exit(1); });
