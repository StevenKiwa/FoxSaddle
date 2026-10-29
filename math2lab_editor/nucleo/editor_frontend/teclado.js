const TECLAS_BARRA = [
  ["a⁄b", "\\frac{#?}{#?}", "Fracción"],
  ["xⁿ", "^{#?}", "Potencia"],
  ["√", "\\sqrt{#?}", "Raíz cuadrada"],
  ["sen", "\\sin\\left(#?\\right)", "Seno"],
  ["cos", "\\cos\\left(#?\\right)", "Coseno"],
  ["tan", "\\tan\\left(#?\\right)", "Tangente"],
  ["ln", "\\ln\\left(#?\\right)", "Logaritmo natural"],
  ["eˣ", "\\exponentialE^{#?}", "e elevado a ..."],
  ["|x|", "\\left|#?\\right|", "Valor absoluto"],
  ["π", "\\pi", "Pi"],
  ["( )", "\\left(#?\\right)", "Paréntesis"],
  ["+", "+", "Suma"],
  ["−", "-", "Resta"],
  ["*", "\\cdot ", "Multiplicación"],
];
const NUMEROS = "1234567890";
const FILA_Q = "qwertyuiop";
const FILA_A = "asdfghjkl";
const FILA_Z = "zxcvbnm";
const INSIGNIA_ALTO = 56;

function crearTeclado({ mf, contenedor, estaListo, marcar, aplicar, altura }) {
  let P = null;
  try { P = window.parent.document.body ? window.parent.document : null; } catch (e) {}
  const doc = P || document;
  const principal = () => P.querySelector('[data-testid="stMain"]') || P.querySelector("section.main");
  let teclado = null, estilo = null, visible = false, tocandoHasta = 0, espera = null, repeticion = null;
  let intervaloLateral = null, baseInferior = 0;

  const sinTecladoNativo = () => {
    try { mf.setAttribute("inputmode", "none"); } catch (e) {}
    try { mf.shadowRoot.querySelectorAll("textarea, [contenteditable]").forEach((el) => el.setAttribute("inputmode", "none")); } catch (e) {}
  };
  const ejecutar = (accion) => { if (estaListo()) { accion(); mf.focus(); marcar(); } };
  const detenerRepeticion = () => { clearTimeout(espera); clearInterval(repeticion); espera = repeticion = null; };
  const insertar = (latex) => () => mf.insert(latex);
  const comando = (nombre) => () => mf.executeCommand(nombre);
  const frenar = (e) => e.preventDefault();

  function crearTecla(texto, accion, { clase = "", ayuda = "", repetir = false } = {}) {
    const b = doc.createElement("button");
    b.type = "button";
    b.className = ("m2l-k " + clase).trim();
    b.textContent = texto;
    if (ayuda) { b.title = ayuda; b.setAttribute("aria-label", ayuda); }
    b.addEventListener("pointerdown", (e) => {
      frenar(e);
      tocandoHasta = Date.now() + 500;
      ejecutar(accion);
      if (repetir) {
        detenerRepeticion();
        espera = setTimeout(() => { repeticion = setInterval(() => ejecutar(accion), 70); }, 380);
      }
    });
    ["pointerup", "pointerleave", "pointercancel"].forEach((ev) => b.addEventListener(ev, detenerRepeticion));
    b.addEventListener("mousedown", frenar);
    b.addEventListener("touchstart", frenar, { passive: false });
    b.addEventListener("contextmenu", frenar);
    return b;
  }

  const letras = (cadena) => [...cadena].map((c) => crearTecla(c, insertar(c)));

  function crearAplicar() {
    const boton = crearTecla("Aplicar ✓", () => {}, { clase: "m2l-ancha m2l-ap", ayuda: "Aplicar la fórmula" });
    boton.addEventListener("pointerdown", () => {
      if (!estaListo()) return;
      aplicar();
      ocultar();
      mf.blur();
    });
    return boton;
  }

  function montar() {
    if (P) ["m2l-teclado", "m2l-teclado-css"].forEach((id) => { const previo = P.getElementById(id); if (previo) previo.remove(); });
    estilo = doc.createElement("style");
    estilo.id = "m2l-teclado-css";
    estilo.textContent = CSS_TECLADO;
    (P ? P.head : document.head).appendChild(estilo);

    teclado = doc.createElement("div");
    teclado.id = "m2l-teclado";
    teclado.className = P ? "m2l-fijo" : "m2l-embebido";
    ["pointerdown", "mousedown"].forEach((ev) => teclado.addEventListener(ev, frenar));
    teclado.addEventListener("touchstart", frenar, { passive: false });
    const dentro = doc.createElement("div");
    dentro.className = "m2l-in";
    teclado.appendChild(dentro);

    const borrar = crearTecla("⌫", comando("deleteBackward"), { clase: "m2l-ancha", ayuda: "Borrar", repetir: true });
    const izquierda = crearTecla("◀", comando("moveToPreviousChar"), { ayuda: "Mover cursor a la izquierda", repetir: true });
    const derecha = crearTecla("▶", comando("moveToNextChar"), { ayuda: "Mover cursor a la derecha", repetir: true });
    const filas = [
      ["m2l-barra", TECLAS_BARRA.map(([texto, latex, ayuda]) => crearTecla(texto, insertar(latex), { ayuda }))],
      ["", letras(NUMEROS)],
      ["", letras(FILA_Q)],
      ["", [...letras(FILA_A), borrar]],
      ["", [...letras(FILA_Z), izquierda, derecha, crearAplicar()]],
    ];
    filas.forEach(([clase, teclas]) => {
      const fila = doc.createElement("div");
      fila.className = ("m2l-fila " + clase).trim();
      teclas.forEach((t) => fila.appendChild(t));
      dentro.appendChild(fila);
    });
    (P ? P.body : contenedor).appendChild(teclado);
  }

  function reservarEspacio(activo) {
    const main = P && principal();
    if (!main) return;
    main.style.transition = "padding-bottom .22s ease-out";
    main.style.paddingBottom = activo ? (teclado.offsetHeight + baseInferior) + "px" : "";
  }

  function ajustarIzquierda() {
    if (!P || !teclado) return;
    let izq = 0;
    try {
      const lateral = P.querySelector('[data-testid="stSidebar"]');
      if (lateral && P.defaultView.innerWidth > 640) {
        const r = lateral.getBoundingClientRect();
        if (r.width > 0 && r.right > 0) izq = Math.round(r.right);
      }
    } catch (e) {}
    if (teclado.style.left !== izq + "px") teclado.style.left = izq + "px";
    let base = 0;
    try {
      const enNube = /\.streamlit\.app$/i.test(window.location.hostname);
      if (enNube && P.defaultView.innerWidth - izq < 1300) base = INSIGNIA_ALTO;
    } catch (e) {}
    if (base !== baseInferior) {
      baseInferior = base;
      teclado.style.setProperty("--m2l-base", base + "px");
      if (visible) reservarEspacio(true);
    }
  }

  function asegurarVisible() {
    if (!P) return;
    setTimeout(() => {
      try {
        const marco = window.frameElement;
        if (!marco || !visible) return;
        const vista = P.defaultView, r = marco.getBoundingClientRect();
        let d = Math.max(0, r.bottom - (vista.innerHeight - teclado.offsetHeight - 8));
        if (r.top - d < 8) d = r.top - 8;
        if (Math.abs(d) < 2) return;
        const main = principal();
        (main && main.scrollHeight > main.clientHeight ? main : vista).scrollBy({ top: d, behavior: "smooth" });
      } catch (e) {}
    }, 80);
  }

  function mostrar() {
    if (visible || !teclado) return;
    visible = true;
    teclado.classList.add("m2l-visible");
    ajustarIzquierda();
    clearInterval(intervaloLateral);
    intervaloLateral = setInterval(ajustarIzquierda, 120);
    reservarEspacio(true);
    asegurarVisible();
    altura();
  }

  function ocultar() {
    if (!visible || !teclado) return;
    visible = false;
    teclado.classList.remove("m2l-visible");
    clearInterval(intervaloLateral);
    reservarEspacio(false);
    altura();
  }

  const alCambiarTamano = () => {
    if (visible) setTimeout(() => { ajustarIzquierda(); reservarEspacio(true); asegurarVisible(); }, 120);
  };
  const revisarFoco = () => setTimeout(() => {
    if (Date.now() >= tocandoHasta && (!document.hasFocus() || document.activeElement !== mf)) ocultar();
  }, 200);
  const tocoFuera = (e) => {
    if ((teclado && teclado.contains(e.target)) || (window.frameElement && window.frameElement.contains(e.target))) return;
    ocultar();
  };

  function retirar() {
    try {
      detenerRepeticion();
      clearInterval(intervaloLateral);
      reservarEspacio(false);
      if (P) {
        P.removeEventListener("pointerdown", tocoFuera, true);
        P.defaultView.removeEventListener("resize", alCambiarTamano);
      }
      if (teclado) teclado.remove();
      if (estilo) estilo.remove();
    } catch (e) {}
  }

  montar();
  if (P) {
    P.addEventListener("pointerdown", tocoFuera, true);
    P.defaultView.addEventListener("resize", alCambiarTamano);
  }
  window.addEventListener("pagehide", retirar);
  window.addEventListener("blur", revisarFoco);
  mf.addEventListener("focusin", () => { sinTecladoNativo(); mostrar(); });
  mf.addEventListener("click", () => { sinTecladoNativo(); mostrar(); });
  mf.addEventListener("focusout", revisarFoco);
  return sinTecladoNativo;
}
