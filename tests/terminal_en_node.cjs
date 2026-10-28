/* La terminal «Factory» de la extensión en node, con un `vscode` falso que deja decidir cuándo avisa que su shell está lista.
   node tests/terminal_en_node.cjs <carpeta de la extensión> <carpeta del proyecto> <escenario JSON>
   escenario: {espera: ms de factory.esperaTerminalMs (omitido: sin configurar), evento: false si esta versión de VS Code no
   tiene onDidChangeTerminalShellIntegration, existente: true si ya hay una terminal «Factory», existente_cerrada: true si hay una «Factory» ya cerrada, integracion: true si las
   terminales nuevas ya informan su integración, falla_crear: true si el primer createTerminal lanza un error, nace_cerrada: true si la primera terminal nace ya cerrada, pasos: [{escribir: comando} | {esperar: ms} | {avisar: true} | {avisar_otra: true} | {cerrar: true} | {cerrar_sin_estado: true} | {cerrar_otra: true} | {pedir: texto, invitado} | {foto: nombre}]}
   Imprime JSON: {fotos: {nombre: [lo que recibió cada terminal]}, terminales (cuántas se crearon), salida (el canal «Oracle Factory»)}. */
'use strict';
const Module = require('module');
const path = require('path');
const [extension, proyecto, escenarioJson] = process.argv.slice(2);
const escenario = JSON.parse(escenarioJson);

const resultados = [];
const recibido = [], salida = [], errores = [], comandos = {}, oyentes = [], cierres = [];
let suscripciones = 0, liberadas = 0, creadas = 0;
const nada = () => ({dispose() {}});
const nueva = nombre => {
    const t = {name: nombre, exitStatus: undefined, show() {}, sendText: (texto, enter) => recibido.push({terminal: t.id, texto, enter})};
    t.id = creadas++;
    vscode.window.terminals.push(t);
    return t;
};
const window = {
    terminals: [],
    registerTreeDataProvider: nada,
    createOutputChannel: () => ({appendLine: l => salida.push(l)}),
    createTerminal(opciones) {
        if (escenario.falla_crear && !window.fallo) { window.fallo = true; throw new Error('no se pudo crear la terminal'); }
        const t = nueva(opciones.name);
        if (escenario.nace_cerrada && !window.nacio) { window.nacio = true; t.exitStatus = {code: 1}; }
        if (escenario.integracion) t.shellIntegration = {};
        return t;
    },
};
window.onDidCloseTerminal = f => { cierres.push(f); return {dispose() { if (cierres.includes(f)) cierres.splice(cierres.indexOf(f), 1); }}; };
if (escenario.evento !== false)
    window.onDidChangeTerminalShellIntegration = f => {
        oyentes.push(f); suscripciones++;
        return {dispose() { liberadas++; if (oyentes.includes(f)) oyentes.splice(oyentes.indexOf(f), 1); }};
    };
const vscode = {
    EventEmitter: class { constructor() { this.event = nada; } fire() {} },
    TreeItem: class {}, TreeItemCollapsibleState: {None: 0, Collapsed: 1}, ThemeIcon: class {},
    Uri: {file: p => ({fsPath: p})},
    workspace: {
        workspaceFolders: [{uri: {fsPath: proyecto}}],
        getConfiguration: () => ({get: clave => (clave === 'esperaTerminalMs' ? escenario.espera : undefined)}),
        createFileSystemWatcher: () => ({onDidChange: nada, onDidCreate: nada, onDidDelete: nada, dispose() {}}),
    },
    window,
    commands: {registerCommand: (id, f) => { comandos[id] = f; return nada(); }},
};
const requerir = Module.prototype.require;
Module.prototype.require = function (nombre) { return nombre === 'vscode' ? vscode : requerir.apply(this, arguments); };

(async () => {
    const modulo = require(path.resolve(extension, 'extension.js'));
    modulo.activate({subscriptions: []});
    if (escenario.existente) nueva('Factory');
    if (escenario.existente_cerrada) { nueva('Factory').exitStatus = {code: 0}; }
    const fotos = {};
    for (const paso of escenario.pasos) {
        if (paso.pedir !== undefined) resultados.push(await modulo.escribirComando(paso.pedir, Boolean(paso.invitado)));
        else if (paso.escribir) comandos['factory.escribirPaso']({comando: paso.escribir}).catch(e => errores.push(e.message));
        else if (paso.esperar !== undefined) await new Promise(r => setTimeout(r, paso.esperar));
        else if (paso.cerrar_sin_estado) { const t = window.terminals.pop(); for (const f of [...cierres]) f(t); }  // como VS Code: sale de la lista y no define exitStatus
        else if (paso.cerrar) { const t = window.terminals.pop(); t.exitStatus = {code: 1}; for (const f of [...cierres]) f(t); }
        else if (paso.cerrar_otra) for (const f of [...cierres]) f({name: 'otra'})
        else if (paso.avisar_otra) for (const f of [...oyentes]) f({terminal: {name: 'otra'}})
        else if (paso.avisar) for (const f of [...oyentes]) f({terminal: window.terminals[window.terminals.length - 1]});
        else if (paso.foto) fotos[paso.foto] = JSON.parse(JSON.stringify(recibido));
        await new Promise(r => setImmediate(r));
    }
    process.stdout.write(JSON.stringify({fotos, terminales: creadas, salida, errores, resultados, suscripciones, liberadas}));
    process.exit(0);
})().catch(e => { console.error(e); process.exit(1); });
