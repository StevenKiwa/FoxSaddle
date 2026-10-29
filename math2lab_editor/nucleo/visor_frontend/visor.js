(function () {
  const ALTURA = __ALTURA__;
  const BOTONES = __BOTONES__;
  const $ = (id) => document.getElementById(id);
  const caja = $("caja"), gd = $("grafica"), pc = $("pc"), modo = $("modo"), aviso = $("aviso");
  const consulta = (q) => !!(window.matchMedia && window.matchMedia(q).matches);
  const tactil = navigator.maxTouchPoints > 0 || consulta("(pointer: coarse)");
  const movil = consulta("(hover: none) and (pointer: coarse)");
  let ultimoAncho = 0, ultimoAlto = 0, escala2D = 1, modoMover = false;

  const enPantallaCompleta = () => document.fullscreenElement === caja || document.webkitFullscreenElement === caja;
  const lista = () => window.Plotly && gd && gd.layout && gd._fullLayout;

  function ajustar() {
    if (!(window.Plotly && gd && gd.layout)) return;
    const ancho = Math.floor(caja.clientWidth);
    const alto = enPantallaCompleta() ? Math.floor(caja.clientHeight) : ALTURA;
    if (ancho < 50 || alto < 50 || (ancho === ultimoAncho && alto === ultimoAlto)) return;
    ultimoAncho = ancho;
    ultimoAlto = alto;
    gd.style.width = ancho + "px";
    gd.style.height = alto + "px";
    Plotly.relayout(gd, { width: ancho, height: alto });
  }

  function camaraActual() {
    try {
      const c = gd._fullLayout.scene._scene.getCamera();
      if (c && c.eye) return c;
    } catch (e) {}
    const cam = (gd.layout.scene && gd.layout.scene.camera) || {};
    return {
      eye: cam.eye || { x: 1.6, y: -1.6, z: 1.0 },
      up: cam.up || { x: 0, y: 0, z: 1 },
      center: cam.center || { x: 0, y: 0, z: 0 },
    };
  }

  function zoom3D(f) {
    const c = camaraActual(), e = c.eye;
    const n = Math.sqrt(e.x * e.x + e.y * e.y + e.z * e.z) || 1;
    const k = Math.min(Math.max(n * f, 0.35), 8) / n;
    Plotly.relayout(gd, { "scene.camera": { eye: { x: e.x * k, y: e.y * k, z: e.z * k }, up: c.up, center: c.center } });
  }

  function zoom2D(f) {
    const nueva = Math.min(Math.max(escala2D * f, 0.04), 25);
    const g = nueva / escala2D;
    escala2D = nueva;
    const escalar = (r) => {
      const m = (r[0] + r[1]) / 2, h = (r[1] - r[0]) / 2 * g;
      return [m - h, m + h];
    };
    Plotly.relayout(gd, { "xaxis.range": escalar(gd._fullLayout.xaxis.range), "yaxis.range": escalar(gd._fullLayout.yaxis.range) });
  }

  function zoom(f) {
    if (!lista()) return;
    if (gd._fullLayout.scene) zoom3D(f);
    else zoom2D(f);
  }

  function aplicarModo() {
    const completa = enPantallaCompleta();
    const desplazar = movil && !completa && !modoMover;
    caja.classList.toggle("desplazar", desplazar);
    caja.style.touchAction = tactil && !desplazar ? "none" : "";
    modo.hidden = !movil || completa;
    modo.textContent = modoMover ? "⇅ Desplazar la página" : "☝ Mover la gráfica";
    modo.classList.toggle("on", modoMover);
  }

  function alCambiarPantalla() {
    aplicarModo();
    pc.textContent = enPantallaCompleta() ? "✕ Salir de pantalla completa" : "⛶ Pantalla completa";
    ajustar();
    setTimeout(ajustar, 150);
    setTimeout(ajustar, 500);
  }

  function aplicarAccion(metodo, a) {
    if (metodo === "restyle") Plotly.restyle(gd, a[0], a[1]);
    else if (metodo === "relayout") Plotly.relayout(gd, a[0]);
    else if (metodo === "update") Plotly.update(gd, a[0], a[1], a[2]);
  }

  $("zmas").addEventListener("click", () => zoom(0.8));
  $("zmenos").addEventListener("click", () => zoom(1.25));
  modo.addEventListener("click", () => {
    modoMover = !modoMover;
    aplicarModo();
  });

  if (tactil) {
    const sinDesplazar = () => !caja.classList.contains("desplazar");
    ["touchstart", "touchmove"].forEach((ev) => caja.addEventListener(ev, (e) => {
      if (sinDesplazar() && e.touches && e.touches.length > 1) {
        e.stopPropagation();
        e.preventDefault();
      }
    }, { capture: true, passive: false }));
    ["gesturestart", "gesturechange", "gestureend"].forEach((ev) => caja.addEventListener(ev, (e) => {
      if (sinDesplazar()) e.preventDefault();
    }, { passive: false }));
  }

  pc.addEventListener("click", () => {
    try {
      if (enPantallaCompleta()) (document.exitFullscreen || document.webkitExitFullscreen).call(document);
      else (caja.requestFullscreen || caja.webkitRequestFullscreen).call(caja);
    } catch (e) {
      aviso.textContent = "El navegador no permitió la pantalla completa.";
    }
  });

  BOTONES.forEach((b) => {
    const el = document.createElement("button");
    let activo = false;
    el.className = "bt";
    el.textContent = b.label;
    el.addEventListener("click", () => {
      activo = !activo;
      aplicarAccion(b.metodo, activo ? b.args : (b.args2 || b.args));
      el.classList.toggle("on", activo);
    });
    $("botones").appendChild(el);
  });

  document.addEventListener("fullscreenchange", alCambiarPantalla);
  document.addEventListener("webkitfullscreenchange", alCambiarPantalla);
  new ResizeObserver(ajustar).observe(caja);
  window.addEventListener("resize", ajustar);
  window.addEventListener("load", () => setTimeout(ajustar, 200));
  setTimeout(() => {
    if (!window.Plotly) aviso.textContent = "No se pudo cargar Plotly (revisa tu conexión a internet).";
  }, 8000);
  aplicarModo();
})();
