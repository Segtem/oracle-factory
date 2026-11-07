/* El tablero de la extensión en node, con un `vscode` falso: lo abre, le manda los clics que haría una persona
   y avisa que cambió un registro.
   node tests/tablero_en_node.cjs <carpeta de la extensión> <carpeta del proyecto> <mensajes JSON> [factory.comando]
   Imprime JSON: {html, htmlDespues, abiertos, diffs, documentos (su texto entero), errores, terminal, pintadas, historia (cada html que se puso), vigilados (el glob de cada vigía y cuántos avisos de cambio escucha)}. */
'use strict';
const Module = require('module');
const path = require('path');
const [extension, proyecto, mensajesJson, comando] = process.argv.slice(2);
const mensajes = JSON.parse(mensajesJson || '[]');

const terminal = [], historia = [], abiertos = [], diffs = [], documentos = [], errores = [], comandos = {}, vigias = [];
let panel = null, pintadas = 0;
const nada = () => ({dispose() {}});
const vscode = {
    EventEmitter: class { constructor() { this.event = nada; } fire() {} },
    TreeItem: class {}, TreeItemCollapsibleState: {None: 0, Collapsed: 1}, ThemeIcon: class {},
    ViewColumn: {One: 1},
    Uri: {file: p => ({fsPath: p})},
    Range: class { constructor(l, c) { this.start = {line: l, character: c}; } },
    workspace: {
        workspaceFolders: [{uri: {fsPath: proyecto}}],
        getConfiguration: () => ({get: clave => (clave === 'comando' ? comando || '' : clave === 'esperaTerminalMs' ? 0 : undefined)}),
        createFileSystemWatcher: glob => {
            const v = {glob, cambios: [], onDidChange: f => { v.cambios.push(f); return nada(); }, onDidCreate: nada, onDidDelete: nada, dispose() {}};
            vigias.push(v);
            return v;
        },
        openTextDocument: async a => (a && a.content !== undefined ? {contenido: a.content, lenguaje: a.language} : {uri: a}),
    },
    window: {
        terminals: [],
        registerTreeDataProvider: nada,
        createTerminal(opciones) {
            const t = {...opciones, exitStatus: undefined, show() {},
                       sendText: (texto, enter) => terminal.push({texto, enter, cwd: t.cwd})};
            this.terminals.push(t);
            return t;
        },
        showErrorMessage: m => { errores.push(m); },
        showInputBox: async () => process.env.PREGUNTA,  // lo que la persona escribe al preguntar (vacío: cancela)
        showTextDocument: async (doc, opciones) => {
            if (doc.contenido !== undefined) { documentos.push(doc.contenido); return diffs.push({lenguaje: doc.lenguaje, primera: doc.contenido.split('\n')[0]}); }
            abiertos.push({archivo: path.relative(proyecto, doc.uri.fsPath), linea: opciones.selection.start.line + 1});
        },
        createWebviewPanel: () => {
            let html = '', recibir = null;
            panel = {
                webview: {cspSource: 'vscode-resource:', onDidReceiveMessage: f => { recibir = f; return nada(); },
                          get html() { return html; }, set html(h) { html = h; pintadas++; historia.push(h); }},
                onDidDispose: nada, reveal() {},
                recibir: m => recibir(m),
            };
            return panel;
        },
    },
    commands: {registerCommand: (id, f) => { comandos[id] = f; return nada(); }},
};
const requerir = Module.prototype.require;
Module.prototype.require = function (nombre) { return nombre === 'vscode' ? vscode : requerir.apply(this, arguments); };

(async () => {
    require(path.resolve(extension, 'extension.js')).activate({subscriptions: []});
    await comandos['factory.tablero']();
    if (process.env.COMANDO) await comandos[process.env.COMANDO]();  // un comando de la paleta, además del tablero
    const html = panel.webview.html;
    // CONCURRENTE=mensajes: los mensajes se atienden a la vez; CONCURRENTE=registro: además un registro cambia (los vigías avisan) mientras tanto.
    if (process.env.CONCURRENTE) await Promise.all([...mensajes.map(m => panel.recibir(m)), ...(process.env.CONCURRENTE === 'registro' ? vigias.flatMap(v => v.cambios.map(f => f())) : [])]);
    else for (const m of mensajes) await panel.recibir(m);
    // Un registro que cambia (TABLERO_CAMBIO: ruta y contenido nuevo): el vigía avisa y el tablero se vuelve a armar.
    if (process.env.TABLERO_CAMBIO) {
        const {ruta, contenido} = JSON.parse(process.env.TABLERO_CAMBIO);
        require('fs').writeFileSync(ruta, contenido);
    }
    const antes = pintadas;
    for (const v of vigias) for (const f of v.cambios) f();
    for (let i = 0; i < 100 && pintadas === antes; i++) await new Promise(r => setTimeout(r, 50));
    process.stdout.write(JSON.stringify({html, htmlDespues: panel.webview.html, abiertos, diffs, documentos, errores, terminal, pintadas, historia, vigilados: vigias.map(v => ({glob: v.glob, avisan: v.cambios.length}))}));
})().catch(e => { console.error(e); process.exit(1); });
