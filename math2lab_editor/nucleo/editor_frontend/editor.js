(function () {
  const $ = (id) => document.getElementById(id);
  const mf = $("mf"), estado = $("estado"), contenedor = $("contenedor");
  let pendiente = null, version = null, aplicado = "", listo = false, ultimaAltura = 0;

  const enviar = (tipo, datos) => window.parent.postMessage({ isStreamlitMessage: true, type: tipo, ...datos }, "*");

  function altura() {
    const h = Math.ceil(contenedor.getBoundingClientRect().height);
    if (Math.abs(h - ultimaAltura) < 2) return;
    ultimaAltura = h;
    enviar("streamlit:setFrameHeight", { height: h });
  }

  function marcar() {
    const sinAplicar = mf.value !== aplicado;
    estado.className = sinAplicar ? "pendiente" : "";
    estado.textContent = sinAplicar ? "● Cambios sin aplicar: pulsa Enter o «Aplicar»." : "Fórmula aplicada.";
  }

  function poner(latex) {
    if (mf.setValue) mf.setValue(latex);
    else mf.value = latex;
    aplicado = mf.value;
    marcar();
  }

  function aplicar() {
    aplicado = mf.value;
    marcar();
    enviar("streamlit:setComponentValue", { value: { latex: mf.value, n: Date.now() }, dataType: "json" });
  }

  function sincronizar() {
    if (!pendiente) return;
    if (pendiente.version !== version) {
      version = pendiente.version;
      poner(pendiente.latex);
    }
    altura();
  }

  window.addEventListener("message", (ev) => {
    if (ev.data && ev.data.type === "streamlit:render") {
      pendiente = ev.data.args;
      if (listo) sincronizar();
    }
  });

  const sinTecladoNativo = crearTeclado({ mf, contenedor, estaListo: () => listo, marcar, aplicar, altura });

  customElements.whenDefined("math-field").then(() => {
    mf.mathVirtualKeyboardPolicy = "manual";
    sinTecladoNativo();
    mf.addEventListener("input", marcar);
    mf.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        aplicar();
      }
    }, true);
    listo = true;
    sincronizar();
  });

  $("aplicar").addEventListener("click", aplicar);

  setTimeout(() => {
    if (!customElements.get("math-field")) {
      estado.className = "fallo";
      estado.textContent = "No se pudo cargar el editor visual (revisa tu conexión a internet). Usa «Escribir como texto» más abajo.";
      altura();
    }
  }, 8000);

  new ResizeObserver(altura).observe(contenedor);
  enviar("streamlit:componentReady", { apiVersion: 1 });
})();
