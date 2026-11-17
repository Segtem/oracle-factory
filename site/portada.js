/* La portada interactiva: copiar comandos, el recorrido de un cambio y los tres ejemplos. Sin este script todo se lee igual:
   el HTML trae los nueve pasos en una lista y los dos estados de cada ejemplo; acá sólo se muestra uno por vez. */
(function () {
  'use strict';
  var P = window.Pixel;
  var $ = function (id) { return document.getElementById(id); };
  document.querySelectorAll('[data-solo-js]').forEach(function (e) { e.hidden = false; });

  // ---- copiar cada comando --------------------------------------------------------------------------------------
  var anuncio = $('copiado-anuncio');
  document.querySelectorAll('#empezar .comando, #camino .comando, #ejemplos .comando').forEach(function (bloque) {
    var code = bloque.querySelector('code');
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'copiar';
    b.textContent = 'Copiar';
    b.setAttribute('aria-label', 'Copiar el comando: ' + code.textContent);
    b.addEventListener('click', function () {
      var listo = function (texto) {
        b.textContent = texto;
        anuncio.textContent = texto === 'Copiado' ? 'Copiado: ' + code.textContent : 'El comando quedó seleccionado: copialo con Ctrl+C.';
        clearTimeout(b.t);
        b.t = setTimeout(function () { b.textContent = 'Copiar'; }, 1800);
      };
      var elegir = function () {
        var rango = document.createRange();
        rango.selectNodeContents(code);
        getSelection().removeAllRanges();
        getSelection().addRange(rango);
        listo('Seleccionado');
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(code.textContent).then(function () { listo('Copiado'); }, elegir);
      } else elegir();
    });
    bloque.appendChild(b);
  });

  // ---- el recorrido ---------------------------------------------------------------------------------------------
  var visor = $('camino-visor');
  if (visor && P) {
    var pasos = Array.prototype.slice.call(document.querySelectorAll('#camino-pasos > li'));
    var escena = visor.querySelector('[data-escena="camino"]');
    var anterior = $('camino-anterior'), siguiente = $('camino-siguiente'), mapa = $('camino-mapa');
    var actual = -1;
    var INICIO = ['persona', 'agente', 'fabrica', 'codex', 'oracle'];
    visor.tabIndex = 0;
    visor.setAttribute('role', 'group');
    visor.setAttribute('aria-roledescription', 'recorrido');
    visor.setAttribute('aria-label', 'Recorrido de un cambio en nueve pasos: usá las flechas para avanzar y retroceder');
    pasos.forEach(function (li, i) {
      var b = document.createElement('button');
      b.type = 'button';
      b.textContent = String(i + 1);
      b.setAttribute('aria-label', 'Paso ' + (i + 1) + ': ' + li.querySelector('h3').textContent +
        (li.classList.contains('decision-persona') ? ', decisión de una persona' : ''));
      if (li.classList.contains('decision-persona')) b.className = 'de-persona';
      b.addEventListener('click', function () { ir(i); });
      mapa.appendChild(b);
    });
    var botonesMapa = mapa.querySelectorAll('button');

    function actores(nombres, x) {
      return nombres.map(function (n, k) {
        return '<g class="trabaja" transform="translate(' + (x + k * 18) + ' 13)">' + P.rects(P.SPRITES[n], 0, 0) + '</g>';
      }).join('');
    }
    function ir(i) {
      actual = Math.max(-1, Math.min(pasos.length - 1, i));
      var li = pasos[actual];
      pasos.forEach(function (p, k) { p.hidden = k !== actual; });
      $('camino-intro').hidden = actual !== -1;
      anterior.setAttribute('aria-disabled', String(actual <= -1));
      siguiente.setAttribute('aria-disabled', String(actual >= pasos.length - 1));
      botonesMapa.forEach(function (b, k) { if (k === actual) b.setAttribute('aria-current', 'step'); else b.removeAttribute('aria-current'); });
      var persona = li && li.classList.contains('decision-persona');
      visor.dataset.persona = persona ? 'si' : 'no';
      escena.querySelectorAll('.luz-estacion').forEach(function (luz, k) {
        luz.setAttribute('fill', k < actual ? P.PALETA.g : k === actual ? P.PALETA.y : P.PALETA.d);
      });
      var x = actual < 0 ? -18 : 14 + actual * 26;
      $('camino-caja').style.transform = 'translate(' + x + 'px, 35px)';
      var quienes = li ? li.dataset.actor.split(' ') : INICIO;
      var izquierda = li ? Math.min(Math.max(x - (quienes.length - 1) * 9, 0), 240 - quienes.length * 18) : 30;
      $('camino-actores').innerHTML = li ? actores(quienes, izquierda) : INICIO.map(function (n, k) {
        return '<g class="trabaja" transform="translate(' + (30 + k * 40) + ' 13)">' + P.rects(P.SPRITES[n], 0, 0) + '</g>';
      }).join('');
      escena.dataset.paso = li ? li.dataset.paso : 'inicio';
      if (li) {
        var titulo = li.querySelector('h3').textContent, actor = li.querySelector('.actor').textContent.replace(/^Quién:\s*/, '');
        $('camino-contador').textContent = 'Paso ' + (actual + 1) + ' de ' + pasos.length;
        escena.setAttribute('aria-label', 'Paso ' + (actual + 1) + ', ' + titulo + ': en la pasarela, ' + actor +
          ' La caja del cambio está en la estación ' + (actual + 1) + ' de la cinta.' + (persona ? ' Es una decisión de una persona.' : ''));
        $('camino-anuncio').textContent = 'Paso ' + (actual + 1) + ' de ' + pasos.length + ': ' + titulo + (persona ? ', decisión de una persona' : '');
      } else {
        $('camino-contador').textContent = 'Antes de empezar';
      }
    }
    anterior.addEventListener('click', function () { if (actual > -1) ir(actual - 1); });
    siguiente.addEventListener('click', function () { if (actual < pasos.length - 1) ir(actual + 1); });
    visor.addEventListener('keydown', function (ev) {
      if (ev.target.closest('a, input')) return;
      var destino = {ArrowRight: actual + 1, ArrowDown: actual + 1, ArrowLeft: actual - 1, ArrowUp: actual - 1, Home: 0,
                     End: pasos.length - 1}[ev.key];
      if (destino === undefined) return;
      ev.preventDefault();
      ir(destino);
    });
    ir(-1);
  }

  // ---- ejemplo 1: rompé el código -------------------------------------------------------------------------------
  function mostrar(ejemplo, estado) {
    ejemplo.querySelectorAll('.estado').forEach(function (e) { e.hidden = e.dataset.caso !== estado; });
  }
  var romper = $('romper');
  if (romper) {
    var ejRomper = $('ej-romper'), escenaRomper = ejRomper.querySelector('[data-escena="romper"]');
    var poner = function (roto) {
      romper.setAttribute('aria-checked', String(roto));
      ejRomper.dataset.roto = escenaRomper.dataset.roto = roto ? 'si' : 'no';
      mostrar(ejRomper, roto ? 'roto' : 'sano');
    };
    romper.addEventListener('click', function () { poner(romper.getAttribute('aria-checked') !== 'true'); });
    poner(false);
  }

  // ---- ejemplo 2: cambiá el sensor ------------------------------------------------------------------------------
  var campo = $('sensor-comando');
  if (campo) {
    var ejSensor = $('ej-sensor'), escenaSensor = ejSensor.querySelector('[data-escena="sensor"]');
    var ORIGINAL = campo.value, aprobados = [ORIGINAL], recien = null;
    var json = function (comando) {
      return JSON.stringify({comando: comando.trim().split(/\s+/), tope_minutos: 5, hechos: 'exigir'}, null, 2);
    };
    var pintarSensor = function () {
      var valor = campo.value.trim().replace(/\s+/g, ' ');
      var estado = !valor ? 'cambiado' : recien === valor ? 'reaprobado' : aprobados.indexOf(valor) >= 0 ? 'aprobado' : 'cambiado';
      if (estado !== 'reaprobado') recien = null;
      ejSensor.dataset.sensor = escenaSensor.dataset.sensor = estado;
      mostrar(ejSensor, estado);
      ejSensor.querySelectorAll('[data-caso="cambiado"] .sensor-json, [data-caso="aprobado"] .sensor-json').forEach(function (pre) {
        pre.textContent = json(valor || ' ');
      });
      $('sensor-aprobar').disabled = !valor;
    };
    campo.addEventListener('input', pintarSensor);
    $('sensor-sugerencia').addEventListener('click', function () { campo.value = ORIGINAL + ' --solo-rapidas'; pintarSensor(); });
    $('sensor-volver').addEventListener('click', function () { campo.value = ORIGINAL; pintarSensor(); });
    $('sensor-aprobar').addEventListener('click', function () {
      var valor = campo.value.trim().replace(/\s+/g, ' '), ultimo = aprobados[aprobados.length - 1];
      ejSensor.querySelector('.sensor-aprobacion').textContent =
        'Sensor declarado en .factory/config.json (el que correría oracle-factory evidencia):\n' + json(valor) +
        '\nÚltimo sensor aprobado (Ana Gómez, 2026-11-17T13:02:11.482913+00:00):\n' + json(ultimo) +
        '\n\nAprobar este sensor para producir los hechos\n' +
        '  1) Aprobar el sensor — oracle-factory evidencia correrá ese comando sobre cada candidato, y sus hechos contarán como producidos por Factory\n' +
        '  2) Cancelar — no registra nada\nElegí 1-2: 1\nSensor aprobado por Ana Gómez. Quedó en .factory/sensor-aprobado.json.';
      aprobados.push(valor);
      recien = valor;
      pintarSensor();
      ejSensor.querySelector('[data-caso="reaprobado"] h4').focus();
    });
    ejSensor.querySelector('[data-caso="reaprobado"] h4').tabIndex = -1;
    pintarSensor();
  }

  // ---- ejemplo 3: la mutación -----------------------------------------------------------------------------------
  var ejMut = $('ej-mutacion');
  if (ejMut) {
    var PRUEBAS = {vacio: 'self.assertFalse(puede_guardar(""))', una_letra: 'self.assertTrue(puede_guardar("a"))',
                   con_texto: 'self.assertTrue(puede_guardar("Mi nota"))', justo_80: 'self.assertTrue(puede_guardar("x" * 80))',
                   largo_81: 'self.assertFalse(puede_guardar("x" * 81))'};
    var filas = ejMut.querySelectorAll('#mutacion-tabla tbody tr');
    var escenaMut = ejMut.querySelector('[data-escena="mutacion"]');
    var total = ejMut.querySelectorAll('#mutacion-tabla thead [data-mutante]').length;
    var juicio = ejMut.querySelector('.juicio-mutacion'), juicioRojo = juicio.textContent;
    var pintarMut = function () {
      var puestas = {}, muertos = {}, modulo = 'import unittest\nfrom notas import puede_guardar\n\n\nclass Notas(unittest.TestCase):\n';
      ejMut.querySelectorAll('.pruebas input').forEach(function (c) { puestas[c.value] = c.checked; });
      filas.forEach(function (tr) {
        var puesta = puestas[tr.dataset.prueba];
        tr.classList.toggle('fuera', !puesta);
        if (puesta) {
          tr.dataset.mata.split(' ').forEach(function (m) { muertos[m] = true; });
          modulo += '    def test_' + tr.dataset.prueba + '(self):\n        ' + PRUEBAS[tr.dataset.prueba] + '\n\n';
        }
      });
      if (modulo.slice(-2) !== '\n\n') modulo += '    pass\n';
      var n = Object.keys(muertos).length, pct = Math.floor(n * 100 / total), cumple = pct >= 80;
      $('mutacion-porcentaje').textContent = pct + '%';
      $('mutacion-cuenta').textContent = n + ' de ' + total + ' mutantes muertos';
      var medida = $('mutacion-medida');
      medida.dataset.cumple = cumple ? 'si' : 'no';
      medida.dataset.veredicto = cumple ? 'verde' : 'rojo';
      medida.innerHTML = cumple ? '<b>La medida se cumple:</b> pide 80% o más.' : '<b>La medida no se cumple:</b> pide 80% o más, y mueren ' + pct + '%.';
      ejMut.querySelector('.hechos-mutacion').textContent = '"notas_mutacion": [\n  {"generados": ' + total + ', "muertos": ' + n +
        ', "porcentaje": ' + pct + ', "tope_alcanzado": 0}\n]';
      juicio.textContent = cumple ? juicioRojo.split('\n').slice(0, 2).join('\n') : juicioRojo;
      juicio.classList.toggle('error', !cumple);
      ejMut.querySelector('.modulo-pruebas').textContent = modulo.replace(/\n+$/, '\n');
      escenaMut.querySelectorAll('.mutante').forEach(function (g) { g.classList.toggle('muerto', !!muertos[g.dataset.mutante]); });
      var barra = $('mutacion-barra');
      if (barra) {
        barra.setAttribute('width', String(Math.round(202 * pct / 100)));
        barra.setAttribute('fill', cumple ? P.PALETA.G : P.PALETA.r);
      }
      escenaMut.setAttribute('aria-label', 'Cinco mutantes, uno por cada falla posible en la línea del cambio: ' + n +
        ' tachados porque alguna prueba los detecta. La barra marca ' + pct + '% contra la marca del 80%.');
    };
    ejMut.querySelectorAll('.pruebas input').forEach(function (c) { c.addEventListener('change', pintarMut); });
    pintarMut();
  }
})();
