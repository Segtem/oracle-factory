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
const {Sesion} = require('./liveshare');

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
// En una sesión de Live Share, un invitado lo pide a quien comparte (ver liveshare.js).
let panel = null;
let sesion = null;
let salida = null;  // Output → Oracle Factory: lo que dice Live Share, para diagnosticar

function anotar(texto) {
    if (salida) salida.appendLine(`${new Date().toISOString()} ${texto}`);
}

function datosLocales() {
    const raiz = carpeta();
    if (!raiz || !fs.existsSync(path.join(raiz, '.factory')))
        return Promise.reject(new Error('Esta carpeta no es un proyecto de Factory (no tiene .factory/).'));
    return correr(raiz, ['tablero', '--json']);
}

let pintura = 0;  // cada pedido de repintar tiene su número: si llega uno más nuevo, el viejo no escribe

async function pintarTablero() {
    if (!panel) return;
    const esta = ++pintura;
    const nonce = crypto.randomBytes(16).toString('base64');
    const invitado = Boolean(sesion && sesion.invitadoConServicio());
    let html;
    if (sesion && sesion.esInvitado() && !invitado) {
        html = tablero.error('Esperando el tablero de quien comparte la sesión de Live Share…', {nonce});
    } else {
        try {
            const datos = invitado ? await sesion.pedir('tablero', []) : await datosLocales();
            // La sesión se lee después de los datos: lo que cambió mientras corría la CLI también se ve.
            const presencia = sesion ? sesion.estado() : {estado: 'sin-live-share'};
            if (sesion) anotar(sesion.diagnostico());
            html = tablero.html({...datos, sesion: {...presencia, invitado}}, {nonce, cspSource: panel.webview.cspSource});
        } catch (e) {
            html = tablero.error(`Factory falló: ${e.message.trim().split('\n').pop()}`, {nonce});
        }
    }
    if (panel && esta === pintura) panel.webview.html = html;
}

function diffLocal(sha) {
    const raiz = carpeta();
    if (!raiz || typeof sha !== 'string' || !/^[0-9a-f]{7,40}$/.test(sha)) return Promise.resolve(null);
    return new Promise(ok => execFile('git', ['show', '--stat', '--patch', '--no-color', sha, '--'],
        {cwd: raiz, maxBuffer: 32 << 20}, (error, stdout) => ok(error ? null : stdout)));
}

// Un comando que viene del panel (propio o de un invitado): sólo `oracle-factory …` de una línea, escrito sin Enter.
// El de un invitado, además, sin operadores de shell: sólo letras, números, espacios y . _ / : = -, como los pasos de
// Factory (un `; rm …` no llega a la terminal de quien comparte).
function escribirComando(texto, deUnInvitado = false) {
    if (deUnInvitado && (typeof texto !== 'string' || !/^[\p{L}\p{N} ._/:=-]+$/u.test(texto))) return false;
    const raiz = carpeta();
    const comando = raiz && modelo.comandoDe(texto, cli(raiz));
    if (comando) escribirPaso({comando});
    return Boolean(comando);
}

// Un mensaje del chat: lo guarda la CLI de quien tiene el proyecto, con el nombre que da Live Share (la CLI valida el
// texto y el nombre; acá sólo el tipo, porque llega de otra máquina).
function guardarMensaje(cambio, texto, de) {
    const raiz = carpeta();
    if (!raiz || typeof cambio !== 'string' || !/^\d{8}-\d{6}-[a-z0-9_-]+$/.test(cambio) || typeof texto !== 'string'
        || typeof de !== 'string')
        return Promise.resolve(false);
    return new Promise(ok => execFile(cli(raiz), ['mensaje', cambio, texto, '--de', de], {cwd: raiz},
        error => ok(!error)));
}

// Lo que pide el panel: abrir un archivo del proyecto (nunca uno de afuera), ver un commit, escribir un comando sin
// ejecutarlo o mandar un mensaje. Un invitado lo hace a través de quien comparte.
async function mensajeDelTablero(m) {
    if (!m) return;
    if (m.tipo === 'sesion' && sesion) {  // los botones de la sesión de Live Share (también para un invitado que espera)
        if (m.accion === 'instalar') await sesion.instalar();
        else if (m.accion === 'compartir') await sesion.compartir();
        else if (m.accion === 'terminar') await sesion.terminar();
        else if (m.accion === 'copiar') {
            const enlace = sesion.enlaceDeLaSesion();
            if (!enlace) {
                if (await sesion.copiarConLiveShare()) return;  // Live Share lo copia y avisa
                return vscode.window.showErrorMessage('Factory: no tengo el enlace de esta sesión; lo copió Live Share al compartirla.');
            }
            await vscode.env.clipboard.writeText(enlace);
            vscode.window.showInformationMessage(`Enlace de la sesión copiado: ${enlace}`);
            pintarTablero();
        }
        else if (m.accion === 'unirse') {
            const enlace = await vscode.window.showInputBox({prompt: 'El enlace de la sesión de Live Share que te pasaron',
                                                             placeHolder: 'https://prod.liveshare.vsengsaas.visualstudio.com/join?…'});
            if (enlace && !(await sesion.unirse(enlace)))
                vscode.window.showErrorMessage('Factory: ese no es un enlace de una sesión de Live Share.');
        }
        return;
    }
    const invitado = Boolean(sesion && sesion.invitadoConServicio());
    if (sesion && sesion.esInvitado() && !invitado) return;  // sin el servicio de quien comparte, nada que hacer
    if (m.tipo === 'abrir' && typeof m.archivo === 'string') {
        const linea = Number.isInteger(m.linea) && m.linea > 0 ? m.linea - 1 : 0;
        let uri;
        if (invitado) {
            // El espacio compartido no es un disco local: sólo rutas relativas que no suben.
            // Ni barras invertidas ni unidades (una ruta de Windows), ni absolutas, ni que suban.
            const normal = path.posix.normalize(m.archivo);
            const carpetas = vscode.workspace.workspaceFolders;
            if (/[\\:]/.test(m.archivo) || path.posix.isAbsolute(normal) || normal === '..' || normal.startsWith('../')
                || !carpetas || !carpetas.length) return;
            uri = vscode.Uri.joinPath(carpetas[0].uri, normal);
        } else {
            const raiz = carpeta();
            if (!raiz) return;
            // Con los enlaces resueltos: un symlink del proyecto que apunta afuera tampoco se abre, ni una carpeta.
            try {
                const real = fs.realpathSync(raiz);
                const destino = fs.realpathSync(path.resolve(raiz, m.archivo));
                if (!destino.startsWith(real + path.sep) || !fs.statSync(destino).isFile()) return;
                uri = vscode.Uri.file(destino);
            } catch (e) { return; }
        }
        const doc = await vscode.workspace.openTextDocument(uri);
        await vscode.window.showTextDocument(doc, {selection: new vscode.Range(linea, 0, linea, 0), preview: false});
    } else if (m.tipo === 'commit' && typeof m.sha === 'string' && /^[0-9a-f]{7,40}$/.test(m.sha)) {
        // El diff del commit en un documento sin guardar: se lee, no cambia nada.
        const diff = invitado ? await sesion.pedir('diff', [m.sha]) : await diffLocal(m.sha);
        if (typeof diff !== 'string') return vscode.window.showErrorMessage(`Factory: git no encontró el commit ${m.sha}.`);
        const doc = await vscode.workspace.openTextDocument({content: diff, language: 'diff'});
        await vscode.window.showTextDocument(doc, {preview: true});
    } else if (m.tipo === 'terminal' && typeof m.comando === 'string') {
        if (invitado) await sesion.pedir('terminal', [m.comando]);
        else escribirComando(m.comando);
    } else if (m.tipo === 'mensaje' && typeof m.cambio === 'string' && typeof m.texto === 'string' && sesion && sesion.yo()) {
        const ok = invitado ? await sesion.pedir('mensaje', [m.cambio, m.texto, sesion.yo()])
            : await guardarMensaje(m.cambio, m.texto, sesion.yo());
        if (!ok) vscode.window.showErrorMessage('Factory: no se pudo guardar el mensaje.');
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
    salida = vscode.window.createOutputChannel ? vscode.window.createOutputChannel('Oracle Factory') : null;
    sesion = new Sesion(vscode, {
        tablero: datosLocales, terminal: comando => escribirComando(comando, true), mensaje: guardarMensaje, diff: diffLocal,
        cambio: () => pintarTablero(),
    });
    sesion.iniciar(context.extension ? context.extension.id : 'cs50-taller.oracle-factory');
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
        sesion.avisarCambio();  // los invitados piden el tablero otra vez
    }
}

module.exports = {activate, deactivate() {}};
