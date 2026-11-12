/* La extensión de VS Code en node, con un `vscode` falso: arma la vista entera y elige cada próximo paso.
   node tests/vscode_en_node.cjs <carpeta de la extensión> <carpeta del proyecto> [factory.comando]
   Imprime JSON: {arbol, terminal} — el árbol desplegado y lo que recibió la terminal. */
'use strict';
const Module = require('module');
const path = require('path');
const [extension, proyecto, comando] = process.argv.slice(2);

const terminal = [], comandos = {}, vigias = [];  // vigias: lo que la extensión pidió vigilar (etapa 5b)
let vista = null;
const nada = () => ({dispose() {}});
const vscode = {
    EventEmitter: class { constructor() { this.event = nada; } fire() {} },
    TreeItem: class { constructor(label, estado) { this.label = label; this.collapsibleState = estado; } },
    TreeItemCollapsibleState: {None: 0, Collapsed: 1},
    ThemeIcon: class { constructor(id) { this.id = id; } },
    Uri: {file: p => ({fsPath: p})},
    // SIN_RELATIVE_PATTERN=1: un editor que no deja vigilar fuera del espacio de trabajo (como el vscode falso de terminal_en_node.cjs)
    RelativePattern: process.env.SIN_RELATIVE_PATTERN ? undefined
        : class { constructor(base, patron) { this.base = base && base.fsPath ? base.fsPath : base; this.pattern = patron; } },
    workspace: {
        workspaceFolders: [{uri: {fsPath: proyecto}}],
        getConfiguration: () => ({get: clave => (clave === 'comando' ? comando || '' : clave === 'esperaTerminalMs' ? 0 : undefined)}),
        createFileSystemWatcher: patron => { vigias.push(typeof patron === 'string' ? patron : {base: patron.base, patron: patron.pattern});
                                             return {onDidChange: nada, onDidCreate: nada, onDidDelete: nada, dispose() {}}; },
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
    const modulo = require(path.resolve(extension, 'extension.js'));
    modulo.activate({subscriptions: []});
    const arbol = await desplegar(undefined);
    if (modulo.vigilando) await modulo.vigilando();  // los vigías del almacén se arman cuando se sabe dónde está
    process.stdout.write(JSON.stringify({arbol, terminal, terminales: vscode.window.terminals.length, vigias}));
})().catch(e => { console.error(e); process.exit(1); });
