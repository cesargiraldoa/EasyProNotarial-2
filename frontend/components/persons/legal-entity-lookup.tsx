"use client";

import { useState } from "react";
import { Search } from "lucide-react";
import {
  searchLegalEntities,
  type LegalEntityPayload,
  type LegalEntityRecord,
} from "@/lib/legal-entities";

export type { LegalEntityPayload, LegalEntityRecord } from "@/lib/legal-entities";

type LegalEntityLookupProps = {
  onPick: (entity: LegalEntityRecord) => void;
  onNotFound: (entity: LegalEntityPayload) => void;
};

function blankEntityDraft(seed?: Partial<LegalEntityPayload>): LegalEntityPayload {
  return {
    nit: "",
    name: "",
    legal_representative: "",
    municipality: "",
    address: "",
    phone: "",
    email: "",
    ...seed,
  };
}

function EntityField({
  label,
  value,
  onChange,
  type = "text",
  required = false,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  required?: boolean;
}) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-sm font-medium text-primary">
        {label}
        {required ? " *" : ""}
      </span>
      <input
        type={type}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="ep-input h-11 rounded-xl px-3"
      />
    </label>
  );
}

export function LegalEntityLookup({ onPick, onNotFound }: LegalEntityLookupProps) {
  const [searchText, setSearchText] = useState("");
  const [results, setResults] = useState<LegalEntityRecord[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [draftEntity, setDraftEntity] = useState<LegalEntityPayload>(() => blankEntityDraft());

  function openCreateForm() {
    setDraftEntity((current) =>
      blankEntityDraft({
        ...current,
        nit: current.nit || searchText,
        name: current.name || searchText,
      }),
    );
    setShowCreateForm(true);
    setError(null);
  }

  async function runLookup() {
    setIsLoading(true);
    setError(null);
    setShowCreateForm(false);
    try {
      const data = await searchLegalEntities(searchText);
      const safeResults = Array.isArray(data) ? data : [];
      setResults(safeResults);
      if (safeResults.length === 0) {
        setDraftEntity((current) =>
          blankEntityDraft({
            ...current,
            nit: current.nit || searchText,
            name: current.name || searchText,
          }),
        );
        setShowCreateForm(true);
      }
    } catch (issue) {
      setResults([]);
      setError(issue instanceof Error ? issue.message : "No fue posible buscar la entidad.");
    } finally {
      setIsLoading(false);
    }
  }

  function saveNewEntity() {
    const nextDraft = {
      ...draftEntity,
      nit: draftEntity.nit.trim(),
      name: draftEntity.name.trim(),
      legal_representative: draftEntity.legal_representative?.trim() || "",
      municipality: draftEntity.municipality?.trim() || "",
      address: draftEntity.address?.trim() || "",
      phone: draftEntity.phone?.trim() || "",
      email: draftEntity.email?.trim() || "",
    };

    if (!nextDraft.nit || !nextDraft.name) {
      setError("Completa el NIT y el nombre de la entidad.");
      return;
    }

    onNotFound(nextDraft);
  }

  return (
    <div className="ep-card-muted rounded-[1.5rem] p-4 space-y-4">
      <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_auto]">
        <input
          value={searchText}
          onChange={(event) => setSearchText(event.target.value)}
          placeholder="Buscar por NIT o nombre"
          className="ep-input h-11 rounded-xl px-3"
        />
        <button
          type="button"
          onClick={() => void runLookup()}
          className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white"
        >
          <Search className="h-4 w-4" />
          Buscar
        </button>
      </div>

      <div className="space-y-3">
        {isLoading ? <p className="text-sm text-secondary">Buscando entidad...</p> : null}
        {error ? <p className="text-sm text-rose-500">{error}</p> : null}

        {!isLoading && results.length > 0 ? (
          <div className="space-y-2">
            <p className="text-sm font-medium text-primary">Resultados encontrados</p>
            {results.map((entity) => (
              <button
                key={entity.id}
                type="button"
                onClick={() => onPick(entity)}
                className="flex w-full flex-col items-start justify-between rounded-xl border border-[var(--line)] px-3 py-3 text-left hover:bg-[var(--panel)]"
              >
                <p className="text-sm font-semibold text-primary">{entity.name || "Sin nombre"}</p>
                <p className="text-xs text-secondary">{entity.nit || "Sin NIT"}{entity.municipality ? ` · ${entity.municipality}` : ""}</p>
              </button>
            ))}
            <button
              type="button"
              onClick={openCreateForm}
              className="inline-flex items-center gap-2 text-sm font-semibold text-primary"
            >
              No encontré la entidad
            </button>
          </div>
        ) : null}

        {!isLoading && !error && results.length === 0 && !showCreateForm ? (
          <p className="text-sm text-secondary">Sin resultados todavía.</p>
        ) : null}

        {showCreateForm ? (
          <div className="space-y-4 rounded-[1.25rem] border border-[var(--line)] bg-[var(--panel)] p-4">
            <div>
              <p className="text-sm font-semibold text-primary">Crear nueva entidad jurídica</p>
              <p className="mt-1 text-sm text-secondary">Completa los datos para guardar y usar esta entidad.</p>
            </div>

            <div className="grid gap-3 lg:grid-cols-2">
              <EntityField
                label="NIT"
                value={draftEntity.nit}
                required
                onChange={(value) => setDraftEntity((current) => ({ ...current, nit: value }))}
              />
              <EntityField
                label="Nombre"
                value={draftEntity.name}
                required
                onChange={(value) => setDraftEntity((current) => ({ ...current, name: value }))}
              />
              <EntityField
                label="Representante legal"
                value={draftEntity.legal_representative || ""}
                onChange={(value) => setDraftEntity((current) => ({ ...current, legal_representative: value }))}
              />
              <EntityField
                label="Municipio"
                value={draftEntity.municipality || ""}
                onChange={(value) => setDraftEntity((current) => ({ ...current, municipality: value }))}
              />
              <EntityField
                label="Dirección"
                value={draftEntity.address || ""}
                onChange={(value) => setDraftEntity((current) => ({ ...current, address: value }))}
              />
              <EntityField
                label="Teléfono"
                value={draftEntity.phone || ""}
                onChange={(value) => setDraftEntity((current) => ({ ...current, phone: value }))}
              />
              <EntityField
                label="Email"
                type="email"
                value={draftEntity.email || ""}
                onChange={(value) => setDraftEntity((current) => ({ ...current, email: value }))}
              />
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => void saveNewEntity()}
                className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white"
              >
                Guardar
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="inline-flex items-center gap-2 text-sm font-semibold text-primary"
              >
                Volver a buscar
              </button>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
