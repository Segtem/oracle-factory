'use strict';
// Live Share sin dependencias: la API se pide a su extensión como lo hace el paquete `vsls`. Quien comparte publica el
// servicio «oracle-factory» (el tablero, el pedido de escribir un comando, el chat); un invitado lo usa por su proxy.
// Sin la extensión, o sin sesión, todo devuelve «sin sesión» y el tablero sigue como siempre.
const ID_LIVE_SHARE = 'ms-vsliveshare.vsliveshare';
const VERSION_API = '1.0.4753';  // la del paquete vsls que documenta esta API
const SERVICIO = 'oracle-factory';
const ROL = {1: 'anfitrión', 2: 'invitado'};

// El rol, venga como número (la API de vsls) o como texto («Host», «Guest»). Una sesión con id y sin rol conocido es
// la de quien la compartió.
function rolDe(x, conId) {
    if (x === 1 || x === 2) return x;
    const t = String(x == null ? '' : x).toLowerCase();
    if (t === 'host' || t === '1') return 1;
    if (t === 'guest' || t === '2') return 2;
    return conId ? 1 : 0;
}

function nombre(usuario) {
    return (usuario && (usuario.displayName || usuario.userName || usuario.emailAddress)) || 'sin nombre';
}

function enlaceDeLiveShare(texto) {
    let url;
    try { url = new URL(String(texto || '').trim()); } catch (e) { return false; }
    return url.protocol === 'https:' && (url.hostname === 'prod.liveshare.vsengsaas.visualstudio.com'
        || (url.hostname === 'vscode.dev' && url.pathname.startsWith('/liveshare/')));
}

class Sesion {
    // al: {tablero(): Promise<datos>, terminal(comando), mensaje(cambio, texto, de), diff(sha): Promise<texto|null>, cambio()}
    constructor(vscode, al) {
        this.vscode = vscode;
        this.al = al;
        this.api = null;
        this.servicio = null;
        this.proxy = null;
        this.enlace = null;  // el de la sesión que compartimos, para mostrarlo y copiarlo
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
        const s = this.api && this.api.session;
        return s ? rolDe(s.role, s.id) : 0;
    }

    async preparar() {
        this.servicio = this.proxy = null;
        if (this.rol() === 1) {
            this.servicio = await this.api.shareService(SERVICIO);
            if (this.servicio) {
                // Lo que llega de un invitado se valida acá, del lado de quien tiene el proyecto.
                const lista = args => (Array.isArray(args) ? args : []);
                this.servicio.onRequest('tablero', () => this.al.tablero());
                this.servicio.onRequest('terminal', args => typeof lista(args)[0] === 'string' && this.al.terminal(lista(args)[0]));
                // El autor de un mensaje tiene que ser un invitado conectado: Live Share no dice quién hizo el pedido,
                // así que con varios invitados uno podría usar el nombre de otro (no el de quien comparte).
                this.servicio.onRequest('mensaje', args => {
                    const [cambio, texto, de] = lista(args);
                    return this.invitados().includes(de) ? this.al.mensaje(cambio, texto, de) : false;
                });
                this.servicio.onRequest('diff', args => this.al.diff(lista(args)[0]));
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

    // Los botones del tablero para la sesión. Ninguno toca un registro de Factory.
    async instalar() {
        await this.vscode.commands.executeCommand('extension.open', ID_LIVE_SHARE);
    }

    async compartir() {
        if (!this.api) return;
        if (this.rol()) return this.al.cambio();  // ya hay sesión: no se comparte otra vez (Live Share lo rechaza)
        const uri = await this.api.share();  // Live Share avisa y copia el enlace
        this.enlace = uri ? uri.toString() : null;
        this.al.cambio();
    }

    // El enlace de la sesión que compartió el tablero. No se le vuelve a pedir a Live Share: llamar otra vez a share()
    // con una sesión abierta intenta empezar otra, falla y deja la actual a medias (lo vio Brian el 2026-10-20).
    enlaceDeLaSesion() {
        return this.rol() === 1 ? this.enlace : null;
    }

    async terminar() {
        if (this.api && this.rol()) await this.api.end();
        this.enlace = null;
    }

    // Sólo un enlace https de Live Share: el de su servicio o el de vscode.dev.
    async unirse(enlace) {
        if (!this.api || this.rol() || !enlaceDeLiveShare(enlace)) return false;
        await this.api.join(this.vscode.Uri.parse(enlace.trim()));
        return true;
    }

    // Para el tablero: quién está y con qué rol.
    estado() {
        if (!this.api) return {estado: 'sin-live-share'};
        const s = this.api.session;
        const rol = this.rol();
        if (!rol) return {estado: 'sin-sesion'};
        return {estado: 'activa', rol: ROL[rol], yo: nombre(s.user), enlace: rol === 1 ? this.enlace : null,
                otros: (this.api.peers || []).map(p => ({nombre: nombre(p.user), rol: ROL[rolDe(p.role)] || 'invitado'}))};
    }

    // Para el diagnóstico (Output → Oracle Factory): lo que dice Live Share, sin nombres.
    diagnostico() {
        if (!this.api) return 'Live Share: sin API (no está instalado, o no dio la API pedida)';
        const s = this.api.session || {};
        return `Live Share: rol ${JSON.stringify(s.role)} (leído ${this.rol()}), id ${s.id ? 'sí' : 'no'}, ` +
               `${(this.api.peers || []).length} más en la sesión, servicio ${this.servicio ? 'publicado' : 'no'}, ` +
               `proxy ${this.proxy ? (this.proxy.isServiceAvailable ? 'disponible' : 'esperando') : 'no'}`;
    }

    // Para quien comparte, los demás de la sesión son sus invitados (peers no la incluye a ella).
    invitados() {
        return (this.api && this.api.peers || []).map(p => nombre(p.user));
    }

    // Un invitado cuyo servicio todavía no está: espera, no usa el disco local (no tiene el proyecto).
    esInvitado() {
        return this.rol() === 2;
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

module.exports = {Sesion, ID_LIVE_SHARE, SERVICIO, VERSION_API, enlaceDeLiveShare, rolDe};
