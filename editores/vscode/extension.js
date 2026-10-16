'use strict';
// Pegamento con VS Code: corre la CLI (sin shell) y le pasa el JSON a modelo.js. No decide nada: el próximo
// paso se escribe en la terminal sin Enter y la decisión se toma en el menú de siempre.
const vscode = require('vscode');
const {execFile} = require('child_process');
const fs = require('fs');
const path = require('path');
const modelo = require('./modelo');

function carpeta() {
    // ponytail: la primera carpeta del espacio de trabajo; multi-raíz cuando haga falta.
    const f = vscode.workspace.workspaceFolders;
    return f && f.length ? f[0].uri.fsPath : null;
}

function cli(raiz) {
    const elegido = vscode.workspace.getConfiguration('factory').get('comando');
    if (elegido) return elegido;
    const local = path.join(raiz, '.venv', 'bin', 'oracle-factory');
    return fs.existsSync(local) ? local : 'oracle-factory';
}

function correr(raiz, args) {
    return new Promise((ok, mal) => execFile(cli(raiz), args, {cwd: raiz, maxBuffer: 32 << 20}, (error, stdout, stderr) => {
        if (error) return mal(new Error((stderr || '').trim() || error.message));
        try { ok(JSON.parse(stdout)); } catch (e) { mal(new Error(`la CLI no devolvió JSON: ${e.message}`)); }
    }));
}

function tipo(raiz) {
    return ruta => {
        try {
            const s = fs.statSync(path.resolve(raiz, ruta));
            return s.isFile() ? 'archivo' : s.isDirectory() ? 'carpeta' : null;
        } catch (e) { return null; }
    };
}

function aviso(etiqueta, icono, tooltip) {
    return [{etiqueta, icono, tooltip}];
}

class Vista {
    constructor() {
        this._cambio = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._cambio.event;
    }

    refrescar() { this._cambio.fire(); }

    async getChildren(nodo) {
        if (nodo && nodo.hijos) return nodo.hijos;
        const raiz = carpeta();
        if (!raiz || !fs.existsSync(path.join(raiz, '.factory')))
            return aviso('Esta carpeta no es un proyecto de Factory (no tiene .factory/)', 'info');
        try {
            if (!nodo) return modelo.raiz(await correr(raiz, ['resumen', '--json']));
            const [estado, donde] = await Promise.all([correr(raiz, ['estado', nodo.cambio, '--json']),
                                                       correr(raiz, ['donde', nodo.cambio, '--json'])]);
            return modelo.hijosCambio(estado, donde, cli(raiz), tipo(raiz));
        } catch (e) {
            // La última línea: la de un error de la CLI, o la de su traceback.
            return aviso(`Factory falló: ${e.message.trim().split('\n').pop()}`, 'error', e.message);
        }
    }

    getTreeItem(nodo) {
        const C = vscode.TreeItemCollapsibleState;
        const item = new vscode.TreeItem(nodo.etiqueta, (nodo.hijos && nodo.hijos.length) || nodo.cambio ? C.Collapsed : C.None);
        item.description = nodo.descripcion;
        item.tooltip = nodo.tooltip;
        if (nodo.icono) item.iconPath = new vscode.ThemeIcon(nodo.icono);
        if (nodo.comando) item.contextValue = 'paso';
        if (nodo.abrir) item.command = {command: 'vscode.open', title: 'Abrir',
                                        arguments: [vscode.Uri.file(path.resolve(carpeta(), nodo.abrir))]};
        else if (nodo.mostrar) item.command = {command: 'revealInExplorer', title: 'Mostrar en el explorador',
                                               arguments: [vscode.Uri.file(path.resolve(carpeta(), nodo.mostrar))]};
        return item;
    }
}

function escribirPaso(nodo) {
    if (!nodo || !nodo.comando) return;
    const terminal = vscode.window.terminals.find(t => t.name === 'Factory' && t.exitStatus === undefined)
        || vscode.window.createTerminal({name: 'Factory', cwd: carpeta()});
    terminal.show();
    terminal.sendText(nodo.comando, false);  // sin Enter: la persona lo lee y lo ejecuta
}

function activate(context) {
    const vista = new Vista();
    const vigia = vscode.workspace.createFileSystemWatcher('**/.factory/cambios/**/factory.json');
    context.subscriptions.push(
        vscode.window.registerTreeDataProvider('factory.cambios', vista),
        vscode.commands.registerCommand('factory.refrescar', () => vista.refrescar()),
        vscode.commands.registerCommand('factory.escribirPaso', escribirPaso),
        vigia, vigia.onDidChange(() => vista.refrescar()), vigia.onDidCreate(() => vista.refrescar()),
        vigia.onDidDelete(() => vista.refrescar()));
}

module.exports = {activate, deactivate() {}};
