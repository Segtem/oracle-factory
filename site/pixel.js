/* Sprites de pixel art como texto: un carácter por píxel, con la paleta de la web. Se dibujan como SVG en línea. */
(function (raiz) {
  'use strict';

  var PALETA = {
    k: '#182a25', d: '#132421', g: '#c0ec96', G: '#5f8f4e', h: '#3d6b45', m: '#acddc5', y: '#ebc36f', Y: '#c99a3e',
    p: '#f6f5ec', l: '#d8ddd0', s: '#f1c8a4', S: '#cf9874', b: '#7fb2e5', B: '#3f6f9e', v: '#b79be6', V: '#7356a8',
    r: '#e0705f', R: '#a8473b', o: '#e8994d', O: '#b8692a', n: '#a07850', N: '#6e5034', w: '#ffffff', c: '#5a5f63'
  };

  var SPRITES = {
    persona: [
      '................',
      '......yyyy......',
      '.....yyyyyy.....',
      '....yyyyyyyy....',
      '....kkkkkkkk....',
      '.....ssssss.....',
      '.....skssks.....',
      '.....ssssss.....',
      '......sSSs......',
      '....GGGGGGGG....',
      '...GGGGGGGGGpp..',
      '...sGGGGGGGGpp..',
      '...sGGGGGGGGpp..',
      '....GGGGGGGG....',
      '.....kk..kk.....',
      '.....kk..kk.....'],
    agente: [
      '.......kk.......',
      '.......gg.......',
      '....kkkkkkkk....',
      '...kmmmmmmmmk...',
      '...kmkgmmkgmk...',
      '...kmkgmmkgmk...',
      '...kmmmmmmmmk...',
      '...kmmkkkkmmk...',
      '....kkkkkkkk....',
      '.....kmmmmk.....',
      '...kkmmggmmkk...',
      '..kmkmmggmmkmk..',
      '..kmkmmmmmmkmk..',
      '....kmmmmmmk....',
      '....kkk..kkk....',
      '....kkk..kkk....'],
    codex: [
      '.......kk.......',
      '.......bb.......',
      '....kkkkkkkk....',
      '...kbbbbbbbbk...',
      '...kkkkbbkkkk...',
      '...kkwkkkkwkk...',
      '...kbbbbbbbbk...',
      '...kbbkkkkbbk...',
      '....kkkkkkkk....',
      '.....kbbbbk.....',
      '...kkbbBBbbkk...',
      '..kbkbbBBbbkbk..',
      '..kbkbbbbbbkbk..',
      '....kbbbbbbk....',
      '....kkk..kkk....',
      '....kkk..kkk....'],
    agy: [
      '.......vv.......',
      '......vwwv......',
      '....kkkvvkkk....',
      '...kvvvvvvvvk...',
      '...kvkwvvkwvk...',
      '...kvkwvvkwvk...',
      '...kvvvvvvvvk...',
      '...kvvkkkkvvk...',
      '....kkkkkkkk....',
      '.....kvvvvk.....',
      '...kkvvVVvvkk...',
      '..kvkvVwwVvkvk..',
      '..kvkvvVVvvkvk..',
      '....kvvvvvvk....',
      '....kkk..kkk....',
      '....kkk..kkk....'],
    oracle: [
      '.......kk.......',
      '......kggk......',
      '.....kgGGgk.....',
      '....kgGwwGgk....',
      '...kgGwkkwGgk...',
      '..kgGwkggkwGgk..',
      '..kgGwkggkwGgk..',
      '...kgGwkkwGgk...',
      '....kgGwwGgk....',
      '.....kgGGgk.....',
      '......kggk......',
      '.......kk.......',
      '......kkkk......',
      '.....kcccck.....',
      '....kcccccck....',
      '....kkkkkkkk....'],
    clue: [
      '................',
      '.....kkkkk......',
      '....kmmmmmk.....',
      '...kmwmmmmmk....',
      '...kmwmmmmmk....',
      '...kmmmmmmmk....',
      '...kmmmmmmmk....',
      '...kmmmmmmmk....',
      '....kmmmmmk.....',
      '.....kkkkkYk....',
      '..........YYk...',
      '...........YYk..',
      '............YYk.',
      '.............Yk.',
      '..............k.',
      '................'],
    openspec: [
      '................',
      '..kkkkkkkkkkk...',
      '.kyykppppppyyk..',
      '.kYykppppppyYk..',
      '..kkpkkkkkkpk...',
      '...kpppppppk....',
      '...kpkkkkkpk....',
      '...kpppppppk....',
      '...kpkkkkppk....',
      '...kpppppppk....',
      '...kpkkkkkpk....',
      '...kpppppppk....',
      '..kkkkkkkkkkk...',
      '.kyykppppppyyk..',
      '.kYykkkkkkkyYk..',
      '..kkk.....kkk...'],
    task: [
      '.....kkkkkk.....',
      '..kkkkYYYYkkkk..',
      '..knnkkkkkknnk..',
      '..knppppppppnk..',
      '..knpGkpppppnk..',
      '..knpkGpkkkpnk..',
      '..knppppppppnk..',
      '..knpGkpppppnk..',
      '..knpkGpkkkpnk..',
      '..knppppppppnk..',
      '..knpkkpppppnk..',
      '..knpkkpkkkpnk..',
      '..knppppppppnk..',
      '..knnnnnnnnnnk..',
      '..kkkkkkkkkkkk..',
      '................'],
    gato: [
      '................',
      '..k.....k.......',
      '..kk...kk.......',
      '..kokkkok.......',
      '..koooook.......',
      '..kowoowk.......',
      '..koookok.......',
      '..koooook...kk..',
      '...kooook...kok.',
      '...kooooook..ok.',
      '..koooooooook.k.',
      '..kooooooooook..',
      '..kooooooooook..',
      '..kooookkooook..',
      '..kook..kook....',
      '..kkk....kkk....'],
    caja: [
      '................',
      '................',
      '................',
      '..kkkkkkkkkkkk..',
      '..knnnnYYnnnnk..',
      '..knnnnYYnnnnk..',
      '..kNNNNYYNNNNk..',
      '..knnnnYYnnnnk..',
      '..knnnnYYnnnnk..',
      '..knnnnnnnnnnk..',
      '..knnnnnnnnnnk..',
      '..knnnnnnnnnnk..',
      '..knnnnnnnnnnk..',
      '..kkkkkkkkkkkk..',
      '................',
      '................'],
    pantalla: [
      '................',
      '.kkkkkkkkkkkkkk.',
      '.kddddddddddddk.',
      '.kdgddddddddddk.',
      '.kddgdddddddddk.',
      '.kdgdgggddddddk.',
      '.kddddddddddddk.',
      '.kdgggggddddddk.',
      '.kddddddddddddk.',
      '.kkkkkkkkkkkkkk.',
      '......kccck.....',
      '.....kcccccck...',
      '....kkkkkkkkk...',
      '................',
      '................',
      '................'],
    bandera: [
      '................',
      '...kkkkkkk......',
      '...kyyyyyyk.....',
      '...kyyyyyyyk....',
      '...kyyyyyyk.....',
      '...kkkkkkk......',
      '...k............',
      '...k............',
      '...k............',
      '...k............',
      '...k............',
      '...k............',
      '..kkk...........',
      '.kGGGk..........',
      '................',
      '................']
  };

  // Una fila de píxeles iguales es un solo rectángulo: menos nodos, el mismo dibujo.
  function rects(filas, dx, dy) {
    var partes = [];
    filas.forEach(function (fila, y) {
      var x = 0;
      while (x < fila.length) {
        var c = fila[x], fin = x;
        while (fin < fila.length && fila[fin] === c) fin++;
        if (PALETA[c]) partes.push('<rect x="' + (x + dx) + '" y="' + (y + dy) + '" width="' + (fin - x) + '" height="1" fill="' + PALETA[c] + '"/>');
        x = fin;
      }
    });
    return partes.join('');
  }

  // El SVG de un sprite; `clase` va al <svg> para animarlo con CSS.
  function svg(nombre, clase) {
    var filas = SPRITES[nombre];
    return '<svg class="px ' + (clase || '') + '" viewBox="0 0 ' + filas[0].length + ' ' + filas.length + '" shape-rendering="crispEdges" aria-hidden="true" focusable="false">'
      + rects(filas, 0, 0) + '</svg>';
  }

  // Un sprite dentro de un SVG mayor, en (x, y), envuelto en un <g> con clase.
  function g(nombre, x, y, clase, extra) {
    return '<g class="' + (clase || '') + '" transform="translate(' + x + ' ' + y + ')"' + (extra || '') + '>'
      + rects(SPRITES[nombre], 0, 0) + '</g>';
  }

  var api = {PALETA: PALETA, SPRITES: SPRITES, svg: svg, g: g, rects: rects};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else raiz.Pixel = api;
})(this);
