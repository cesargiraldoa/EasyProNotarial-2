"use client";

import { useEffect, useRef, useState } from "react";
import { ChevronLeft, ChevronRight, HelpCircle, X } from "lucide-react";

export interface TourStep {
  targetId: string;
  titulo: string;
  texto: string;
  posicion?: "top" | "bottom" | "left" | "right";
}

export interface MinutasTourProps {
  steps: TourStep[];
  /** Whether the tour overlay is open — owned by parent */
  visible: boolean;
  /** Current step index — owned by parent */
  currentStep: number;
  onNext: () => void;
  onPrev: () => void;
  /** Close without marking as done */
  onSkip: () => void;
  /** Close and mark as done (last step) */
  onFinish: () => void;
  /** Re-open from step 0 (? button) */
  onRelaunch: () => void;
}

const TIP_W = 320;
const TIP_H = 210;
const GAP = 14;
const SPOT_PAD = 8;

const PRIMARY = "#0d2e5d";
const PRIMARY_RGBA = "rgba(13,46,93,";

interface Rect { top: number; left: number; width: number; height: number; }
interface TipPos {
  top: number;
  left: number;
  side: "top" | "bottom" | "left" | "right";
  arrowOffset: number;
}

function calcPos(rect: Rect, prefer?: TourStep["posicion"]): TipPos {
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  const cx = rect.left + rect.width / 2;
  const cy = rect.top + rect.height / 2;

  const clampX = (x: number) => Math.max(GAP, Math.min(vw - TIP_W - GAP, x));
  const clampY = (y: number) => Math.max(GAP, Math.min(vh - TIP_H - GAP, y));

  const order = prefer
    ? [prefer, "bottom", "top", "right", "left"]
    : ["bottom", "top", "right", "left"];

  for (const side of [...new Set(order)] as NonNullable<TourStep["posicion"]>[]) {
    if (side === "bottom" && vh - rect.top - rect.height > TIP_H + GAP * 2) {
      const left = clampX(cx - TIP_W / 2);
      return { top: rect.top + rect.height + SPOT_PAD + GAP, left, side: "bottom", arrowOffset: Math.max(16, Math.min(TIP_W - 24, cx - left)) };
    }
    if (side === "top" && rect.top > TIP_H + GAP * 2) {
      const left = clampX(cx - TIP_W / 2);
      return { top: rect.top - SPOT_PAD - TIP_H - GAP, left, side: "top", arrowOffset: Math.max(16, Math.min(TIP_W - 24, cx - left)) };
    }
    if (side === "right" && vw - rect.left - rect.width > TIP_W + GAP * 2) {
      const top = clampY(cy - TIP_H / 2);
      return { top, left: rect.left + rect.width + SPOT_PAD + GAP, side: "right", arrowOffset: Math.max(16, Math.min(TIP_H - 24, cy - top)) };
    }
    if (side === "left" && rect.left > TIP_W + GAP * 2) {
      const top = clampY(cy - TIP_H / 2);
      return { top, left: rect.left - SPOT_PAD - TIP_W - GAP, side: "left", arrowOffset: Math.max(16, Math.min(TIP_H - 24, cy - top)) };
    }
  }

  return { top: (vh - TIP_H) / 2, left: (vw - TIP_W) / 2, side: "bottom", arrowOffset: TIP_W / 2 };
}

function TipArrow({ pos }: { pos: TipPos }) {
  const lc = "#dfe7f2";
  const bc = "#ffffff";
  const base: React.CSSProperties = { position: "absolute", width: 0, height: 0 };
  const { side, arrowOffset } = pos;

  if (side === "bottom") return (
    <div style={{ ...base, top: -9, left: arrowOffset - 8, borderLeft: "8px solid transparent", borderRight: "8px solid transparent", borderBottom: `9px solid ${lc}` }}>
      <div style={{ ...base, top: 2, left: -7, borderLeft: "7px solid transparent", borderRight: "7px solid transparent", borderBottom: `7px solid ${bc}` }} />
    </div>
  );
  if (side === "top") return (
    <div style={{ ...base, bottom: -9, left: arrowOffset - 8, borderLeft: "8px solid transparent", borderRight: "8px solid transparent", borderTop: `9px solid ${lc}` }}>
      <div style={{ ...base, bottom: 2, left: -7, borderLeft: "7px solid transparent", borderRight: "7px solid transparent", borderTop: `7px solid ${bc}` }} />
    </div>
  );
  if (side === "right") return (
    <div style={{ ...base, left: -9, top: arrowOffset - 8, borderTop: "8px solid transparent", borderBottom: "8px solid transparent", borderRight: `9px solid ${lc}` }}>
      <div style={{ ...base, top: -7, left: 2, borderTop: "7px solid transparent", borderBottom: "7px solid transparent", borderRight: `7px solid ${bc}` }} />
    </div>
  );
  return (
    <div style={{ ...base, right: -9, top: arrowOffset - 8, borderTop: "8px solid transparent", borderBottom: "8px solid transparent", borderLeft: `9px solid ${lc}` }}>
      <div style={{ ...base, top: -7, right: 2, borderTop: "7px solid transparent", borderBottom: "7px solid transparent", borderLeft: `7px solid ${bc}` }} />
    </div>
  );
}

/**
 * MinutasTour — guided tour overlay.
 *
 * All navigation state (visible, currentStep) lives in the parent so that
 * workspace re-renders (file upload, form edits) don't reset the tour position.
 * This component only owns ephemeral visual state: spotlight rect and tooltip position.
 */
export function MinutasTour({
  steps,
  visible,
  currentStep,
  onNext,
  onPrev,
  onSkip,
  onFinish,
  onRelaunch,
}: MinutasTourProps) {
  // Visual-only state — safe to recompute any time visible/currentStep changes
  const [spotRect, setSpotRect] = useState<Rect | null>(null);
  const [tipPos, setTipPos] = useState<TipPos | null>(null);
  const [tooltipVisible, setTooltipVisible] = useState(false);
  const measureRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Measure target and position tooltip whenever visible or currentStep changes
  useEffect(() => {
    if (measureRef.current) clearTimeout(measureRef.current);

    if (!visible) {
      // Tour closed — reset visual state cleanly
      setSpotRect(null);
      setTipPos(null);
      setTooltipVisible(false);
      return;
    }

    setTooltipVisible(false);

    const step = steps[currentStep];
    const t = setTimeout(() => {
      const el = document.getElementById(step.targetId);

      if (!el) {
        // Target not in DOM (different wizard step) — centered tooltip, no spotlight
        setSpotRect(null);
        setTipPos({
          top: (window.innerHeight - TIP_H) / 2,
          left: (window.innerWidth - TIP_W) / 2,
          side: "bottom",
          arrowOffset: TIP_W / 2,
        });
        setTooltipVisible(true);
        return;
      }

      el.scrollIntoView({ behavior: "smooth", block: "center" });

      measureRef.current = setTimeout(() => {
        const r = el.getBoundingClientRect();
        const rect = { top: r.top, left: r.left, width: r.width, height: r.height };
        setSpotRect(rect);
        setTipPos(calcPos(rect, step.posicion));
        setTooltipVisible(true);
      }, 320);
    }, 80);

    return () => {
      clearTimeout(t);
      if (measureRef.current) clearTimeout(measureRef.current);
    };
  }, [visible, currentStep, steps]);

  // Re-measure on window resize while tour is open
  useEffect(() => {
    if (!visible) return;
    const onResize = () => {
      const step = steps[currentStep];
      const el = document.getElementById(step.targetId);
      if (!el) return;
      const r = el.getBoundingClientRect();
      const rect = { top: r.top, left: r.left, width: r.width, height: r.height };
      setSpotRect(rect);
      setTipPos(calcPos(rect, step.posicion));
    };
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, [visible, currentStep, steps]);

  const step = steps[currentStep];
  const isLast = currentStep === steps.length - 1;

  const sTop = spotRect ? spotRect.top - SPOT_PAD : 0;
  const sLeft = spotRect ? spotRect.left - SPOT_PAD : 0;
  const sW = spotRect ? spotRect.width + SPOT_PAD * 2 : 0;
  const sH = spotRect ? spotRect.height + SPOT_PAD * 2 : 0;

  return (
    <>
      {/* ── Help button — always in DOM, opens/restarts tour ──────────────── */}
      <button
        onClick={onRelaunch}
        aria-label="Ver tour guiado del módulo"
        title="Ver tour guiado"
        style={{
          position: "fixed", bottom: 24, right: 24, zIndex: 10002,
          width: 44, height: 44, borderRadius: "50%",
          background: PRIMARY, color: "#fff", border: "none",
          display: "flex", alignItems: "center", justifyContent: "center",
          cursor: "pointer",
          boxShadow: `0 4px 16px ${PRIMARY_RGBA}0.3)`,
        }}
      >
        <HelpCircle size={20} />
      </button>

      {visible && (
        <>
          {/* ── Transparent backdrop — captures clicks to close tour ───────── */}
          <div
            aria-hidden="true"
            style={{ position: "fixed", inset: 0, zIndex: 9998, cursor: "default" }}
            onClick={onSkip}
          />

          {/* ── Spotlight — box-shadow creates dark overlay around target ───── */}
          {spotRect && (
            <div
              aria-hidden="true"
              style={{
                position: "fixed",
                top: sTop, left: sLeft, width: sW, height: sH,
                borderRadius: 10,
                boxShadow: `0 0 0 9999px rgba(0,0,0,0.60), 0 0 0 2px ${PRIMARY}`,
                zIndex: 9999,
                pointerEvents: "none",
                animation: "ep-tour-spotlight-pulse 2s ease-in-out infinite",
              }}
            />
          )}

          {/* ── Plain overlay — fallback when target is not in DOM ─────────── */}
          {!spotRect && tooltipVisible && (
            <div
              aria-hidden="true"
              style={{
                position: "fixed", inset: 0,
                background: "rgba(0,0,0,0.60)",
                zIndex: 9999, pointerEvents: "none",
              }}
            />
          )}

          {/* ── Tooltip ────────────────────────────────────────────────────── */}
          {tipPos && (
            <div
              role="dialog"
              aria-label={`Tour paso ${currentStep + 1} de ${steps.length}: ${step.titulo}`}
              style={{
                position: "fixed",
                top: tipPos.top, left: tipPos.left, width: TIP_W,
                zIndex: 10001,
                background: "#ffffff",
                border: "1px solid #dfe7f2",
                borderRadius: 12,
                boxShadow: "0 8px 32px rgba(11,30,58,0.22), 0 1px 4px rgba(11,30,58,0.06)",
                padding: "18px 20px 16px",
                pointerEvents: "all",
                opacity: tooltipVisible ? 1 : 0,
                transform: tooltipVisible ? "scale(1) translateY(0)" : "scale(0.95) translateY(6px)",
                transition: "opacity 0.18s ease, transform 0.18s ease",
              }}
              onClick={e => e.stopPropagation()}
            >
              {spotRect && <TipArrow pos={tipPos} />}

              {/* Step badge + close */}
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
                <span style={{
                  fontSize: 11, fontWeight: 700, letterSpacing: "0.04em",
                  color: PRIMARY,
                  background: `${PRIMARY_RGBA}0.08)`,
                  padding: "2px 10px", borderRadius: 20,
                }}>
                  {currentStep + 1} / {steps.length}
                </span>
                <button
                  onClick={onSkip}
                  aria-label="Saltar tour"
                  style={{
                    background: "none", border: "none", cursor: "pointer",
                    color: "#7e8ea6", padding: 4,
                    display: "flex", alignItems: "center", borderRadius: 6,
                  }}
                >
                  <X size={14} />
                </button>
              </div>

              <h3 style={{ fontSize: 15, fontWeight: 600, color: "#141e38", margin: "0 0 8px", lineHeight: 1.35 }}>
                {step.titulo}
              </h3>

              <p style={{ fontSize: 13, lineHeight: 1.65, color: "#526082", margin: "0 0 16px" }}>
                {step.texto}
              </p>

              {/* Progress dots */}
              <div style={{ display: "flex", justifyContent: "center", gap: 5, marginBottom: 14 }}>
                {steps.map((_, i) => (
                  <div
                    key={i}
                    style={{
                      height: 6,
                      width: i === currentStep ? 20 : 6,
                      borderRadius: 3,
                      background: i === currentStep ? PRIMARY : i < currentStep ? `${PRIMARY_RGBA}0.32)` : "#ced9e8",
                      transition: "width 0.2s ease, background 0.2s ease",
                    }}
                  />
                ))}
              </div>

              {/* Navigation */}
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <button
                  onClick={onSkip}
                  style={{
                    background: "none", border: "none", cursor: "pointer",
                    fontSize: 12, color: "#7e8ea6",
                    textDecoration: "underline", textUnderlineOffset: 2,
                    padding: "4px 0", marginRight: "auto",
                  }}
                >
                  Saltar tour
                </button>

                {currentStep > 0 && (
                  <button
                    onClick={onPrev}
                    style={{
                      display: "flex", alignItems: "center", gap: 3,
                      background: "none", border: "1px solid #ced9e8",
                      borderRadius: 8, padding: "6px 12px",
                      fontSize: 12, fontWeight: 500, cursor: "pointer", color: "#526082",
                    }}
                  >
                    <ChevronLeft size={13} /> Anterior
                  </button>
                )}

                <button
                  onClick={isLast ? onFinish : onNext}
                  style={{
                    display: "flex", alignItems: "center", gap: 3,
                    background: PRIMARY, border: "none", borderRadius: 8,
                    padding: "6px 14px",
                    fontSize: 12, fontWeight: 600, cursor: "pointer", color: "#fff",
                  }}
                >
                  {isLast ? "No mostrar de nuevo" : <>Siguiente <ChevronRight size={13} /></>}
                </button>
              </div>
            </div>
          )}
        </>
      )}

      <style>{`
        @keyframes ep-tour-spotlight-pulse {
          0%, 100% { box-shadow: 0 0 0 9999px rgba(0,0,0,0.60), 0 0 0 2px #0d2e5d, 0 0 0 5px rgba(13,46,93,0.22); }
          50%       { box-shadow: 0 0 0 9999px rgba(0,0,0,0.60), 0 0 0 2px #0d2e5d, 0 0 0 9px rgba(13,46,93,0.07); }
        }
      `}</style>
    </>
  );
}
