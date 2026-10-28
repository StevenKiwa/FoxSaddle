"""Visor propio de gráficas Plotly con botón de pantalla completa que conserva el zoom del usuario.

La barra de herramientas de Plotly está oculta: los únicos controles son «Pantalla completa», «Decimales», «Curvas de
nivel» (solo en 3D) y los botones de lupa (+ / −) de la esquina superior derecha. En pantallas táctiles el pellizco con
dos dedos se bloquea, porque hacía que el zoom «se volviera loco»: el zoom se hace con los botones de lupa.

El botón «Pantalla completa» de Streamlit vuelve a crear la gráfica y el zoom se pierde. Aquí la gráfica vive en
un iframe con Plotly.js y el botón solo cambia su tamaño (la misma gráfica, sin recrearla), así la cámara y el
zoom quedan exactamente donde los dejó el usuario. Plotly.js se descarga de internet (CDN) al abrir la página.
"""
import json

import plotly.graph_objects as go
import streamlit.components.v1 as components
from plotly.utils import PlotlyJSONEncoder

_PLANTILLA = """<!doctype html>
<html><head><meta charset="utf-8">
<style>
  html, body {{ margin: 0; padding: 0; background: #0a0a12; overflow: hidden; }}
  #caja {{ position: relative; box-sizing: border-box; background: #0a0a12; border: 1px solid rgba(0,245,255,.25); border-radius: 10px;
           box-shadow: 0 0 14px rgba(0,245,255,.15); overflow: hidden; }}
  #caja:fullscreen {{ border: none; border-radius: 0; box-shadow: none; }}
  #pc {{ position: absolute; left: 10px; bottom: 10px; z-index: 50; background: #12121f; color: #00f5ff;
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
</style></head>
<body>
<div id="caja">
  {grafica}
  <button id="pc" title="Pantalla completa (Esc para salir)">⛶ Pantalla completa</button>
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
  // ---- Zoom con los botones de lupa. f < 1 acerca (más grande), f > 1 aleja (más pequeño).
  var escala2D = 1;                                           // zoom acumulado en las gráficas 2D (1 = vista inicial)
  function lista() {{ return window.Plotly && gd && gd.layout && gd._fullLayout; }}
  function camaraActual() {{                                  // cámara 3D vigente (incluye lo que giró el usuario)
    try {{ var c = gd._fullLayout.scene._scene.getCamera(); if (c && c.eye) return c; }} catch (e) {{}}
    var cam = (gd.layout.scene && gd.layout.scene.camera) || {{}};
    return {{ eye: cam.eye || {{ x: 1.6, y: -1.6, z: 1.0 }}, up: cam.up || {{ x: 0, y: 0, z: 1 }}, center: cam.center || {{ x: 0, y: 0, z: 0 }} }};
  }}
  function zoom(f) {{
    if (!lista()) return;
    if (gd._fullLayout.scene) {{                              // 3D: acercar o alejar la cámara conservando hacia dónde mira
      var c = camaraActual(), e = c.eye, n = Math.sqrt(e.x * e.x + e.y * e.y + e.z * e.z) || 1;
      var k = Math.min(Math.max(n * f, 0.35), 8) / n;         // distancia limitada: ni dentro del modelo ni perdido
      Plotly.relayout(gd, {{ "scene.camera": {{ eye: {{ x: e.x * k, y: e.y * k, z: e.z * k }}, up: c.up, center: c.center }} }});
    }} else {{                                                // 2D: se reducen o amplían los rangos de los ejes, alrededor de su centro
      var nueva = Math.min(Math.max(escala2D * f, 0.04), 25);
      var g = nueva / escala2D; escala2D = nueva;
      function escalar(r) {{ var m = (r[0] + r[1]) / 2, h = (r[1] - r[0]) / 2 * g; return [m - h, m + h]; }}
      Plotly.relayout(gd, {{ "xaxis.range": escalar(gd._fullLayout.xaxis.range), "yaxis.range": escalar(gd._fullLayout.yaxis.range) }});
    }}
  }}
  document.getElementById("zmas").addEventListener("click", function () {{ zoom(0.8); }});
  document.getElementById("zmenos").addEventListener("click", function () {{ zoom(1.25); }});

  // ---- Pantallas táctiles: sin pellizco (los dos dedos volvían loco el zoom); un dedo gira/mueve la gráfica.
  var tactil = (navigator.maxTouchPoints > 0) || (window.matchMedia && window.matchMedia("(pointer: coarse)").matches);
  if (tactil) {{
    caja.style.touchAction = "none";                          // el navegador no hace zoom ni desplaza la página sobre la gráfica
    ["touchstart", "touchmove"].forEach(function (ev) {{
      caja.addEventListener(ev, function (e) {{
        if (e.touches && e.touches.length > 1) {{ e.stopPropagation(); e.preventDefault(); }}
      }}, {{ capture: true, passive: false }});
    }});
    ["gesturestart", "gesturechange", "gestureend"].forEach(function (ev) {{      // iOS Safari
      caja.addEventListener(ev, function (e) {{ e.preventDefault(); }}, {{ passive: false }});
    }});
  }}

  function actualizarBoton() {{
    pc.textContent = enPantallaCompleta() ? "✕ Salir de pantalla completa" : "⛶ Pantalla completa";
  }}
  function alCambiarPantalla() {{
    actualizarBoton();
    ajustar();
    setTimeout(ajustar, 150); setTimeout(ajustar, 500);      // por si el navegador termina de agrandar después
  }}
  pc.addEventListener("click", function () {{
    try {{
      if (enPantallaCompleta()) {{ (document.exitFullscreen || document.webkitExitFullscreen).call(document); }}
      else {{ (caja.requestFullscreen || caja.webkitRequestFullscreen).call(caja); }}
    }} catch (e) {{ document.getElementById("aviso").textContent = "El navegador no permitió la pantalla completa."; }}
  }});
  // Botones propios (arriba el primero): posición fija en píxeles, no dependen del tamaño de la gráfica.
  // Cada uno alterna entre args (activar) y args2 (desactivar) y empieza desactivado.
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
  new ResizeObserver(ajustar).observe(caja);                  // también si cambia el ancho de la columna
  window.addEventListener("resize", ajustar);
  window.addEventListener("load", function () {{ setTimeout(ajustar, 200); }});
  setTimeout(function () {{
    if (!window.Plotly) document.getElementById("aviso").textContent =
      "No se pudo cargar Plotly (revisa tu conexión a internet).";
  }}, 8000);
</script>
</body></html>"""


def _extraer_botones(fig):
    """Botones de la figura (updatemenus) como lista simple: etiqueta, método y argumentos de activar/desactivar."""
    botones = []
    for menu in fig.to_plotly_json()["layout"].get("updatemenus", []) or []:
        for b in menu.get("buttons", []):
            botones.append({"label": b.get("label", ""), "metodo": b.get("method", "restyle"),
                            "args": b.get("args", []), "args2": b.get("args2")})
    return botones


def visor_plotly(fig, altura):
    """Dibuja la figura de Plotly en un iframe con botón de pantalla completa que conserva el zoom.
    Los botones de la figura se dibujan como botones HTML fijos en la esquina inferior derecha."""
    botones = _extraer_botones(fig)
    limpia = go.Figure(fig)
    limpia.layout.updatemenus = []      # asignación directa: update_layout(updatemenus=[]) NO borra los existentes
    if "scene" not in fig.to_plotly_json()["layout"]:
        limpia.layout.dragmode = "pan"  # 2D: con el dedo o el mouse se mueve la gráfica (el zoom va con las lupas)
    cuerpo = limpia.to_html(full_html=False, include_plotlyjs="cdn", div_id="grafica", default_width="100%",
                            default_height=f"{altura}px", config={"displayModeBar": False, "displaylogo": False,
                                                     "responsive": True, "doubleClick": False})
    botones_js = json.dumps(botones, cls=PlotlyJSONEncoder).replace("</", "<\\/")
    components.html(_PLANTILLA.format(grafica=cuerpo, altura=int(altura), botones=botones_js),
                    height=int(altura) + 6, scrolling=False)
