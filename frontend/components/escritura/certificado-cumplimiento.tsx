"use client";

import { useEffect, useRef, type CSSProperties } from "react";
import type { Resultado } from "@/lib/motor-escritura";

type Cumplimiento = Resultado["cumplimiento"];
type Item = Cumplimiento["items"][number];

export type CertificadoCaso = {
  codigo?: string;
  acto?: string;
  notaria?: string;
  fecha?: string;
  corpusResumen?: string;
  verificacionUrl?: string;
};

type Estado = "verde" | "amarillo" | "rojo";

const COLORS: Record<Estado, { cert: string; deep: string }> = {
  verde: { cert: "#2F7D57", deep: "#1f5e40" },
  amarillo: { cert: "#B8791F", deep: "#8a5c14" },
  rojo: { cert: "#A3342E", deep: "#7d2621" },
};

function resolverEstado(c: Cumplimiento): Estado {
  if (c.tiles.bloqueante > 0) return "rojo";
  if (c.tiles.advertencia > 0) return "amarillo";
  return "verde";
}

function veredicto(estado: Estado): { titulo: string; icono: string; texto: string } {
  if (estado === "verde") return { titulo: "APTO", icono: "✓", texto: "sin observaciones" };
  if (estado === "amarillo") return { titulo: "REVISAR", icono: "!", texto: "apto con observaciones" };
  return { titulo: "BLOQUEADO", icono: "✕", texto: "con hallazgos bloqueantes" };
}

function conformidad(c: Cumplimiento): string {
  const total = c.tiles.cumple + c.tiles.advertencia + c.tiles.bloqueante;
  if (total === 0) return "100%";
  if (c.tiles.bloqueante > 0) return "—";
  return `${Math.round((c.tiles.cumple / total) * 100)}%`;
}

const STATUS_BY_TIPO: Record<Item["tipo"], "ok" | "warn" | "stop"> = {
  ok: "ok",
  warn: "warn",
  obl: "stop",
  crit: "stop",
};

// ---- guilloche (papel de seguridad) en canvas ----
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

export function CertificadoCumplimiento({ cumplimiento, caso }: { cumplimiento: Cumplimiento; caso?: CertificadoCaso }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const estado = resolverEstado(cumplimiento);
  const { cert, deep } = COLORS[estado];
  const v = veredicto(estado);

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
      ctx.strokeStyle = cert;
      ctx.lineWidth = 0.7;
      ctx.globalAlpha = 0.05;
      rose(ctx, w / 2, h * 0.34, Math.min(w, h) * 0.5, 9, 6);
      ctx.globalAlpha = 0.5;
      woven(ctx, w, h, 15);
    };
    draw();
    const ro = new ResizeObserver(draw);
    ro.observe(canvas);
    return () => ro.disconnect();
  }, [cert]);

  const grupos = cumplimiento.items;

  return (
    <div className="cert-cmp" style={{ "--cert": cert, "--deep": deep } as CSSProperties}>
      <style>{CSS}</style>

      <div className="cc-cert">
        <canvas ref={canvasRef} className="cc-guilloche" aria-hidden="true" />
        <div className="cc-inner">
          <div className="cc-top">
            <div>
              C&Oacute;DIGO DE VERIFICACI&Oacute;N<b>{caso?.codigo ?? "NC-—"}</b>
            </div>
            <div className="r">
              FECHA<b>{caso?.fecha ?? "—"}</b>
            </div>
          </div>

          <div className="cc-emblem">
            <div className="cc-mark">EN</div>
            <div className="cc-word">Ecosistema&nbsp;Notarial</div>
          </div>

          <div className="cc-title">CUMPLIMIENTO</div>
          <div className="cc-subtitle">Normativo verificado</div>

          <div className="cc-vlbl">Resultado de la verificaci&oacute;n</div>
          <p className="cc-verdict">{v.titulo}</p>
          <div className="cc-score">
            Conformidad <span className="pct">{conformidad(cumplimiento)}</span> &middot; {v.texto}
          </div>

          <div className="cc-counts">
            <div className="c ok">
              <b>{cumplimiento.tiles.cumple}</b>
              <span>cumple</span>
            </div>
            <div className="c warn">
              <b>{cumplimiento.tiles.advertencia}</b>
              <span>advertencia</span>
            </div>
            <div className="c stop">
              <b>{cumplimiento.tiles.bloqueante}</b>
              <span>bloqueo</span>
            </div>
          </div>

          <div className="cc-seals">
            <div className="cc-holo">
              <div className="t">MOTOR DE<br />REGLAS</div>
              <div className="chk">{"✓"}</div>
              <div className="t">VERIFICACI&Oacute;N<br />DETERMINISTA</div>
            </div>
            <div className="cc-certifies">
              Certifica que la escritura del caso <b>{caso?.codigo ?? "—"}</b>
              {caso?.acto ? <> ({caso.acto})</> : null}
              {caso?.notaria ? <>, de la <b>{caso.notaria}</b>,</> : null} fue sometida a verificaci&oacute;n normativa
              automatizada {caso?.corpusResumen ? <>bajo el <b>{caso.corpusResumen}</b></> : <>bajo el corpus vigente</>} con el resultado consignado.
            </div>
            <div className="cc-stamp">
              <svg viewBox="0 0 100 100" aria-hidden="true">
                <defs>
                  <path id="cc-sealring" d="M50,50 m-39,0 a39,39 0 1,1 78,0 a39,39 0 1,1 -78,0" />
                </defs>
                <circle className="s-ring1" cx="50" cy="50" r="47.5" />
                <circle className="s-ring2" cx="50" cy="50" r="43" />
                <text className="s-txt">
                  <textPath href="#cc-sealring" startOffset="0">
                    {"★ ECOSISTEMA NOTARIAL ★ CUMPLIMIENTO VERIFICADO "}
                  </textPath>
                </text>
                <circle className="s-core" cx="50" cy="50" r="20" />
                <text className="s-icon" x="50" y="50" textAnchor="middle" dominantBaseline="central">
                  {v.icono}
                </text>
              </svg>
            </div>
          </div>

          <div className="cc-foot">
            <div className="cc-barcode">
              <div className="bars" />
              <div className="code">{caso?.codigo ?? "NC —"}</div>
            </div>
            {caso?.verificacionUrl ? (
              <div className="cc-verify">
                Verificaci&oacute;n en l&iacute;nea<b>{caso.verificacionUrl}</b>
              </div>
            ) : null}
          </div>

          <div className="cc-ribbon">
            <span>Verificado</span>&middot;<span>Trazable</span>&middot;<span>Conforme a ley</span>
          </div>
        </div>
      </div>

      <div className="cc-detail">
        <h2>Detalle de la verificaci&oacute;n</h2>
        <p className="sub">Cada hallazgo sale del motor de reglas y cita su norma.</p>
        {grupos.map((item, index) => {
          const st = STATUS_BY_TIPO[item.tipo];
          return (
            <div className="cc-find" key={`${item.titulo}-${index}`}>
              <div className="fh">
                <span className={`st ${st}`}>{st === "ok" ? "✓" : st === "warn" ? "!" : "✕"}</span>
                <span className="h">{item.titulo}</span>
              </div>
              {item.detalle ? <p className="fd">{item.detalle}</p> : null}
              {item.norma ? <div className="norma">{item.norma}</div> : null}
            </div>
          );
        })}
      </div>
    </div>
  );
}

const CSS = `
.cert-cmp{--paper:#E7E4DB;--card:#fff;--ink:#1a2744;--muted:#6B6F77;--rule:#DAD6CB;
  font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:#2B2F36}
.cert-cmp .cc-cert{position:relative;background:var(--card);border-radius:5px;padding:30px 26px 0;
  box-shadow:0 12px 44px rgba(26,39,68,.16);border:2px solid var(--cert);overflow:hidden}
.cert-cmp .cc-guilloche{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:0}
.cert-cmp .cc-cert::before{content:"";position:absolute;inset:9px;border:1px solid color-mix(in srgb,var(--cert) 45%,transparent);border-radius:3px;pointer-events:none;z-index:1}
.cert-cmp .cc-inner{position:relative;z-index:2;text-align:center}
.cert-cmp .cc-top{display:flex;justify-content:space-between;font-family:ui-monospace,Menlo,monospace;font-size:9px;letter-spacing:.12em;color:var(--muted);text-transform:uppercase;text-align:left}
.cert-cmp .cc-top .r{text-align:right}
.cert-cmp .cc-top b{display:block;color:var(--ink);font-size:11px;letter-spacing:.05em;margin-top:2px}
.cert-cmp .cc-emblem{display:flex;flex-direction:column;align-items:center;gap:7px;margin:10px 0 4px}
.cert-cmp .cc-mark{width:40px;height:44px;background:var(--cert);clip-path:polygon(50% 0,100% 16%,100% 62%,50% 100%,0 62%,0 16%);display:grid;place-items:center;color:#fff;font-family:Georgia,serif;font-weight:700;font-size:19px}
.cert-cmp .cc-word{font-family:Georgia,serif;font-weight:700;color:var(--ink);font-size:13px;letter-spacing:.16em;text-transform:uppercase}
.cert-cmp .cc-title{font-family:Georgia,serif;font-weight:700;color:var(--ink);font-size:clamp(24px,5vw,36px);line-height:1.02;margin:2px 0 0}
.cert-cmp .cc-subtitle{font-weight:600;letter-spacing:.3em;text-transform:uppercase;font-size:11px;color:var(--deep);margin:6px 0 0}
.cert-cmp .cc-vlbl{font-weight:600;letter-spacing:.2em;text-transform:uppercase;font-size:11px;color:var(--muted);margin:20px 0 0}
.cert-cmp .cc-verdict{font-weight:800;color:var(--cert);line-height:.9;font-size:clamp(42px,11vw,74px);margin:2px 0 0}
.cert-cmp .cc-score{font-weight:700;font-size:14px;color:var(--ink);margin:10px 0 0}
.cert-cmp .cc-score .pct{color:var(--cert)}
.cert-cmp .cc-counts{display:flex;justify-content:center;gap:22px;margin:14px 0 0;font-family:ui-monospace,Menlo,monospace;font-size:12px}
.cert-cmp .cc-counts .c b{font-size:17px;display:block}
.cert-cmp .cc-counts .c.ok b{color:#2F7D57}
.cert-cmp .cc-counts .c.warn b{color:#B8791F}
.cert-cmp .cc-counts .c.stop b{color:#A3342E}
.cert-cmp .cc-counts .c span{color:var(--muted);font-size:10px;letter-spacing:.08em;text-transform:uppercase}
.cert-cmp .cc-seals{display:flex;justify-content:space-between;align-items:center;margin:22px 2px 0;gap:12px}
.cert-cmp .cc-holo{width:74px;height:92px;border-radius:10px;flex:none;position:relative;overflow:hidden;
  background:linear-gradient(135deg,#e4ebf6,#c4d0e8 32%,#f2f5fc 52%,#cdd9ee 72%,#e4ebf6);
  border:1px solid rgba(120,140,180,.5);box-shadow:0 3px 10px rgba(30,50,90,.14),inset 0 0 0 3px rgba(255,255,255,.45);
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px}
.cert-cmp .cc-holo::before{content:"";position:absolute;inset:0;pointer-events:none;mix-blend-mode:screen;
  background:linear-gradient(52deg,transparent 30%,rgba(150,110,215,.28) 43%,rgba(110,205,185,.28) 57%,transparent 70%)}
.cert-cmp .cc-holo>*{position:relative;z-index:1}
.cert-cmp .cc-holo .t{font-size:7px;font-weight:700;letter-spacing:.06em;color:#3d4d6d;text-align:center}
.cert-cmp .cc-holo .chk{width:26px;height:26px;border-radius:50%;background:var(--cert);color:#fff;display:grid;place-items:center;font-size:14px}
.cert-cmp .cc-certifies{max-width:52ch;margin:0 auto;font-family:Georgia,serif;font-size:11.5px;line-height:1.55;color:var(--muted);font-style:italic}
.cert-cmp .cc-certifies b{color:var(--ink);font-style:normal}
.cert-cmp .cc-stamp{width:96px;height:96px;flex:none}
.cert-cmp .cc-stamp svg{width:100%;height:100%;overflow:visible;transform:rotate(-8deg)}
.cert-cmp .cc-stamp .s-ring1{fill:none;stroke:var(--cert);stroke-width:2.4}
.cert-cmp .cc-stamp .s-ring2{fill:none;stroke:var(--cert);stroke-width:.6;stroke-dasharray:1.4 1.9;opacity:.85}
.cert-cmp .cc-stamp .s-txt{fill:var(--deep);font-family:system-ui,sans-serif;font-weight:700;font-size:6.3px;letter-spacing:1.05px}
.cert-cmp .cc-stamp .s-core{fill:var(--cert)}
.cert-cmp .cc-stamp .s-icon{fill:#fff;font-family:system-ui,sans-serif;font-weight:800;font-size:19px}
.cert-cmp .cc-foot{display:flex;justify-content:space-between;align-items:flex-end;margin:22px 0 0;gap:16px}
.cert-cmp .cc-barcode{text-align:left}
.cert-cmp .cc-barcode .bars{height:30px;width:150px;background:repeating-linear-gradient(90deg,var(--ink) 0 2px,transparent 2px 3px,var(--ink) 3px 4px,transparent 4px 7px,var(--ink) 7px 8px,transparent 8px 10px)}
.cert-cmp .cc-barcode .code{font-family:ui-monospace,Menlo,monospace;font-size:10px;letter-spacing:.1em;color:var(--muted);margin-top:4px}
.cert-cmp .cc-verify{text-align:right;font-family:ui-monospace,Menlo,monospace;font-size:9px;color:var(--muted)}
.cert-cmp .cc-verify b{display:block;color:var(--deep);font-size:10px;margin-top:2px}
.cert-cmp .cc-ribbon{margin:22px -26px 0;background:var(--cert);color:#fff;text-align:center;font-weight:700;letter-spacing:.3em;text-transform:uppercase;font-size:11px;padding:11px}
.cert-cmp .cc-ribbon span{opacity:.85;margin:0 8px}
.cert-cmp .cc-detail{background:var(--card);border:1px solid var(--rule);border-radius:12px;padding:20px 22px;margin-top:18px}
.cert-cmp .cc-detail h2{font-family:Georgia,serif;font-size:16px;color:var(--ink);margin:0 0 4px}
.cert-cmp .cc-detail .sub{color:var(--muted);font-size:12.5px;margin:0 0 14px}
.cert-cmp .cc-find{border:1px solid var(--rule);border-radius:10px;margin-bottom:10px;padding:12px 14px}
.cert-cmp .cc-find .fh{display:flex;align-items:center;gap:10px}
.cert-cmp .cc-find .st{width:20px;height:20px;border-radius:6px;display:grid;place-items:center;font-size:11px;font-weight:700;flex:none}
.cert-cmp .cc-find .st.ok{background:#e3f0e8;color:#2F7D57}
.cert-cmp .cc-find .st.warn{background:#f6ecda;color:#B8791F}
.cert-cmp .cc-find .st.stop{background:#f4e2e0;color:#A3342E}
.cert-cmp .cc-find .h{font-weight:600;color:var(--ink);font-size:13.5px}
.cert-cmp .cc-find .fd{margin:6px 0 0;color:var(--muted);font-size:12.5px;line-height:1.5}
.cert-cmp .cc-find .norma{margin:8px 0 0;font-family:ui-monospace,Menlo,monospace;font-size:10.5px;color:#9B2D3A;background:#f3e3e4;border:1px solid #e6c9cb;border-radius:5px;padding:3px 8px;display:inline-block}
`;
