/* Las claves que la extensión de VS Code lee de los JSON de la CLI: corre sus funciones puras (modelo.js y tablero.js) sobre
   la salida real de la CLI, con cada JSON envuelto en un Proxy que anota la ruta de cada lectura.
   node tests/contrato_en_node.cjs <carpeta de la extensión> <carpeta con resumen.json, tablero.json, estado-N.json y donde-N.json>
   Imprime JSON: {resumen, estado, donde, tablero}, cada uno con la lista ordenada de rutas leídas.
   Una ruta: claves separadas por punto, «[]» por cada nivel de arreglo y «.*» para un objeto que se recorre (nombres variables). */
'use strict';
const fs = require('fs');
const path = require('path');
const [extension, carpeta] = process.argv.slice(2);
const IGNORAR = new Set(['toJSON', 'then', 'constructor', 'toString', 'valueOf', 'hasOwnProperty', 'inspect']);

function envolver(valor, ruta, leidas, mapas) {
    if (valor === null || typeof valor !== 'object') return valor;
    const arreglo = Array.isArray(valor);
    return new Proxy(valor, {
        get(t, p, r) {
            if (typeof p === 'symbol') return Reflect.get(t, p, r);
            if (arreglo) {
                if (!/^\d+$/.test(p)) return Reflect.get(t, p, r);  // length, map, filter…
                leidas.add(`${ruta}[]`);
                return envolver(t[p], `${ruta}[]`, leidas, mapas);
            }
            if (IGNORAR.has(p)) return Reflect.get(t, p, r);
            const hija = mapas.has(ruta) ? `${ruta}.*` : (ruta ? `${ruta}.${p}` : p);
            leidas.add(hija);
            return envolver(t[p], hija, leidas, mapas);
        },
        ownKeys(t) {
            if (!arreglo) mapas.add(ruta);  // recorrer las claves: sus nombres no son parte del contrato
            return Reflect.ownKeys(t);
        },
    });
}

function leer(nombre) { return JSON.parse(fs.readFileSync(path.join(carpeta, nombre), 'utf8')); }
const modelo = require(path.join(extension, 'modelo.js'));
const tablero = require(path.join(extension, 'tablero.js'));
const leidas = {resumen: new Set(), estado: new Set(), donde: new Set(), tablero: new Set()};
const mapas = new Set();
const proxy = (clave, valor) => envolver(valor, '', leidas[clave], mapas);

modelo.raiz(proxy('resumen', leer('resumen.json')));
const cambios = fs.readdirSync(carpeta).filter(n => /^estado-\d+\.json$/.test(n)).sort();
for (const n of cambios) {
    modelo.hijosCambio(proxy('estado', leer(n)), proxy('donde', leer(n.replace('estado', 'donde'))), 'oracle-factory', () => 'archivo');
}
const datos = proxy('tablero', leer('tablero.json'));
// La extensión le agrega `sesion` (de Live Share): no viene de la CLI.
tablero.html(new Proxy(datos, {get: (t, p, r) => (p === 'sesion' ? {estado: 'sin-live-share'} : Reflect.get(t, p, r))}),
             {nonce: 'n', cspSource: 'vscode-resource:'});
const salida = {};
for (const [clave, conjunto] of Object.entries(leidas)) salida[clave] = [...conjunto].sort();
process.stdout.write(JSON.stringify(salida));
