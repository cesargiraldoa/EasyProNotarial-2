"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowLeft, Loader2, Plus, Save, ScrollText } from "lucide-react";
import {
  getPlantillaAdmin,
  listPlantillasAdmin,
  savePlantillaAdmin,
  type PlantillaAdminItem,
} from "@/lib/api-escritura";
import { searchLegalEntities, type LegalEntityRecord } from "@/lib/legal-entities";
import type { ActoCode } from "@/lib/motor-escritura";

const ACTOS: Array<[ActoCode, string]> = [
  ["compraventa", "Compraventa"],
  ["hipoteca", "Compraventa + Hipoteca"],
  ["cancelacion", "Cancelación de hipoteca"],
];
const FUENTES: Array<[string, string]> = [
  ["banco", "Banco"],
  ["particular", "Particular"],
  ["proyecto", "Proyecto"],
];

const inputClass =
  "w-full rounded-lg border border-line-strong bg-white px-3 py-2 text-sm text-primary shadow-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20";
const labelClass = "mb-1 block text-xs font-semibold uppercase tracking-[0.04em] text-secondary";

function actoLabel(code: string): string {
  return ACTOS.find(([c]) => c === code)?.[1] ?? code;
}

export function MoldesRegistro() {
  const [items, setItems] = useState<PlantillaAdminItem[]>([]);
  const [bancos, setBancos] = useState<LegalEntityRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const [editId, setEditId] = useState<number | null>(null);
  const [acto, setActo] = useState<ActoCode>("hipoteca");
  const [fuente, setFuente] = useState<string>("banco");
  const [legalEntityId, setLegalEntityId] = useState<number | null>(null);
  const [name, setName] = useState("");
  const [bodyHtml, setBodyHtml] = useState("");
  const [editorOpen, setEditorOpen] = useState(false);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setItems(await listPlantillasAdmin());
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudieron cargar los moldes.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    searchLegalEntities("")
      .then(setBancos)
      .catch(() => setBancos([]));
  }, []);

  function nuevo() {
    setEditId(null);
    setActo("hipoteca");
    setFuente("banco");
    setLegalEntityId(null);
    setName("");
    setBodyHtml("");
    setFeedback(null);
    setEditorOpen(true);
  }

  async function editar(id: number) {
    setFeedback(null);
    setError(null);
    try {
      const detail = await getPlantillaAdmin(id);
      setEditId(detail.id);
      setActo((detail.acto as ActoCode) || "hipoteca");
      setFuente(detail.fuente || "banco");
      setLegalEntityId(detail.legal_entity_id ?? null);
      setName(detail.name);
      setBodyHtml(detail.body_html);
      setEditorOpen(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo abrir el molde.");
    }
  }

  async function guardar() {
    if (!name.trim()) {
      setError("Ponle un nombre al molde.");
      return;
    }
    if (!bodyHtml.trim()) {
      setError("El cuerpo del molde no puede estar vacío.");
      return;
    }
    if (fuente === "banco" && legalEntityId == null) {
      setError("Elige el banco para este molde (o cambia la fuente a Particular).");
      return;
    }
    setSaving(true);
    setError(null);
    setFeedback(null);
    try {
      const saved = await savePlantillaAdmin({
        acto,
        fuente,
        legal_entity_id: fuente === "banco" ? legalEntityId : null,
        name: name.trim(),
        body_html: bodyHtml,
      });
      setEditId(saved.id);
      setFeedback(`Molde "${saved.name}" guardado. Ya se usa al elegir ${actoLabel(saved.acto)}${saved.bank_name ? ` con ${saved.bank_name}` : ""}.`);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo guardar el molde.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <Link href="/dashboard/escritura" className="inline-flex items-center gap-2 text-sm font-semibold text-secondary hover:text-primary">
          <ArrowLeft className="h-4 w-4" aria-hidden="true" />
          Volver a Minutas Asistidas
        </Link>
        <h1 className="mt-3 flex items-center gap-2 font-serif text-3xl font-semibold text-primary">
          <ScrollText className="h-7 w-7" aria-hidden="true" />
          Registro de moldes
        </h1>
        <p className="mt-1 max-w-3xl text-sm leading-6 text-secondary">
          Crea y edita las minutas base (moldes) por acto y banco, tú mismo, sin tocar código. Lo que guardes aquí se usa
          al instante cuando el protocolista elige ese acto y banco.
        </p>
      </div>

      {error ? (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">{error}</div>
      ) : null}
      {feedback ? (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-semibold text-emerald-700">{feedback}</div>
      ) : null}

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-[380px_minmax(0,1fr)]">
        {/* Lista */}
        <div className="space-y-3">
          <button
            type="button"
            onClick={nuevo}
            className="inline-flex w-full items-center justify-center gap-2 rounded-xl border border-primary bg-primary px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary/90"
          >
            <Plus className="h-4 w-4" aria-hidden="true" />
            Nuevo molde
          </button>
          <div className="rounded-xl border border-line-strong bg-white p-2 shadow-sm">
            {loading ? (
              <p className="px-2 py-6 text-center text-sm text-secondary">Cargando moldes…</p>
            ) : items.length === 0 ? (
              <p className="px-2 py-6 text-center text-sm text-secondary">Aún no hay moldes. Crea el primero con “Nuevo molde”.</p>
            ) : (
              <ul className="divide-y divide-line">
                {items.map((item) => (
                  <li key={item.id}>
                    <button
                      type="button"
                      onClick={() => editar(item.id)}
                      className={`w-full rounded-lg px-3 py-2 text-left transition hover:bg-primary/5 ${editId === item.id ? "bg-primary/8" : ""}`}
                    >
                      <span className="block text-sm font-semibold text-primary">{item.name}</span>
                      <span className="mt-0.5 block text-xs text-secondary">
                        {actoLabel(item.acto)} · {item.bank_name ?? (item.fuente || "genérico")}
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Editor */}
        <div className="rounded-xl border border-line-strong bg-white p-4 shadow-sm">
          {!editorOpen ? (
            <p className="py-16 text-center text-sm text-secondary">
              Elige un molde de la lista para editarlo, o crea uno nuevo.
            </p>
          ) : (
            <div className="space-y-4">
              <p className="text-sm font-bold text-primary">{editId ? "Editar molde" : "Nuevo molde"}</p>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <div>
                  <label className={labelClass} htmlFor="molde-acto">Acto</label>
                  <select id="molde-acto" className={inputClass} value={acto} onChange={(e) => setActo(e.currentTarget.value as ActoCode)}>
                    {ACTOS.map(([code, label]) => (
                      <option key={code} value={code}>{label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className={labelClass} htmlFor="molde-fuente">Fuente</label>
                  <select id="molde-fuente" className={inputClass} value={fuente} onChange={(e) => setFuente(e.currentTarget.value)}>
                    {FUENTES.map(([code, label]) => (
                      <option key={code} value={code}>{label}</option>
                    ))}
                  </select>
                </div>
              </div>

              {fuente === "banco" ? (
                <div>
                  <label className={labelClass} htmlFor="molde-banco">Banco</label>
                  <select
                    id="molde-banco"
                    className={inputClass}
                    value={legalEntityId ?? ""}
                    onChange={(e) => setLegalEntityId(e.currentTarget.value ? Number(e.currentTarget.value) : null)}
                  >
                    <option value="">— Seleccionar banco —</option>
                    {bancos.map((banco) => (
                      <option key={banco.id ?? banco.nit} value={banco.id ?? ""}>{banco.name} · NIT {banco.nit}</option>
                    ))}
                  </select>
                  <p className="mt-1 text-xs text-secondary">Si dejas la fuente en Particular/Proyecto, el molde es genérico del acto (sin banco).</p>
                </div>
              ) : null}

              <div>
                <label className={labelClass} htmlFor="molde-nombre">Nombre del molde</label>
                <input
                  id="molde-nombre"
                  className={inputClass}
                  value={name}
                  placeholder="Ej: Bancolombia · Compraventa + Hipoteca"
                  onChange={(e) => setName(e.currentTarget.value)}
                />
              </div>

              <div>
                <label className={labelClass} htmlFor="molde-body">Cuerpo (HTML con {"{{tokens}}"} y condicionales [[if …]])</label>
                <textarea
                  id="molde-body"
                  className={`${inputClass} min-h-[420px] resize-y font-mono text-xs leading-5`}
                  value={bodyHtml}
                  placeholder="Pega aquí el HTML del molde. Usa {{matricula}}, {{V.0.nombre}}, etc., y [[if credito]]…[[/if]] para bloques condicionales."
                  onChange={(e) => setBodyHtml(e.currentTarget.value)}
                  spellCheck={false}
                />
                <p className="mt-1 text-xs text-secondary">
                  El formulario rellena los {"{{tokens}}"} con los datos del caso. Consejo: parte de un molde existente (ábrelo, cópialo y ajústalo).
                </p>
              </div>

              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={guardar}
                  disabled={saving}
                  className="inline-flex items-center gap-2 rounded-xl border border-primary bg-primary px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {saving ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <Save className="h-4 w-4" aria-hidden="true" />}
                  Guardar molde
                </button>
                <button
                  type="button"
                  onClick={() => setEditorOpen(false)}
                  className="rounded-xl border border-line-strong px-4 py-2 text-sm font-semibold text-secondary hover:text-primary"
                >
                  Cerrar
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
