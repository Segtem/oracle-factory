/* «¿Por qué existe esta línea?» en la extensión, con un `vscode` falso: un editor abierto en ARCHIVO con el cursor en
   LÍNEA. node tests/porque_en_node.cjs <carpeta de la extensión> <proyecto> <oracle-factory> <archivo> <línea>
   Imprime JSON: {documentos: [{lenguaje, contenido}], errores}. */
'use strict';
const Module = require('module');
const path = require('path');
const [extension, proyecto, cliRuta, archivo, linea] = process.argv.slice(2);
const nada = () => ({dispose() {}});
const documentos = [], errores = [], comandos = {};
const vscode = {
    EventEmitter: class { constructor() { this.event = nada; } fire() {} },
    TreeItem: class {}, TreeItemCollapsibleState: {None: 0, Collapsed: 1}, ThemeIcon: class {}, ViewColumn: {One: 1},
    Uri: {file: p => ({fsPath: p})}, Range: class {},
    workspace: {
        workspaceFolders: [{uri: {fsPath: proyecto}}],
        getConfiguration: () => ({get: clave => (clave === 'comando' ? cliRuta : clave === 'esperaTerminalMs' ? 0 : undefined)}),
        createFileSystemWatcher: () => ({onDidChange: nada, onDidCreate: nada, onDidDelete: nada, dispose() {}}),
        openTextDocument: async a => a,
    },
    window: {
        terminals: [], registerTreeDataProvider: nada,
        activeTextEditor: {document: {uri: {fsPath: path.resolve(proyecto, archivo)}}, selection: {active: {line: Number(linea) - 1}}},
        showErrorMessage: m => { errores.push(m); },
        showTextDocument: async doc => { documentos.push({lenguaje: doc.language, contenido: doc.content}); },
    },
    commands: {registerCommand: (id, f) => { comandos[id] = f; return nada(); }},
};
const requerir = Module.prototype.require;
Module.prototype.require = function (n) { return n === 'vscode' ? vscode : requerir.apply(this, arguments); };
(async () => {
    require(path.resolve(extension, 'extension.js')).activate({subscriptions: [], extension: {id: 'cs50-taller.oracle-factory'}});
    await comandos['factory.porQue']();
    process.stdout.write(JSON.stringify({documentos, errores}));
})().catch(e => { console.error(e); process.exit(1); });
