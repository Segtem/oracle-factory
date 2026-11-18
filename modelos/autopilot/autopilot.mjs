function word_to_u32(w) {
  let x = 0;
  for (let i = 0; w.$ === "WCon"; i++) {
    x |= Number(w.head) << i;
    w = w.tail;
  }
  return x >>> 0;
}

function u32_to_word(x) {
  let w = {$: "WNil"};
  for (let i = 31; i >= 0; i--) {
    w = {$: "WCon", head: ((x >>> i) & 1) === 1, tail: w};
  }
  return w;
}

function cmp_new(a, b) {
  return {$: a < b ? "LT" : a === b ? "EQ" : "GT"};
}

function tup_new(a, b) {
  return {$: "Tuple", fst: a, snd: b};
}

function nat_divmod(a, b) {
  return tup_new(b && Math.trunc(a / b), b ? a % b : a);
}

function nat_chk(n) {
  if (n > 281474976710655) {
    throw "bend: a Nat past the largest immediate 2^48-1";
  }
  return n;
}

function nat_in(n) {
  if (!Number.isInteger(n) || n < 0 || n > 2 ** 53) {
    throw "bend: expected a Nat host number: an integer from 0 to 2^53";
  }
  return n;
}

function f32_show(x) {
  let s = "nan";
  for (let p = 1; x === x && p <= 9 && f32_round(s) !== x; p += 1) {
    s = String(Number(x.toExponential(p - 1)));
  }
  return (Object.is(x, -0) ? "-0" : s).replace("Infinity", "inf");
}

function f32_bits(x) {
  return new Uint32Array(new Float32Array([x]).buffer)[0];
}

function f32_from_bits(u) {
  return new Float32Array(new Uint32Array([u]).buffer)[0];
}

function f32_read(s) {
  const re = /^[\t\n\v\f\r ]*[+-]?((\d+(?:\.\d*)?|\.\d+)(e[+-]?\d+)?|inf(inity)?|nan)$/i;
  return re.test(s) ? {$: "Some", value: f32_round(
    s.replace(/inf\w*/i, "Infinity"))} : {$: "None"};
}

const f32_round = function f32_round(s) {
  const d = Number(s);
  const a = Math.abs(d);
  const f = Math.fround(a);
  const g = 2 * a - Math.min(f, 2 ** 128);
  if (g === f || Math.fround(g) !== g || g === Infinity) {
    return Math.sign(d) * f;
  }
  let k = 0;
  while (a * 2 ** k % 1 !== 0) {
    k += 1;
  }
  const [, i, r, e] = /(\d*)\.?(\d*)(?:e([+-]?\d+))?$/i.exec(s);
  const n = Number(e ?? 0) - r.length;
  const x = BigInt(i + r) * 2n ** BigInt(k) * 10n ** BigInt(Math.max(n, 0));
  const y = BigInt(a * 2 ** k) * 10n ** BigInt(Math.max(-n, 0));
  return Math.sign(d) * (x === y || x > y !== g > f ? f : g);
};

const char_new = function char_new(c) {
  return c < 55296 || c >= 57344 && c <= 1114111 ? String.fromCodePoint(c) : String.fromCharCode(56320, c >>> 22, c >>> 11 & 2047, c & 2047);
};

function char_len(s, at = 0) {
  return s[at] === "\uDC00" ? 4 : s.codePointAt(at) > 0xFFFF ? 2 : 1;
}

function char_code(s) {
  return s.length < 4 ? s.codePointAt(0)
    : (s.charCodeAt(1) << 22 | s.charCodeAt(2) << 11 | s.charCodeAt(3)) >>> 0;
}

function string_contains(s, p) {
  // A match starts at a Char, not inside a packed U32 code.
  for (let at = 0; at <= s.length; at += char_len(s, at)) {
    if (s.startsWith(p, at)) {
      return true;
    }
  }
  return false;
}

function str_out(s) {
  return s.replace(/\uDC00[^]{3}/gu, "\uFFFD");
}

function str_in(s) {
  return s.replace(/\p{Cs}/gu, "\uFFFD");
}

// Array
// =====

function array_new(d, v, lgs) {
  if (d > 31 - lgs) {
    throw "bend: an array past the deepest block class 31 (depth + log2 words per cell)";
  }
  return Array(2 ** d).fill(v);
}

function array_node(a, b) {
  if (a.length !== b.length) {
    throw "bend: runtime fail-stop";
  }
  return a.concat(b);
}

function array_rmw(a, i, f) {
  const old = a[i %= a.length];
  a[i] = f(old);
  return tup_new(a, old);
}

// Run
// ===

function run_tail(f, x) {
  return {$: "$JMP", f: f.j?.f === f ? f.j : f, x};
}

function run_clo(j) {
  const f = (x) => run_loop(j(x));
  f.j = j;
  j.f = f;
  return f;
}

function run_loop(r) {
  while (r !== null && typeof r === "object" && r.$ === "$JMP") {
    r = r.f(r.x);
  }
  return r;
}

function run_lib(f, n) {
  return (...a) => a.length < n ? run_lib((...b) => f(...a, ...b), n - a.length)
    : run_loop(f(...a));
}

// Effect
// ======

const $0eff = Object.create(null);
const io_file_append = new Set();

function io_eff(k, run) {
  if (arguments.length > 2) {
    throw new Error("bend: " + k + " takes no need: an effect that waits parks itself");
  }
  if (k in $0eff) {
    throw new Error("bend: two effects register " + k);
  }
  $0eff[k] = run;
}
// Program
// =======

function $frena() {
  return {$: "Salida", "accion": {$: "Frenar"}, "sub": {$: "SinPaso"}};
}

function $delega() {
  return {$: "Salida", "accion": {$: "DelegarAlAgente"}, "sub": {$: "SinPaso"}};
}

function $con_revisar(_segundo_0, _candidato_0, _propuesta_0) {
  if (_segundo_0) {
    return {$: "Salida", "accion": {$: "Actuar"}, "sub": {$: "PedirRevision"}};
  } else {
    if (_candidato_0) {
      if (_propuesta_0) {
        return {$: "Salida", "accion": {$: "PedirAPersona"}, "sub": {$: "Revisar"}};
      } else {
        return $delega();
      }
    } else {
      return {$: "Salida", "accion": {$: "PedirAPersona"}, "sub": {$: "Revisar"}};
    }
  }
}

function $sin_candidato_construye(_candidato_0, _s_0) {
  if (_candidato_0) {
    return {$: "Salida", "accion": {$: "Actuar"}, "sub": _s_0};
  } else {
    return $delega();
  }
}

function $sin_frenos(_s_0, _terminada_0, _segundo_0, _candidato_0, _propuesta_0) {
  if (_s_0.$ === "SinPaso") {
    if (_terminada_0) {
      return {$: "Salida", "accion": {$: "Terminado"}, "sub": {$: "SinPaso"}};
    } else {
      return $frena();
    }
  } else if (_s_0.$ === "Prosa") {
    return $delega();
  } else if (_s_0.$ === "Ilegible") {
    return $frena();
  } else if (_s_0.$ === "AprobarSpec") {
    return {$: "Salida", "accion": {$: "PedirAPersona"}, "sub": {$: "AprobarSpec"}};
  } else if (_s_0.$ === "Revisar") {
    return $con_revisar(_segundo_0, _candidato_0, _propuesta_0);
  } else if (_s_0.$ === "Cerrar") {
    return {$: "Salida", "accion": {$: "PedirAPersona"}, "sub": {$: "Cerrar"}};
  } else if (_s_0.$ === "Abandonar") {
    return {$: "Salida", "accion": {$: "PedirAPersona"}, "sub": {$: "Abandonar"}};
  } else if (_s_0.$ === "Modo") {
    return {$: "Salida", "accion": {$: "PedirAPersona"}, "sub": {$: "Modo"}};
  } else if (_s_0.$ === "Autonomia") {
    return {$: "Salida", "accion": {$: "PedirAPersona"}, "sub": {$: "Autonomia"}};
  } else if (_s_0.$ === "Soltar") {
    return {$: "Salida", "accion": {$: "PedirAPersona"}, "sub": {$: "Soltar"}};
  } else if (_s_0.$ === "DecidirUnion") {
    return {$: "Salida", "accion": {$: "PedirAPersona"}, "sub": {$: "DecidirUnion"}};
  } else if (_s_0.$ === "Conectar") {
    return {$: "Salida", "accion": {$: "PedirAPersona"}, "sub": {$: "Conectar"}};
  } else if (_s_0.$ === "Desconectar") {
    return {$: "Salida", "accion": {$: "PedirAPersona"}, "sub": {$: "Desconectar"}};
  } else if (_s_0.$ === "Importar") {
    return {$: "Salida", "accion": {$: "Actuar"}, "sub": {$: "Importar"}};
  } else if (_s_0.$ === "Juzgar") {
    return {$: "Salida", "accion": {$: "Actuar"}, "sub": {$: "Juzgar"}};
  } else if (_s_0.$ === "PedirRevision") {
    return $sin_candidato_construye(_candidato_0, {$: "PedirRevision"});
  } else if (_s_0.$ === "RevisionPreparar") {
    return $sin_candidato_construye(_candidato_0, {$: "RevisionPreparar"});
  } else if (_s_0.$ === "Tomar") {
    return {$: "Salida", "accion": {$: "Actuar"}, "sub": {$: "Tomar"}};
  } else if (_s_0.$ === "Mensaje") {
    return {$: "Salida", "accion": {$: "Actuar"}, "sub": {$: "Mensaje"}};
  } else if (_s_0.$ === "Sincronizar") {
    return {$: "Salida", "accion": {$: "Actuar"}, "sub": {$: "Sincronizar"}};
  } else if (_s_0.$ === "MedirConfirmar") {
    return {$: "Salida", "accion": {$: "PedirAPersona"}, "sub": {$: "MedirConfirmar"}};
  } else if (_s_0.$ === "MedirListar") {
    return $delega();
  } else if (_s_0.$ === "MedirOtro") {
    return $frena();
  } else if (_s_0.$ === "AprobarSensor") {
    return $frena();
  } else if (_s_0.$ === "Evidencia") {
    return $frena();
  } else {
    return $frena();
  }
}

function $decidir(_frenos_0, _terminada_0, _s_0, _segundo_0, _candidato_0, _propuesta_0) {
  if (_frenos_0) {
    return $frena();
  } else {
    return $sin_frenos(_s_0, _terminada_0, _segundo_0, _candidato_0, _propuesta_0);
  }
}

function $es_mecanico(_s_0) {
  if (_s_0.$ === "Importar") {
    return true;
  } else if (_s_0.$ === "Juzgar") {
    return true;
  } else if (_s_0.$ === "PedirRevision") {
    return true;
  } else if (_s_0.$ === "RevisionPreparar") {
    return true;
  } else if (_s_0.$ === "Tomar") {
    return true;
  } else if (_s_0.$ === "Mensaje") {
    return true;
  } else if (_s_0.$ === "Sincronizar") {
    return true;
  } else {
    return false;
  }
}

function $sin_comando(_s_0) {
  if (_s_0.$ === "SinPaso") {
    return true;
  } else {
    return false;
  }
}

function $permitida(_x_0) {
  const _t_0 = _x_0["accion"];
  if (_t_0.$ === "Actuar") {
    const _s_0 = _x_0["sub"];
    return $es_mecanico(_s_0);
  } else if (_t_0.$ === "PedirAPersona") {
    return true;
  } else if (_t_0.$ === "Frenar") {
    const _s_2 = _x_0["sub"];
    return $sin_comando(_s_2);
  } else if (_t_0.$ === "DelegarAlAgente") {
    const _s_3 = _x_0["sub"];
    return $sin_comando(_s_3);
  } else {
    const _s_4 = _x_0["sub"];
    return $sin_comando(_s_4);
  }
}

function $accion_de(_x_0) {
  const _a_0 = _x_0["accion"];
  return _a_0;
}
export default {
  "frena": run_lib(() => run_loop($frena()), 0),
  "delega": run_lib(() => run_loop($delega()), 0),
  "con_revisar": run_lib((a0,a1,a2) => run_loop($con_revisar(a0,a1,a2)), 3),
  "sin_candidato_construye": run_lib((a0,a1) => run_loop($sin_candidato_construye(a0,a1)), 2),
  "sin_frenos": run_lib((a0,a1,a2,a3,a4) => run_loop($sin_frenos(a0,a1,a2,a3,a4)), 5),
  "decidir": run_lib((a0,a1,a2,a3,a4,a5) => run_loop($decidir(a0,a1,a2,a3,a4,a5)), 6),
  "es_mecanico": run_lib((a0) => run_loop($es_mecanico(a0)), 1),
  "sin_comando": run_lib((a0) => run_loop($sin_comando(a0)), 1),
  "permitida": run_lib((a0) => run_loop($permitida(a0)), 1),
  "accion_de": run_lib((a0) => run_loop($accion_de(a0)), 1),
};
