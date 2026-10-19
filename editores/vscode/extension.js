'use strict';
// Pegamento con VS Code: corre la CLI (sin shell) y le pasa el JSON a modelo.js. No decide nada: el próximo
// paso se escribe en la terminal sin Enter y la decisión se toma en el menú de siempre.
const vscode = require('vscode');
const {execFile} = require('child_process');
const fs = require('fs');
const path = require('path');
const modelo = require('./modelo');
const tablero = require('./tablero');
const crypto = require('crypto');

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

// El tablero de comando: un panel que se arma con `oracle-factory tablero --json` y se rehace cuando cambia un registro.
let panel = null;

async function pintarTablero() {
    if (!panel) return;
    const nonce = crypto.randomBytes(16).toString('base64');
    const raiz = carpeta();
    if (!raiz || !fs.existsSync(path.join(raiz, '.factory'))) {
        panel.webview.html = tablero.error('Esta carpeta no es un proyecto de Factory (no tiene .factory/).', {nonce});
        return;
    }
    try {
        panel.webview.html = tablero.html(await correr(raiz, ['tablero', '--json']), {nonce, cspSource: panel.webview.cspSource});
    } catch (e) {
        panel.webview.html = tablero.error(`Factory falló: ${e.message.trim().split('\n').pop()}`, {nonce});
    }
}

// Lo que pide el panel: abrir un archivo del proyecto (nunca uno de afuera) o escribir un comando sin ejecutarlo.
async function mensajeDelTablero(m) {
    const raiz = carpeta();
    if (!m || !raiz) return;
    if (m.tipo === 'abrir' && typeof m.archivo === 'string') {
        // Con los enlaces resueltos: un symlink del proyecto que apunta afuera tampoco se abre, ni una carpeta.
        let destino;
        try {
            const real = fs.realpathSync(raiz);
            destino = fs.realpathSync(path.resolve(raiz, m.archivo));
            if (!destino.startsWith(real + path.sep) || !fs.statSync(destino).isFile()) return;
        } catch (e) { return; }
        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(destino));
        const linea = Number.isInteger(m.linea) && m.linea > 0 ? m.linea - 1 : 0;
        await vscode.window.showTextDocument(doc, {selection: new vscode.Range(linea, 0, linea, 0), preview: false});
    } else if (m.tipo === 'commit' && typeof m.sha === 'string' && /^[0-9a-f]{7,40}$/.test(m.sha)) {
        // El diff del commit en un documento sin guardar: se lee, no cambia nada.
        const diff = await new Promise(ok => execFile('git', ['show', '--stat', '--patch', '--no-color', m.sha, '--'],
            {cwd: raiz, maxBuffer: 32 << 20}, (error, stdout, stderr) => ok(error ? null : stdout)));
        if (diff === null) return vscode.window.showErrorMessage(`Factory: git no encontró el commit ${m.sha}.`);
        const doc = await vscode.workspace.openTextDocument({content: diff, language: 'diff'});
        await vscode.window.showTextDocument(doc, {preview: true});
    } else if (m.tipo === 'terminal' && typeof m.comando === 'string') {
        const comando = modelo.comandoDe(m.comando, cli(raiz));
        if (comando) escribirPaso({comando});
    }
}

function abrirTablero() {
    if (panel) { panel.reveal(); return pintarTablero(); }
    panel = vscode.window.createWebviewPanel('factory.tablero', 'Tablero de Factory', vscode.ViewColumn.One,
                                            {enableScripts: true, retainContextWhenHidden: true});
    panel.webview.onDidReceiveMessage(mensajeDelTablero);
    panel.onDidDispose(() => { panel = null; });
    return pintarTablero();
}

function activate(context) {
    const vista = new Vista();
    const vigia = vscode.workspace.createFileSystemWatcher('**/.factory/cambios/**/factory.json');
    context.subscriptions.push(
        vscode.window.registerTreeDataProvider('factory.cambios', vista),
        vscode.commands.registerCommand('factory.refrescar', () => vista.refrescar()),
        vscode.commands.registerCommand('factory.escribirPaso', escribirPaso),
        vscode.commands.registerCommand('factory.tablero', abrirTablero),
        vigia, vigia.onDidChange(() => refrescar()), vigia.onDidCreate(() => refrescar()),
        vigia.onDidDelete(() => refrescar()));

    function refrescar() {
        vista.refrescar();
        pintarTablero();
    }
}

module.exports = {activate, deactivate() {}};
