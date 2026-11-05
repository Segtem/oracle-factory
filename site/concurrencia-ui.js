/* La página de la simulación: dibuja el estado del motor (concurrencia.js) con los sprites de pixel.js. */
(function () {
  'use strict';
  var C = window.Concurrencia, P = window.Pixel, K = P.PALETA;
  var quieto = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  var $ = function (id) { return document.getElementById(id); };
  var e = null, reloj = null, escena = null;

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]; }); }
  function r(x, y, w, h, c, extra) { return '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" fill="' + c + '"' + (extra || '') + '/>'; }
  function t(x, y, s, clase) { return '<text x="' + x + '" y="' + y + '" class="' + (clase || 'sim-t') + '">' + esc(s) + '</text>'; }

  function fichas(archivos, base, x0, y, resalta) {
    var s = '', i = 0;
    Object.keys(archivos).sort().forEach(function (f) {
      if (base && archivos[f] === base[f]) return;
      var mal = resalta === f;
      s += r(x0 + i * 52, y, 48, 11, mal ? K.r : K.y, ' stroke="' + K.k + '" stroke-width="1"') + t(x0 + i * 52 + 3, y + 8, f, 'sim-t sim-chip') ;
      i++;
    });
    return s;
  }
  function dibujar() {
    var ultimo = e.registro[e.registro.length - 1], activo = ultimo ? ultimo.quien : null;
    var mal = e.espera && e.espera.tipo === 'conflicto' ? e.espera.archivo : null;
    var s = r(0, 0, 320, 160, '#e7f0dc');
    // main: el tronco
    s += t(6, 18, 'main', 'sim-t sim-rotulo') + r(34, 15, 280, 3, K.k) + fichas(e.tronco.archivos, {'app.py': 'base'}, 40, 21, mal);
    s += P.g('oracle', 296, 4, '');
    [['ana', 'Ana', 'agente', 'claude-code', 58], ['beto', 'Beto', 'codex', 'codex', 110]].forEach(function (l) {
      var rama = e.ramas[l[0]], y = l[4];
      s += r(34, y + 14, 280, 2, K.G) + t(6, y + 30, 'rama «' + l[0] + '»', 'sim-t');
      s += '<g class="sim-actor' + (activo === l[1] ? ' activo' : '') + '">' + P.g('persona', 4, y - 2, '') + '</g>';
      s += '<g class="sim-actor' + (activo === l[3] ? ' activo' : '') + '">' + P.g(l[2], 20, y - 2, '') + '</g>';
      s += fichas(rama.archivos, rama.base, 40, y + 17, mal);
      var x = 40;
      Object.keys(rama.revisiones).forEach(function (c) {
        var v = rama.revisiones[c];
        s += r(x + 120, y + 2, 66, 10, v.vigente ? K.g : K.r, ' stroke="' + K.k + '"') + t(x + 123, y + 9.5, 'revisión ' + (v.vigente ? 'vale' : 'vieja'), 'sim-t sim-chip');
      });
    });
    if (e.espera) s += '<g class="sim-alerta">' + r(150, 78, 20, 20, K.r, ' stroke="' + K.k + '"') + t(156, 92, '!', 'sim-t sim-rotulo') + '</g>';
    escena.innerHTML = '<svg viewBox="0 0 320 160" shape-rendering="crispEdges" preserveAspectRatio="xMidYMid meet" focusable="false" aria-hidden="true">' + s + '</svg>';
    escena.setAttribute('aria-label', 'Paso ' + e.registro.length + ' de la simulación' + (ultimo ? ': ' + ultimo.que : ': todavía no pasó nada'));
  }

  function registro() {
    var li = e.registro.map(function (x) {
      return '<li class="sim-' + x.tipo + '"><span class="sim-quien">' + esc(x.quien) + ' <small>(' + esc(x.tipo) + ')</small></span> ' + esc(x.que) + '</li>';
    }).join('');
    $('sim-registro').innerHTML = li;
    var ul = $('sim-registro').lastElementChild; if (ul && !quieto && ul.scrollIntoView) { /* sin saltos de página */ }
  }
  function espera() {
    var w = e.espera, caja = $('sim-espera');
    caja.hidden = !w;
    $('sim-paso').disabled = !!w || !!e.fin; $('sim-play').disabled = !!w || !!e.fin;
    if (!w) return;
    parar();
    $('sim-espera-texto').textContent = w.texto;
    $('sim-espera-comando').textContent = w.comando || '';
    $('sim-espera-comando').parentNode.hidden = !w.comando;
    $('sim-espera-opciones').innerHTML = w.opciones.map(function (o) { return '<button type="button" data-op="' + esc(o.id) + '">' + esc(o.texto) + '</button>'; }).join('');
  }
  function fin() {
    var f = $('sim-fin');
    f.hidden = !e.fin;
    if (e.fin) { f.textContent = 'Final: ' + e.fin.explicacion; parar(); }
    $('sim-paso').disabled = !!e.fin || !!e.espera; $('sim-play').disabled = !!e.fin || !!e.espera;
  }
  function pintar() { dibujar(); registro(); espera(); fin(); }

  function parar() {
    if (reloj) { clearInterval(reloj); reloj = null; }
    $('sim-play').setAttribute('aria-pressed', 'false'); $('sim-play').textContent = 'Reproducir';
  }
  function paso() { C.paso(e); pintar(); }
  function reproducir() {
    if (reloj) { parar(); return; }
    $('sim-play').setAttribute('aria-pressed', 'true'); $('sim-play').textContent = 'Pausar';
    reloj = setInterval(function () { if (e.fin || e.espera) { parar(); return; } paso(); }, +$('sim-vel').value);
  }
  function semilla() { var n = parseInt($('sim-semilla').value, 10); return n >= 1 && n <= 999 ? n : 1; }
  function reiniciar() {
    parar();
    e = C.nuevo($('sim-escenario').value, semilla());
    var x = C.ESCENARIOS.filter(function (z) { return z.id === e.escenario; })[0];
    $('sim-resumen').textContent = x.resumen;
    var nota = $('sim-nota');
    if (quieto) {
      // Con movimiento reducido no hay animación: se muestra el final. Donde el escenario espera a una persona, la
      // simulación elige por ella la primera opción, y lo dice.
      var elegidas = 0;
      while (!e.fin) { if (e.espera) { C.elegir(e, e.espera.opciones[0].id); elegidas++; } else C.paso(e); }
      nota.hidden = !elegidas;
      nota.textContent = elegidas ? 'Con movimiento reducido la simulación muestra el final de una vez. En ' + elegidas + ' paso(s) una persona tenía que elegir: acá eligió la primera opción. Con "Reiniciar" y "Un paso" podés recorrerlo vos.' : '';
    } else nota.hidden = true;
    pintar();
  }
  function reglas() {
    $('sim-reglas').innerHTML = C.REGLAS.map(function (x) {
      return '<dt id="regla-' + x.id + '">' + esc(x.texto) + '</dt><dd>La guía dice: «<q>' + esc(x.cita) + '</q>».</dd>';
    }).join('');
  }
  function iniciar() {
    escena = $('sim-escena');
    $('sim-escenario').innerHTML = C.ESCENARIOS.map(function (x) { return '<option value="' + x.id + '">' + esc(x.titulo) + '</option>'; }).join('');
    $('sim-escenario').addEventListener('change', reiniciar);
    $('sim-semilla').addEventListener('change', reiniciar);
    $('sim-vel').addEventListener('change', function () { if (reloj) { parar(); reproducir(); } });
    $('sim-paso').addEventListener('click', paso);
    $('sim-play').addEventListener('click', reproducir);
    $('sim-reiniciar').addEventListener('click', reiniciar);
    $('sim-espera-opciones').addEventListener('click', function (ev) {
      var b = ev.target.closest('button[data-op]');
      if (!b) return;
      C.elegir(e, b.getAttribute('data-op'));
      pintar();
      $('sim-paso').focus();
    });
    reglas();
    reiniciar();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})();
