const CSS_TECLADO = `
#m2l-teclado { display: none; background: #0a0a12; padding: 8px 8px calc(8px + env(safe-area-inset-bottom, 0px));
    font-family: Inter, "Segoe UI", sans-serif; -webkit-user-select: none; user-select: none; touch-action: manipulation;
    -webkit-tap-highlight-color: transparent; box-sizing: border-box; }
#m2l-teclado.m2l-visible { display: block; }
#m2l-teclado.m2l-fijo { position: fixed; left: 0; right: 0; bottom: 0; z-index: 999990;
    border-top: 1px solid rgba(0,245,255,.45); box-shadow: 0 -4px 18px rgba(0,245,255,.22);
    display: block; transform: translateY(100%); visibility: hidden; pointer-events: none;
    transition: transform .22s ease-out, visibility 0s linear .22s; will-change: transform; }
#m2l-teclado.m2l-fijo.m2l-visible { transform: translateY(0); visibility: visible; pointer-events: auto;
    transition: transform .22s ease-out, visibility 0s; }
@media (prefers-reduced-motion: reduce) {
  #m2l-teclado.m2l-fijo, #m2l-teclado.m2l-fijo.m2l-visible { transition: none; }
}
#m2l-teclado.m2l-embebido { position: static; margin-top: 8px; border-radius: 10px; border: 1px solid rgba(0,245,255,.3); }
#m2l-teclado .m2l-in { max-width: 900px; margin: 0 auto; display: flex; flex-direction: column; gap: 6px; }
#m2l-teclado .m2l-fila { display: flex; gap: 6px; }
#m2l-teclado .m2l-barra { display: grid; grid-template-columns: repeat(14, 1fr); }
#m2l-teclado .m2l-k { flex: 1 1 0; min-width: 0; height: 40px; margin: 0; padding: 0; background: #12121f; color: #b6ff3b;
    border: 1px solid rgba(182,255,59,.45); border-radius: 6px; font: 400 15px Inter, "Segoe UI", sans-serif;
    cursor: pointer; transition: all .15s; line-height: 1; }
#m2l-teclado .m2l-k:active { background: rgba(182,255,59,.3); box-shadow: 0 0 8px rgba(182,255,59,.6); }
#m2l-teclado .m2l-ancha { flex: 0 0 22%; }
#m2l-teclado .m2l-ap { color: #00f5ff; border-color: #00f5ff; box-shadow: 0 0 10px rgba(0,245,255,.35); }
#m2l-teclado .m2l-ap:active { background: rgba(0,245,255,.25); box-shadow: 0 0 18px rgba(0,245,255,.85); }
@media (hover: hover) {
  #m2l-teclado .m2l-k:hover { background: rgba(182,255,59,.15); box-shadow: 0 0 8px rgba(182,255,59,.6); }
  #m2l-teclado .m2l-ap:hover { background: rgba(0,245,255,.12); box-shadow: 0 0 18px rgba(0,245,255,.85); }
}
@media (max-width: 600px) {
  #m2l-teclado .m2l-k { height: 38px; font-size: 14px; }
}
@media (max-width: 600px) and (min-height: 501px) {
  #m2l-teclado .m2l-barra { grid-template-columns: repeat(7, 1fr); }
}
@media (max-height: 500px) {
  #m2l-teclado { padding: 4px 6px calc(4px + env(safe-area-inset-bottom, 0px)); }
  #m2l-teclado .m2l-in, #m2l-teclado .m2l-fila { gap: 4px; }
  #m2l-teclado .m2l-k { height: 30px; font-size: 13px; border-radius: 5px; }
}`;
