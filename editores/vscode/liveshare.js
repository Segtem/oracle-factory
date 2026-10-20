'use strict';
// Live Share sin dependencias: la API se pide a su extensión como lo hace el paquete `vsls`. Quien comparte publica el
// servicio «oracle-factory» (el tablero, el pedido de escribir un comando, el chat); un invitado lo usa por su proxy.
// Sin la extensión, o sin sesión, todo devuelve «sin sesión» y el tablero sigue como siempre.
const ID_LIVE_SHARE = 'ms-vsliveshare.vsliveshare';
const VERSION_API = '1.0.4753';  // la del paquete vsls que documenta esta API
const SERVICIO = 'oracle-factory';
const ROL = {1: 'anfitrión', 2: 'invitado'};

function nombre(usuario) {
    return (usuario && (usuario.displayName || usuario.userName || usuario.emailAddress)) || 'sin nombre';
}

class Sesion {
    // al: {tablero(): Promise<datos>, terminal(comando), mensaje(cambio, texto, de), diff(sha): Promise<texto|null>, cambio()}
    constructor(vscode, al) {
        this.vscode = vscode;
        this.al = al;
        this.api = null;
        this.servicio = null;
        this.proxy = null;
    }

    async iniciar(idExtension) {
        const ext = this.vscode.extensions && this.vscode.extensions.getExtension(ID_LIVE_SHARE);
        if (!ext) return;
        try {
            const exportada = ext.isActive ? ext.exports : await ext.activate();
            this.api = exportada && exportada.getApi ? await exportada.getApi(VERSION_API, idExtension) : null;
        } catch (e) {
            this.api = null;
        }
        if (!this.api) return;
        this.api.onDidChangeSession(() => this.preparar());
        this.api.onDidChangePeers(() => this.al.cambio());
        await this.preparar();
    }

    rol() {
        return (this.api && this.api.session && this.api.session.role) || 0;
    }

    async preparar() {
        this.servicio = this.proxy = null;
        if (this.rol() === 1) {
            this.servicio = await this.api.shareService(SERVICIO);
            if (this.servicio) {
                // Lo que llega de un invitado se valida acá, del lado de quien tiene el proyecto.
                this.servicio.onRequest('tablero', () => this.al.tablero());
                this.servicio.onRequest('terminal', ([comando]) => typeof comando === 'string' && this.al.terminal(comando));
                this.servicio.onRequest('mensaje', ([cambio, texto, de]) => this.al.mensaje(cambio, texto, de));
                this.servicio.onRequest('diff', ([sha]) => this.al.diff(sha));
            }
        } else if (this.rol() === 2) {
            this.proxy = await this.api.getSharedService(SERVICIO);
            if (this.proxy) {
                this.proxy.onNotify('cambio', () => this.al.cambio());
                this.proxy.onDidChangeIsServiceAvailable(() => this.al.cambio());
            }
        }
        this.al.cambio();
    }

    // Para el tablero: quién está y con qué rol.
    estado() {
        if (!this.api) return {estado: 'sin-live-share'};
        const s = this.api.session;
        if (!s || !s.role) return {estado: 'sin-sesion'};
        return {estado: 'activa', rol: ROL[s.role], yo: nombre(s.user),
                otros: (this.api.peers || []).map(p => ({nombre: nombre(p.user), rol: ROL[p.role] || 'invitado'}))};
    }

    yo() {
        return this.api && this.api.session ? nombre(this.api.session.user) : null;
    }

    invitadoConServicio() {
        return this.rol() === 2 && this.proxy && this.proxy.isServiceAvailable;
    }

    pedir(nombre_, args) {
        return this.proxy.request(nombre_, args);
    }

    avisarCambio() {
        if (this.servicio) this.servicio.notify('cambio', {});
    }
}

module.exports = {Sesion, ID_LIVE_SHARE, SERVICIO, VERSION_API};
