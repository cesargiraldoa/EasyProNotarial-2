"use client";

import { useEffect, useRef } from "react";

export type CalculadoraCaso = {
  codigo?: string;
  tarifasRef?: string;
  baseGravable?: string;
};

const CERT = "#3F6E63";

function rose(ctx: CanvasRenderingContext2D, cx: number, cy: number, R: number, k: number, layers: number) {
  for (let L = 0; L < layers; L++) {
    const rr = R * (1 - L * 0.16);
    ctx.beginPath();
    for (let t = 0; t <= Math.PI * 2 + 0.01; t += 0.02) {
      const r = rr * (0.55 + 0.45 * Math.cos(k * t));
      const x = cx + r * Math.cos(t);
      const y = cy + r * Math.sin(t);
      if (t === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
  }
}
function woven(ctx: CanvasRenderingContext2D, w: number, h: number, inset: number) {
  const amp = 3.4;
  const wl = 13;
  for (let p = 0; p < 2; p++) {
    const ph = p * Math.PI;
    ctx.beginPath();
    for (let i = inset; i <= w - inset; i++) {
      const y = inset + amp + amp * Math.sin(i / wl + ph);
      i === inset ? ctx.moveTo(i, y) : ctx.lineTo(i, y);
    }
    ctx.stroke();
    ctx.beginPath();
    for (let i = inset; i <= w - inset; i++) {
      const y = h - inset - amp - amp * Math.sin(i / wl + ph);
      i === inset ? ctx.moveTo(i, y) : ctx.lineTo(i, y);
    }
    ctx.stroke();
    ctx.beginPath();
    for (let j = inset; j <= h - inset; j++) {
      const x = inset + amp + amp * Math.sin(j / wl + ph);
      j === inset ? ctx.moveTo(x, j) : ctx.lineTo(x, j);
    }
    ctx.stroke();
    ctx.beginPath();
    for (let j = inset; j <= h - inset; j++) {
      const x = w - inset - amp - amp * Math.sin(j / wl + ph);
      j === inset ? ctx.moveTo(x, j) : ctx.lineTo(x, j);
    }
    ctx.stroke();
  }
}

export function CalculadoraLiquidacion({ liquidacionHtml, caso }: { liquidacionHtml: string; caso?: CalculadoraCaso }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const draw = () => {
      const w = canvas.clientWidth;
      const h = canvas.clientHeight;
      if (!w || !h) return;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);
      ctx.strokeStyle = CERT;
      ctx.lineWidth = 0.7;
      ctx.globalAlpha = 0.05;
      rose(ctx, w / 2, h * 0.28, Math.min(w, h) * 0.5, 9, 6);
      ctx.globalAlpha = 0.5;
      woven(ctx, w, h, 15);
    };
    draw();
    const ro = new ResizeObserver(draw);
    ro.observe(canvas);
    return () => ro.disconnect();
  }, []);

  return (
    <div className="calc-liq">
      <style>{CSS}</style>
      <div className="cl-cert">
        <canvas ref={canvasRef} className="cl-guilloche" aria-hidden="true" />
        <div className="cl-inner">
          <div className="cl-top">
            <div>
              CASO<b>{caso?.codigo ?? "—"}</b>
            </div>
            <div className="r">
              TARIFAS<b>{caso?.tarifasRef ?? "SNR vigentes"}</b>
            </div>
          </div>

          <div className="cl-emblem">
            <div className="cl-mark">EN</div>
            <div className="cl-word">Ecosistema&nbsp;Notarial</div>
          </div>

          <div className="cl-title">LIQUIDACI&Oacute;N</div>
          <div className="cl-subtitle">Calculadora &middot; derechos y tributos</div>

          <div className="cl-body" dangerouslySetInnerHTML={{ __html: liquidacionHtml }} />

          {caso?.baseGravable ? (
            <div className="cl-base">
              Base gravable <b>{caso.baseGravable}</b>
            </div>
          ) : null}

          <div className="cl-ribbon">
            <span>Liquidado</span>&middot;<span>Tarifas vigentes</span>&middot;<span>Trazable</span>
          </div>
        </div>
      </div>
    </div>
  );
}

const CSS = `
.calc-liq{--cert:#3F6E63;--deep:#2c5049;--card:#fff;--ink:#1a2744;--muted:#6B6F77;--rule:#DAD6CB;
  font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:#2B2F36}
.calc-liq .cl-cert{position:relative;background:var(--card);border-radius:5px;padding:30px 26px 0;
  box-shadow:0 12px 44px rgba(26,39,68,.16);border:2px solid var(--cert);overflow:hidden}
.calc-liq .cl-guilloche{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:0}
.calc-liq .cl-cert::before{content:"";position:absolute;inset:9px;border:1px solid color-mix(in srgb,var(--cert) 45%,transparent);border-radius:3px;pointer-events:none;z-index:1}
.calc-liq .cl-inner{position:relative;z-index:2;text-align:center}
.calc-liq .cl-top{display:flex;justify-content:space-between;font-family:ui-monospace,Menlo,monospace;font-size:9px;letter-spacing:.12em;color:var(--muted);text-transform:uppercase;text-align:left}
.calc-liq .cl-top .r{text-align:right}
.calc-liq .cl-top b{display:block;color:var(--ink);font-size:11px;letter-spacing:.05em;margin-top:2px}
.calc-liq .cl-emblem{display:flex;flex-direction:column;align-items:center;gap:7px;margin:10px 0 4px}
.calc-liq .cl-mark{width:40px;height:44px;background:var(--cert);clip-path:polygon(50% 0,100% 16%,100% 62%,50% 100%,0 62%,0 16%);display:grid;place-items:center;color:#fff;font-family:Georgia,serif;font-weight:700;font-size:19px}
.calc-liq .cl-word{font-family:Georgia,serif;font-weight:700;color:var(--ink);font-size:13px;letter-spacing:.16em;text-transform:uppercase}
.calc-liq .cl-title{font-family:Georgia,serif;font-weight:700;color:var(--ink);font-size:clamp(24px,5vw,36px);line-height:1.02;margin:2px 0 0}
.calc-liq .cl-subtitle{font-weight:600;letter-spacing:.28em;text-transform:uppercase;font-size:11px;color:var(--deep);margin:6px 0 2px}
.calc-liq .cl-body{text-align:left;margin:16px auto 0;max-width:620px}
.calc-liq .cl-body table{width:100%;border-collapse:collapse;font-size:12.5px}
.calc-liq .cl-body th{font-family:ui-monospace,Menlo,monospace;font-size:9.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);text-align:left;padding:0 8px 8px;border-bottom:2px solid color-mix(in srgb,var(--cert) 35%,var(--rule))}
.calc-liq .cl-body td{padding:8px;border-bottom:1px solid var(--rule);color:var(--ink);vertical-align:top}
.calc-liq .cl-body td:last-child,.calc-liq .cl-body th:last-child{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.calc-liq .cl-body tr:last-child td{border-top:2px solid var(--cert);border-bottom:none;font-weight:700;color:var(--deep)}
.calc-liq .cl-body p{margin:6px 0;color:var(--ink);font-size:12.5px;line-height:1.5}
.calc-liq .cl-base{text-align:right;margin:12px 0 0;font-family:ui-monospace,Menlo,monospace;font-size:11px;color:var(--muted)}
.calc-liq .cl-base b{color:var(--deep)}
.calc-liq .cl-ribbon{margin:20px -26px 0;background:var(--cert);color:#fff;text-align:center;font-weight:700;letter-spacing:.3em;text-transform:uppercase;font-size:11px;padding:11px}
.calc-liq .cl-ribbon span{opacity:.85;margin:0 8px}
`;
