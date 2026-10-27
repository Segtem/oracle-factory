/* La extensión de VS Code en node, con un `vscode` falso: arma la vista entera y elige cada próximo paso.
   node tests/vscode_en_node.cjs <carpeta de la extensión> <carpeta del proyecto> [factory.comando]
   Imprime JSON: {arbol, terminal} — el árbol desplegado y lo que recibió la terminal. */
'use strict';
const Module = require('module');
const path = require('path');
const [extension, proyecto, comando] = process.argv.slice(2);

const terminal = [], comandos = {};
let vista = null;
const nada = () => ({dispose() {}});
const vscode = {
    EventEmitter: class { constructor() { this.event = nada; } fire() {} },
    TreeItem: class { constructor(label, estado) { this.label = label; this.collapsibleState = estado; } },
    TreeItemCollapsibleState: {None: 0, Collapsed: 1},
    ThemeIcon: class { constructor(id) { this.id = id; } },
    Uri: {file: p => ({fsPath: p})},
    workspace: {
        workspaceFolders: [{uri: {fsPath: proyecto}}],
        getConfiguration: () => ({get: clave => (clave === 'comando' ? comando || '' : clave === 'esperaTerminalMs' ? 0 : undefined)}),
        createFileSystemWatcher: () => ({onDidChange: nada, onDidCreate: nada, onDidDelete: nada, dispose() {}}),
    },
    window: {
        terminals: [],
        registerTreeDataProvider: (id, p) => { vista = p; return nada(); },
        createTerminal(opciones) {
            const t = {...opciones, exitStatus: undefined, show() {},
                       sendText: (texto, enter) => terminal.push({terminal: t.name, cwd: t.cwd, texto, enter})};
            this.terminals.push(t);
            return t;
        },
    },
    commands: {registerCommand: (id, f) => { comandos[id] = f; return nada(); }},
};
const requerir = Module.prototype.require;
Module.prototype.require = function (nombre) { return nombre === 'vscode' ? vscode : requerir.apply(this, arguments); };

async function desplegar(nodo) {
    const salida = [];
    for (const hijo of await vista.getChildren(nodo)) {
        const item = vista.getTreeItem(hijo);
        const fila = {etiqueta: item.label, descripcion: item.description, icono: item.iconPath && item.iconPath.id,
                      contexto: item.contextValue,
                      [{'vscode.open': 'abre', revealInExplorer: 'muestra'}[item.command && item.command.command] || 'sin']:
                          item.command ? path.relative(proyecto, item.command.arguments[0].fsPath) : undefined};
        delete fila.sin;
        if (item.collapsibleState) fila.hijos = await desplegar(hijo);
        if (item.contextValue === 'paso') comandos['factory.escribirPaso'](hijo);
        salida.push(fila);
    }
    return salida;
}

(async () => {
    require(path.resolve(extension, 'extension.js')).activate({subscriptions: []});
    const arbol = await desplegar(undefined);
    process.stdout.write(JSON.stringify({arbol, terminal, terminales: vscode.window.terminals.length}));
})().catch(e => { console.error(e); process.exit(1); });
