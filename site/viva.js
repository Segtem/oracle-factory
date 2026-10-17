/* La portada viva: escenas de pixel art que se animan al entrar en pantalla, personajes, el minijuego y los
   easter eggs. Con movimiento reducido nada se anima: cada escena muestra su estado final. */
(function () {
  'use strict';
  var P = window.Pixel, J = window.Juego;
  var quieto = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var C = P.PALETA;

  function r(x, y, w, h, color, extra) {
    return '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" fill="' + color + '"' + (extra || '') + '/>';
  }
  function marco(ancho, alto, cuerpo) {
    return '<svg viewBox="0 0 ' + ancho + ' ' + alto + '" shape-rendering="crispEdges" preserveAspectRatio="xMidYMid meet" aria-hidden="true" focusable="false">' + cuerpo + '</svg>';
  }
  function suelo(ancho, y) {
    return r(0, y, ancho, 2, C.G) + r(0, y + 2, ancho, 6, C.h);
  }
  function nube(x, y, clase) {
    return '<g class="' + clase + '">' + r(x + 3, y, 10, 2, C.w) + r(x, y + 2, 18, 3, C.w) + r(x + 2, y + 5, 12, 1, C.l) + '</g>';
  }

  // ---- las escenas, una por sección -----------------------------------------------------------------------
  var ESCENAS = {
    inicio: function () {
      var ventanas = '';
      for (var i = 0; i < 5; i++) ventanas += r(76 + i * 18, 52, 8, 6, C.y, ' class="ventana" style="--i:' + i + '"');
      var cinta = '';
      for (var j = 0; j < 30; j++) cinta += r(j * 8, 83, 4, 1, C.c);
      return marco(240, 96,
        r(0, 0, 240, 96, '#e7f0dc') + r(208, 8, 12, 12, C.y) + r(206, 10, 16, 8, C.y) +
        nube(20, 10, 'nube') + nube(120, 4, 'nube lenta') +
        '<g class="humo" id="humo"></g>' +
        // la chimenea larga: un botón escondido
        '<g class="chimenea" id="chimenea" tabindex="0" role="button" aria-label="Chimenea larga de la fábrica">' +
        r(150, 10, 10, 30, C.k) + r(151, 11, 8, 29, C.c) + r(149, 8, 12, 3, C.k) + '</g>' +
        r(84, 26, 8, 14, C.k) + r(85, 27, 6, 13, C.c) +
        // el edificio con techo de sierra
        r(64, 40, 112, 38, C.k) + r(66, 42, 108, 36, C.h) +
        r(64, 34, 16, 6, C.k) + r(80, 30, 2, 10, C.k) + r(96, 34, 16, 6, C.k) + r(112, 30, 2, 10, C.k) +
        r(128, 34, 16, 6, C.k) + r(144, 30, 2, 10, C.k) + r(160, 34, 16, 6, C.k) +
        r(92, 44, 56, 6, C.k) + r(94, 45, 52, 4, C.d) +
        '<text x="120" y="48.6" text-anchor="middle" class="cartel">ORACLE FACTORY</text>' +
        ventanas + r(114, 64, 12, 14, C.k) + r(116, 66, 8, 12, C.Y) +
        // el gato en el techo: otro botón escondido
        '<g class="gato" id="gato" tabindex="0" role="button" aria-label="Gato de la fábrica">' + P.g('gato', 98, 18, '') + '</g>' +
        '<g class="confeti" id="confeti"></g>' +
        // la cinta y la caja que viaja
        r(0, 80, 240, 3, C.k) + '<g class="cinta">' + cinta + '</g>' + r(0, 84, 240, 2, C.k) +
        P.g('caja', 0, 66, 'viaja') +
        P.g('persona', 10, 64, 'quien saluda') + P.g('agente', 196, 64, 'quien trabaja') +
        suelo(240, 86) + r(0, 94, 240, 2, C.k));
    },
    formas: function () {
      var carriles = '';
      ['#d9d2c4', '#cfe3c4', '#c4dde4', '#e4e9d4'].forEach(function (color, i) {
        var y = 4 + i * 11;
        carriles += r(10, y + 6, 220, 2, C.c) + r(10, y, 220, 6, color);
        if (i === 3) for (var k = 0; k < 4; k++) carriles += r(60 + k * 44, y - 1, 4, 4, C.Y, ' class="parada"');
        carriles += '<g class="viajero v' + i + '">' + r(12, y, 6, 6, C.n) + r(14, y, 2, 6, C.Y) + '</g>';
      });
      return marco(240, 48, carriles + r(226, 2, 4, 44, C.k) + r(230, 2, 8, 4, C.g));
    },
    herramientas: function () {
      var cuerpo = r(8, 38, 224, 4, C.N) + r(8, 42, 224, 2, C.k);
      ['openspec', 'task', 'agente', 'clue', 'oracle', 'persona'].forEach(function (n, i) {
        cuerpo += P.g(n, 22 + i * 36, 20, 'salta', ' style="--i:' + i + '"');
      });
      return marco(240, 48, cuerpo);
    },
    elenco: function () {
      var cuerpo = suelo(240, 38);
      ['persona', 'agente', 'codex', 'agy', 'oracle', 'clue'].forEach(function (n, i) {
        cuerpo += P.g(n, 20 + i * 36, 21, 'salta', ' style="--i:' + i + '"');
      });
      return marco(240, 48, cuerpo);
    },
    jugar: function () {
      return marco(240, 48, suelo(240, 38) + P.g('persona', 70, 21, 'quien saluda') +
        '<g class="parpadea">' + P.g('pantalla', 100, 18, '') + '</g>' + P.g('agente', 140, 21, 'quien trabaja') +
        P.g('oracle', 180, 21, 'luz'));
    },
    criterio: function () {
      var cuerpo = r(0, 36, 240, 3, C.Y) + suelo(240, 39);
      for (var i = 0; i < 4; i++) cuerpo += P.g('bandera', 34 + i * 48, 22, 'sube', ' style="--i:' + i + '"');
      return marco(240, 48, cuerpo + P.g('persona', 4, 22, 'camina'));
    },
    novedades: function () {
      return marco(240, 48, suelo(240, 38) +
        '<g class="tapa">' + r(98, 22, 44, 4, C.N) + r(98, 22, 44, 1, C.k) + '</g>' +
        r(100, 26, 40, 14, C.n) + r(100, 26, 40, 1, C.k) + r(118, 26, 4, 14, C.Y) +
        P.g('pantalla', 78, 10, 'brota', ' style="--i:0"') + P.g('bandera', 112, 4, 'brota', ' style="--i:1"') +
        P.g('clue', 146, 10, 'brota', ' style="--i:2"'));
    },
    trabajar: function () {
      return marco(240, 48, r(60, 38, 120, 4, C.N) + r(64, 42, 4, 6, C.N) + r(172, 42, 4, 6, C.N) +
        P.g('pantalla', 100, 23, '') + r(108, 30, 1, 2, C.g, ' class="cursor"') +
        P.g('persona', 70, 22, 'quien') + P.g('agente', 140, 22, 'quien trabaja'));
    }
  };

  function pintar(el) {
    var f = ESCENAS[el.dataset.escena];
    if (!f) return;
    el.innerHTML = f();
    el.dataset.estado = quieto ? 'final' : 'quieta';
  }

  // ---- personajes con nombre ------------------------------------------------------------------------------
  function personajes() {
    document.querySelectorAll('.personaje[data-sprite]').forEach(function (el) {
      var hueco = el.querySelector('.cara');
      if (hueco && !hueco.firstChild) hueco.innerHTML = P.svg(el.dataset.sprite);
    });
    document.querySelectorAll('.tool-icon[data-sprite]').forEach(function (el) {
      el.innerHTML = P.svg(el.dataset.sprite);
    });
  }

  // ---- el minijuego ---------------------------------------------------------------------------------------
  var QUIEN_HABLA = {pedido: 'agente', medidas: 'agente', pruebas: 'agente', revision: 'codex', motivo: 'persona',
                     cierre: 'oracle', fin: 'oracle'};
  var NOMBRE = {agente: 'Agente', codex: 'codex', oracle: 'Oracle', persona: 'Vos'};

  function juego() {
    var raiz = document.getElementById('juego');
    if (!raiz || !J) return;
    var e = J.nuevo();
    var situacion = document.getElementById('juego-situacion'), opciones = document.getElementById('juego-opciones');
    var porque = document.getElementById('juego-porque'), registro = document.getElementById('juego-registro');
    var habla = document.getElementById('juego-habla'), nombre = document.getElementById('juego-nombre');
    var pasos = document.querySelectorAll('#juego-pasos li');
    var ORDEN = ['pedido', 'medidas', 'pruebas', 'revision', 'cierre', 'fin'];

    function dibujar(enfocar) {
      var quien = QUIEN_HABLA[e.paso];
      habla.innerHTML = P.svg(quien);
      nombre.textContent = NOMBRE[quien];
      situacion.textContent = J.situacion(e);
      var actual = ORDEN.indexOf(e.paso === 'motivo' ? 'revision' : e.paso);
      pasos.forEach(function (li, i) {
        li.classList.toggle('hecho', i < actual);
        if (i === actual) li.setAttribute('aria-current', 'step'); else li.removeAttribute('aria-current');
      });
      opciones.innerHTML = '';
      J.opciones(e).forEach(function (o) {
        var b = document.createElement('button');
        b.type = 'button';
        b.textContent = o.texto;
        b.dataset.opcion = o.id;
        if (!o.disponible) {
          b.setAttribute('aria-disabled', 'true');
          b.title = o.porque;
        }
        opciones.appendChild(b);
      });
      raiz.dataset.paso = e.paso;
      raiz.dataset.oracle = e.oracle || '';
      registro.hidden = e.paso !== 'fin';
      document.getElementById('juego-otra').hidden = e.paso !== 'fin';
      if (e.paso === 'fin') {
        registro.innerHTML = '';
        e.registro.forEach(function (x) {
          var li = document.createElement('li');
          var b = document.createElement('b');
          b.textContent = x.quien;
          li.appendChild(b);
          li.appendChild(document.createTextNode(' ' + x.que));
          registro.appendChild(li);
        });
      }
      if (enfocar) {
        var primera = opciones.querySelector('button:not([aria-disabled])') || document.getElementById('juego-otra');
        if (primera && !primera.hidden) primera.focus();
      }
    }

    opciones.addEventListener('click', function (ev) {
      var b = ev.target.closest('button');
      if (!b) return;
      var error = J.elegir(e, b.dataset.opcion);
      porque.textContent = error || '';
      if (!error) dibujar(true);
    });
    // Las flechas mueven el foco entre las opciones, también las no disponibles: elegirlas dice por qué.
    opciones.addEventListener('keydown', function (ev) {
      var botones = Array.prototype.slice.call(opciones.querySelectorAll('button'));
      var i = botones.indexOf(document.activeElement);
      if (i < 0) return;
      var paso = {ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1}[ev.key];
      if (!paso) return;
      ev.preventDefault();
      botones[(i + paso + botones.length) % botones.length].focus();
    });
    document.getElementById('juego-otra').addEventListener('click', function () {
      e = J.nuevo();
      porque.textContent = '';
      dibujar(true);
    });
    dibujar(false);
  }

  // ---- easter eggs ----------------------------------------------------------------------------------------
  function globo(ancla, texto) {
    var g = document.getElementById('globo-secreto');
    g.textContent = texto;
    g.hidden = false;
    g.dataset.de = ancla;
    clearTimeout(globo.t);
    globo.t = setTimeout(function () { g.hidden = true; }, 4000);
  }
  function activable(el, f) {
    if (!el) return;
    el.addEventListener('click', f);
    el.addEventListener('keydown', function (ev) {
      if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); f(); }
    });
  }

  function huevos() {
    var escena = document.querySelector('[data-escena="inicio"]');
    var humo = document.getElementById('humo'), bocanadas = 0;
    activable(document.getElementById('chimenea'), function () {
      bocanadas++;
      escena.dataset.humo = bocanadas;
      var g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      g.setAttribute('class', 'bocanada');
      g.innerHTML = r(150 + (bocanadas % 3) * 2, 2, 6, 5, C.l) + r(152, 0, 4, 2, C.w);
      humo.appendChild(g);
      if (!quieto) setTimeout(function () { g.remove(); }, 1800);
      else while (humo.childNodes.length > 3) humo.firstChild.remove();
      globo('chimenea', bocanadas >= 5 ? '¡La fábrica está a pleno! (' + bocanadas + ' bocanadas)' : '¡Puf!');
    });
    var miaus = ['Miau. Yo sólo superviso.', 'Miau. Ninguna decisión pasa sin que la mire.', 'Prrr… Oracle dio verde.'];
    var vez = 0;
    activable(document.getElementById('gato'), function () {
      var gato = document.getElementById('gato');
      gato.classList.remove('salto');
      void gato.getBoundingClientRect();
      gato.classList.add('salto');  // con movimiento reducido no se anima: la escena nunca queda viva
      escena.dataset.gato = ++vez;
      globo('gato', miaus[(vez - 1) % miaus.length]);
    });
    var KONAMI = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
    var avance = 0;
    document.addEventListener('keydown', function (ev) {
      var tecla = ev.key.length === 1 ? ev.key.toLowerCase() : ev.key;
      avance = tecla === KONAMI[avance] ? avance + 1 : (tecla === KONAMI[0] ? 1 : 0);
      if (avance < KONAMI.length) return;
      avance = 0;
      var fiesta = document.body.dataset.fiesta !== 'si';
      document.body.dataset.fiesta = fiesta ? 'si' : 'no';
      var confeti = document.getElementById('confeti'), piezas = '';
      if (fiesta) for (var i = 0; i < 24; i++) {
        piezas += r(8 + (i * 37) % 224, 2 + (i * 13) % 30, 2, 2, [C.y, C.g, C.b, C.v, C.r, C.o][i % 6], ' class="pieza" style="--i:' + i + '"');
      }
      confeti.innerHTML = piezas;
      document.getElementById('anuncio').textContent = fiesta ? 'Modo fiesta en la fábrica.' : 'Se terminó la fiesta.';
      globo('konami', fiesta ? '↑↑↓↓←→←→BA: ¡modo fiesta!' : 'Fin de la fiesta.');
    });
  }

  // ---- escenas que se animan al entrar ---------------------------------------------------------------------
  function observar() {
    var escenas = document.querySelectorAll('.pixel-scene[data-escena]');
    escenas.forEach(pintar);
    if (quieto) return;
    if (!('IntersectionObserver' in window)) {
      escenas.forEach(function (el) { el.dataset.estado = 'viva'; });
      return;
    }
    var io = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (en) {
        if (en.isIntersecting) { en.target.dataset.estado = 'viva'; io.unobserve(en.target); }
      });
    }, {threshold: 0.25});
    escenas.forEach(function (el) { io.observe(el); });
  }

  observar();
  personajes();
  juego();
  huevos();
})();
