"""Visor propio de gráficas Plotly con botón de pantalla completa que conserva el zoom del usuario.

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
  #aviso {{ position: absolute; left: 10px; top: 10px; color: #ff6b6b; font: 13px sans-serif; z-index: 60; }}
</style></head>
<body>
<div id="caja">
  {grafica}
  <button id="pc" title="Pantalla completa (Esc para salir)">⛶ Pantalla completa</button>
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
    cuerpo = limpia.to_html(full_html=False, include_plotlyjs="cdn", div_id="grafica", default_width="100%",
                            default_height=f"{altura}px", config={"displaylogo": False, "responsive": True})
    botones_js = json.dumps(botones, cls=PlotlyJSONEncoder).replace("</", "<\\/")
    components.html(_PLANTILLA.format(grafica=cuerpo, altura=int(altura), botones=botones_js),
                    height=int(altura) + 6, scrolling=False)