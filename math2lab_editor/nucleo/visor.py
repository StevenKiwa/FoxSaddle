
import json

import plotly.graph_objects as go
import streamlit as st
from plotly.utils import PlotlyJSONEncoder

_PLANTILLA = """<!doctype html>
<html><head><meta charset="utf-8">
<style>
  html, body {{ margin: 0; padding: 0; background: #0a0a12; overflow: hidden; }}
  #caja {{ position: relative; box-sizing: border-box; background: #0a0a12; border: 1px solid rgba(0,245,255,.25); border-radius: 10px;
           box-shadow: 0 0 14px rgba(0,245,255,.15); overflow: hidden; }}
  #caja:fullscreen {{ border: none; border-radius: 0; box-shadow: none; }}
  #izq {{ position: absolute; left: 10px; bottom: 10px; z-index: 50; display: flex; flex-direction: column;
          align-items: flex-start; gap: 6px; }}
  #pc {{ background: #12121f; color: #00f5ff;
         border: 1px solid #00f5ff; border-radius: 6px; padding: 4px 10px; font: 12px Inter, "Segoe UI", sans-serif;
         cursor: pointer; box-shadow: 0 0 8px rgba(0,245,255,.35); }}
  #pc:hover {{ background: rgba(0,245,255,.15); box-shadow: 0 0 14px rgba(0,245,255,.8); }}
  #botones {{ position: absolute; right: 12px; bottom: 12px; z-index: 50; display: flex; flex-direction: column;
              align-items: flex-end; gap: 6px; }}
  .bt {{ background: #12121f; color: #00f5ff; border: 1px solid #00f5ff; border-radius: 6px; padding: 4px 12px;
         font: 12px Inter, "Segoe UI", sans-serif; cursor: pointer; box-shadow: 0 0 8px rgba(0,245,255,.35); }}
  .bt:hover {{ background: rgba(0,245,255,.15); box-shadow: 0 0 14px rgba(0,245,255,.8); }}
  .bt.on {{ background: #00f5ff; color: #0a0a12; font-weight: 600; box-shadow: 0 0 14px rgba(0,245,255,.9); }}
  #zoom {{ position: absolute; top: 10px; right: 10px; z-index: 50; display: flex; gap: 6px; }}
  .zb {{ width: 40px; height: 40px; padding: 0; display: flex; align-items: center; justify-content: center;
         background: #12121f; color: #00f5ff; border: 1px solid #00f5ff; border-radius: 8px; cursor: pointer;
         box-shadow: 0 0 8px rgba(0,245,255,.35); touch-action: manipulation; -webkit-tap-highlight-color: transparent; }}
  .zb:hover {{ background: rgba(0,245,255,.15); box-shadow: 0 0 14px rgba(0,245,255,.8); }}
  .zb:active {{ background: rgba(0,245,255,.35); }}
  .zb svg {{ width: 24px; height: 24px; }}
  #aviso {{ position: absolute; left: 10px; top: 10px; color: #ff6b6b; font: 13px sans-serif; z-index: 60; }}

  #modo {{ padding: 8px 14px; font-size: 13px; }}
  #modo[hidden] {{ display: none; }}
  #caja.desplazar #grafica {{ pointer-events: none; }}
</style></head>
<body>
<div id="caja">
  {grafica}
  <div id="izq">
    <button id="modo" class="bt" hidden></button>
    <button id="pc" title="Pantalla completa (Esc para salir)">⛶ Pantalla completa</button>
  </div>
  <div id="zoom">
    <button class="zb" id="zmas" title="Acercar (hacer más grande)" aria-label="Acercar">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
        <circle cx="10" cy="10" r="6.5"/><line x1="15" y1="15" x2="21" y2="21"/>
        <line x1="7" y1="10" x2="13" y2="10"/><line x1="10" y1="7" x2="10" y2="13"/></svg>
    </button>
    <button class="zb" id="zmenos" title="Alejar (hacer más pequeño)" aria-label="Alejar">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
        <circle cx="10" cy="10" r="6.5"/><line x1="15" y1="15" x2="21" y2="21"/>
        <line x1="7" y1="10" x2="13" y2="10"/></svg>
    </button>
  </div>
  <div id="botones"></div>
  <div id="aviso"></div>
</div>
<script>
  var ALTURA = {altura};
  var BOTONES = {botones};
  var caja = document.getElementById("caja"), gd = document.getElementById("grafica"), pc = document.getElementById("pc");
  var ultimoAncho = 0, ultimoAlto = 0;
  function enPantallaCompleta() {{ return document.fullscreenElement === caja || document.webkitFullscreenElement === caja; }}

  // Ajusta la gráfica al tamaño REAL del recuadro (no al de la ventana, que aún puede estar cambiando).
  // Solo cambia el tamaño: es la misma gráfica, así que la cámara y el zoom del usuario no se tocan.
  function ajustar() {{
    if (!(window.Plotly && gd && gd.layout)) return;
    var completa = enPantallaCompleta();
    var ancho = Math.floor(caja.clientWidth);
    var alto = completa ? Math.floor(caja.clientHeight) : ALTURA;
    if (ancho < 50 || alto < 50 || (ancho === ultimoAncho && alto === ultimoAlto)) return;
    ultimoAncho = ancho; ultimoAlto = alto;
    gd.style.width = ancho + "px"; gd.style.height = alto + "px";
    Plotly.relayout(gd, {{ width: ancho, height: alto }});
  }}

  var escala2D = 1;                                           
  function lista() {{ return window.Plotly && gd && gd.layout && gd._fullLayout; }}
  function camaraActual() {{                                  
    try {{ var c = gd._fullLayout.scene._scene.getCamera(); if (c && c.eye) return c; }} catch (e) {{}}
    var cam = (gd.layout.scene && gd.layout.scene.camera) || {{}};
    return {{ eye: cam.eye || {{ x: 1.6, y: -1.6, z: 1.0 }}, up: cam.up || {{ x: 0, y: 0, z: 1 }}, center: cam.center || {{ x: 0, y: 0, z: 0 }} }};
  }}
  function zoom(f) {{
    if (!lista()) return;
    if (gd._fullLayout.scene) {{                              
      var c = camaraActual(), e = c.eye, n = Math.sqrt(e.x * e.x + e.y * e.y + e.z * e.z) || 1;
      var k = Math.min(Math.max(n * f, 0.35), 8) / n;         
      Plotly.relayout(gd, {{ "scene.camera": {{ eye: {{ x: e.x * k, y: e.y * k, z: e.z * k }}, up: c.up, center: c.center }} }});
    }} else {{                                                
      var nueva = Math.min(Math.max(escala2D * f, 0.04), 25);
      var g = nueva / escala2D; escala2D = nueva;
      function escalar(r) {{ var m = (r[0] + r[1]) / 2, h = (r[1] - r[0]) / 2 * g; return [m - h, m + h]; }}
      Plotly.relayout(gd, {{ "xaxis.range": escalar(gd._fullLayout.xaxis.range), "yaxis.range": escalar(gd._fullLayout.yaxis.range) }});
    }}
  }}
  document.getElementById("zmas").addEventListener("click", function () {{ zoom(0.8); }});
  document.getElementById("zmenos").addEventListener("click", function () {{ zoom(1.25); }});


  var tactil = (navigator.maxTouchPoints > 0) || (window.matchMedia && window.matchMedia("(pointer: coarse)").matches);

  var movil = !!(window.matchMedia && window.matchMedia("(hover: none) and (pointer: coarse)").matches);
  var modoMover = false, modo = document.getElementById("modo");
  function aplicarModo() {{
    var completa = enPantallaCompleta();
    var desplazar = movil && !completa && !modoMover;           
    caja.classList.toggle("desplazar", desplazar);
    caja.style.touchAction = (tactil && !desplazar) ? "none" : "";   
    modo.hidden = !movil || completa;
    modo.textContent = modoMover ? "⇅ Desplazar la página" : "Mover gráfica";
    modo.classList.toggle("on", modoMover);
  }}
  modo.addEventListener("click", function () {{ modoMover = !modoMover; aplicarModo(); }});
  if (tactil) {{
    ["touchstart", "touchmove"].forEach(function (ev) {{
      caja.addEventListener(ev, function (e) {{
        if (!caja.classList.contains("desplazar") && e.touches && e.touches.length > 1) {{ e.stopPropagation(); e.preventDefault(); }}
      }}, {{ capture: true, passive: false }});
    }});
    ["gesturestart", "gesturechange", "gestureend"].forEach(function (ev) {{      // iOS Safari
      caja.addEventListener(ev, function (e) {{ if (!caja.classList.contains("desplazar")) e.preventDefault(); }}, {{ passive: false }});
    }});
  }}
  aplicarModo();

  function actualizarBoton() {{
    pc.textContent = enPantallaCompleta() ? "✕ Salir de pantalla completa" : "⛶ Pantalla completa";
  }}
  function alCambiarPantalla() {{
    aplicarModo();
    actualizarBoton();
    ajustar();
    setTimeout(ajustar, 150); setTimeout(ajustar, 500);      
  }}
  pc.addEventListener("click", function () {{
    try {{
      if (enPantallaCompleta()) {{ (document.exitFullscreen || document.webkitExitFullscreen).call(document); }}
      else {{ (caja.requestFullscreen || caja.webkitRequestFullscreen).call(caja); }}
    }} catch (e) {{ document.getElementById("aviso").textContent = "El navegador no permitió la pantalla completa."; }}
  }});

  function aplicarAccion(metodo, a) {{
    if (metodo === "restyle") Plotly.restyle(gd, a[0], a[1]);
    else if (metodo === "relayout") Plotly.relayout(gd, a[0]);
    else if (metodo === "update") Plotly.update(gd, a[0], a[1], a[2]);
  }}
  BOTONES.forEach(function (b) {{
    var el = document.createElement("button"), activo = false;
    el.className = "bt"; el.textContent = b.label;
    el.addEventListener("click", function () {{
      activo = !activo;
      aplicarAccion(b.metodo, activo ? b.args : (b.args2 || b.args));
      el.classList.toggle("on", activo);
    }});
    document.getElementById("botones").appendChild(el);
  }});
  document.addEventListener("fullscreenchange", alCambiarPantalla);
  document.addEventListener("webkitfullscreenchange", alCambiarPantalla);
  new ResizeObserver(ajustar).observe(caja);                  
  window.addEventListener("resize", ajustar);
  window.addEventListener("load", function () {{ setTimeout(ajustar, 200); }});
  setTimeout(function () {{
    if (!window.Plotly) document.getElementById("aviso").textContent =
      "No se pudo cargar Plotly (revisa tu conexión a internet).";
  }}, 8000);
</script>
</body></html>"""


def _extraer_botones(fig):

    botones = []
    for menu in fig.to_plotly_json()["layout"].get("updatemenus", []) or []:
        for b in menu.get("buttons", []):
            botones.append({"label": b.get("label", ""), "metodo": b.get("method", "restyle"),
                            "args": b.get("args", []), "args2": b.get("args2")})
    return botones


def _mostrar_html(html, alto):

    if hasattr(st, "iframe"):
        st.iframe(html, width="stretch", height=alto)
    else:                                      
        import streamlit.components.v1 as components
        components.html(html, height=alto, scrolling=False)


def visor_plotly(fig, altura):
    botones = _extraer_botones(fig)
    limpia = go.Figure(fig)
    limpia.layout.updatemenus = []      
    if "scene" not in fig.to_plotly_json()["layout"]:
        limpia.layout.dragmode = "pan"  
    cuerpo = limpia.to_html(full_html=False, include_plotlyjs="cdn", div_id="grafica", default_width="100%",
                            default_height=f"{altura}px", config={"displayModeBar": False, "displaylogo": False,
                                                     "responsive": True, "doubleClick": False})
    botones_js = json.dumps(botones, cls=PlotlyJSONEncoder).replace("</", "<\\/")
    _mostrar_html(_PLANTILLA.format(grafica=cuerpo, altura=int(altura), botones=botones_js), int(altura) + 6)
