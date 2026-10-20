/* Los botones de la sesión de Live Share en el tablero, con un `vscode` falso y un Live Share falso (o sin él).
   node tests/sesion_en_node.cjs <carpeta de la extensión> <proyecto> <oracle-factory> <con|sin> <enlaces JSON>
   Recorre: compartir, terminar, unirse con cada enlace (en orden); sin Live Share, instalar. Imprime JSON. */
'use strict';
const Module = require('module');
const path = require('path');
const [extension, proyecto, cliRuta, conLiveShare, enlacesJson] = process.argv.slice(2);
const enlaces = JSON.parse(enlacesJson || '[]');
const espera = ms => new Promise(r => setTimeout(r, ms));

function emisor() {
    const oyentes = [];
    const e = f => { oyentes.push(f); return {dispose() {}}; };
    e.disparar = x => oyentes.forEach(f => f(x));
    return e;
}
const llamadas = [];
const ls = {
    session: {role: 0, user: {displayName: 'Ana'}}, peers: [],
    onDidChangeSession: emisor(), onDidChangePeers: emisor(),
    async share(opciones) {
        llamadas.push(opciones && opciones.suppressNotification ? 'share (sin aviso)' : 'share');
        this.session = {role: 1, user: {displayName: 'Ana'}};
        this.onDidChangeSession.disparar({});
        return {toString: () => 'https://prod.liveshare.vsengsaas.visualstudio.com/join?SESION1'};
    },
    async end() { llamadas.push('end'); this.session = {role: 0, user: {displayName: 'Ana'}}; this.onDidChangeSession.disparar({}); },
    async join(uri) { llamadas.push(`join ${uri.toString()}`); },
    async shareService() { return {onRequest() {}, onNotify() {}, notify() {}}; },
    async getSharedService() { return null; },
};
const nada = () => ({dispose() {}});
let panel = null, html = '';
const pedidos = [...enlaces];
const comandos = {}, errores = [], ejecutados = [], avisos = [], portapapeles = [];
const vscode = {
    EventEmitter: class { constructor() { this.event = nada; } fire() {} },
    TreeItem: class {}, TreeItemCollapsibleState: {None: 0, Collapsed: 1}, ThemeIcon: class {}, ViewColumn: {One: 1},
    Uri: {file: p => ({fsPath: p}), parse: t => ({toString: () => t})},
    Range: class {},
    env: {clipboard: {writeText: async t => { portapapeles.push(t); }}},
    extensions: {getExtension: id => (conLiveShare !== 'sin' && id === 'ms-vsliveshare.vsliveshare'
        ? {isActive: true, exports: {getApi: async () => ls}} : undefined)},
    workspace: {
        workspaceFolders: [{uri: {fsPath: proyecto}}],
        getConfiguration: () => ({get: clave => (clave === 'comando' ? cliRuta : undefined)}),
        createFileSystemWatcher: () => ({onDidChange: nada, onDidCreate: nada, onDidDelete: nada, dispose() {}}),
    },
    window: {
        terminals: [], registerTreeDataProvider: nada,
        showErrorMessage: m => { errores.push(m); },
        showInformationMessage: m => { avisos.push(m); },
        showInputBox: async () => pedidos.shift(),
        createWebviewPanel: () => {
            let recibir = null;
            panel = {webview: {cspSource: 'x', onDidReceiveMessage: f => { recibir = f; return nada(); },
                               get html() { return html; }, set html(h) { html = h; }},
                     onDidDispose: nada, reveal() {}, recibir: m => recibir(m)};
            return panel;
        },
    },
    commands: {registerCommand: (id, f) => { comandos[id] = f; return nada(); },
               executeCommand: async (...args) => { ejecutados.push(args); }},
};
const requerir = Module.prototype.require;
Module.prototype.require = function (n) { return n === 'vscode' ? vscode : requerir.apply(this, arguments); };

async function hasta(cond, que) {
    for (let i = 0; i < 200 && !cond(); i++) await espera(25);
    if (!cond()) throw new Error(`no pasó: ${que}`);
}

(async () => {
    require(path.resolve(extension, 'extension.js')).activate({subscriptions: [], extension: {id: 'cs50-taller.oracle-factory'}});
    await espera(50);
    await comandos['factory.tablero']();
    const vistas = {};
    if (conLiveShare === 'ya-compartida') {
        // Live Share ya compartía (desde la paleta) y da el rol como texto: el tablero lo ve y no comparte otra vez.
        ls.session = {role: 'Host', id: 'sesion-de-la-paleta', user: {displayName: 'Ana'}};
        ls.onDidChangeSession.disparar({});
        await hasta(() => html.includes('En la sesión'), 've la sesión');
        await panel.recibir({tipo: 'sesion', accion: 'compartir'});
        await panel.recibir({tipo: 'sesion', accion: 'copiar'});
        await hasta(() => html.includes('que copió Live Share al compartir'), 'explica de dónde sale el enlace');
        vistas.inicio = html;
    } else if (conLiveShare !== 'con') {
        await hasta(() => html.includes('data-sesion="instalar"'), 'ofrece instalar');
        vistas.inicio = html;
        await panel.recibir({tipo: 'sesion', accion: 'instalar'});
    } else {
        await hasta(() => html.includes('data-sesion="compartir"'), 'ofrece compartir');
        vistas.inicio = html;
        await panel.recibir({tipo: 'sesion', accion: 'compartir'});
        await hasta(() => html.includes('data-sesion="terminar"'), 'ofrece terminar');
        vistas.compartida = html;
        await panel.recibir({tipo: 'sesion', accion: 'compartir'});  // ya compartida: no empieza otra
        await panel.recibir({tipo: 'sesion', accion: 'copiar'});
        await panel.recibir({tipo: 'sesion', accion: 'copiar'});  // copiar otra vez no le pide nada a Live Share
        await hasta(() => html.includes('join?SESION1</code>'), 'muestra el enlace');
        vistas.conEnlace = html;
        await panel.recibir({tipo: 'sesion', accion: 'terminar'});
        await hasta(() => html.includes('data-sesion="compartir"'), 'vuelve a ofrecer compartir');
        for (let i = 0; i < enlaces.length; i++) await panel.recibir({tipo: 'sesion', accion: 'unirse'});
    }
    process.stdout.write(JSON.stringify({vistas, llamadas, errores, ejecutados, avisos, portapapeles}));
})().catch(e => { console.error(e); process.exit(1); });
