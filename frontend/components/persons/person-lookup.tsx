"use client";

import { useState } from "react";
import { Search } from "lucide-react";
import { lookupPersons, type PersonPayload, type PersonRecord } from "@/lib/document-flow";

type PersonLookupProps = {
  onPick: (person: PersonRecord) => void;
  onNotFound: (person: PersonPayload) => void;
};

function blankPersonDraft(seed?: Partial<PersonPayload>): PersonPayload {
  return {
    document_type: "CC",
    document_number: "",
    full_name: "",
    sex: "",
    nationality: "Colombiana",
    marital_status: "",
    profession: "",
    municipality: "",
    is_transient: false,
    phone: "",
    address: "",
    email: "",
    metadata_json: "{}",
    ...seed,
  };
}

function PersonField({
  label,
  value,
  onChange,
  type = "text",
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
}) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-sm font-medium text-primary">{label}</span>
      <input
        type={type}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="ep-input h-11 rounded-xl px-3"
      />
    </label>
  );
}

export function PersonLookup({ onPick, onNotFound }: PersonLookupProps) {
  const [documentType, setDocumentType] = useState("CC");
  const [documentNumber, setDocumentNumber] = useState("");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<PersonRecord[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [draftPerson, setDraftPerson] = useState<PersonPayload>(() => blankPersonDraft());

  function openCreateForm() {
    setDraftPerson((current) =>
      blankPersonDraft({
        ...current,
        document_type: documentType || current.document_type,
        document_number: documentNumber || current.document_number,
        full_name: query || current.full_name,
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
      const data = await lookupPersons({ document_type: documentType, document_number: documentNumber, q: query });
      const safeResults = Array.isArray(data) ? data : [];
      setResults(safeResults);
      if (safeResults.length === 0) {
        setDraftPerson(
          blankPersonDraft({
            document_type: documentType,
            document_number: documentNumber,
            full_name: query,
          }),
        );
        setShowCreateForm(true);
      }
    } catch (issue) {
      setResults([]);
      setError(issue instanceof Error ? issue.message : "No fue posible buscar la persona.");
    } finally {
      setIsLoading(false);
    }
  }

  function saveNewPerson() {
    const nextDraft = {
      ...draftPerson,
      document_type: draftPerson.document_type.trim(),
      document_number: draftPerson.document_number.trim(),
      full_name: draftPerson.full_name.trim(),
      metadata_json: draftPerson.metadata_json || "{}",
    };

    if (!nextDraft.document_type || !nextDraft.document_number || !nextDraft.full_name || !nextDraft.marital_status || !nextDraft.municipality) {
      setError("Completa el tipo, número, nombre, estado civil y municipio de la persona.");
      return;
    }

    onNotFound(nextDraft);
  }

  return (
    <div className="ep-card-muted rounded-[1.5rem] p-4 space-y-4">
      <div className="grid gap-3 lg:grid-cols-[110px_minmax(0,1fr)_minmax(0,1fr)_auto]">
        <select
          value={documentType}
          onChange={(event) => setDocumentType(event.target.value)}
          className="ep-select h-11 rounded-xl px-3"
        >
          {["CC", "CE", "TI", "PP", "NIT"].map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
        <input
          value={documentNumber}
          onChange={(event) => setDocumentNumber(event.target.value)}
          placeholder="Número de documento"
          className="ep-input h-11 rounded-xl px-3"
        />
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Buscar por nombre"
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
        {isLoading ? <p className="text-sm text-secondary">Buscando persona...</p> : null}
        {error ? <p className="text-sm text-rose-500">{error}</p> : null}

        {!isLoading && results.length > 0 ? (
          <div className="space-y-2">
            <p className="text-sm font-medium text-primary">Resultados encontrados</p>
            {results.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => onPick(item)}
                className="flex w-full items-center justify-between rounded-xl border border-[var(--line)] px-3 py-3 text-left hover:bg-[var(--panel)]"
              >
                <div>
                  <p className="text-sm font-semibold text-primary">{item.full_name || "Sin nombre"}</p>
                  <p className="text-xs text-secondary">
                    {item.document_type || "DOC"} {item.document_number || "Sin número"} · {item.municipality || "Sin municipio"}
                  </p>
                </div>
                <span className="text-xs font-semibold text-primary">Usar este</span>
              </button>
            ))}
            <button
              type="button"
              onClick={openCreateForm}
              className="inline-flex items-center gap-2 text-sm font-semibold text-primary"
            >
              No encontré la persona
            </button>
          </div>
        ) : null}

        {!isLoading && !error && results.length === 0 && !showCreateForm ? (
          <p className="text-sm text-secondary">Sin resultados todavía.</p>
        ) : null}

        {showCreateForm ? (
          <div className="space-y-4 rounded-[1.25rem] border border-[var(--line)] bg-[var(--panel)] p-4">
            <div>
              <p className="text-sm font-semibold text-primary">Crear nueva persona</p>
              <p className="mt-1 text-sm text-secondary">Completa los datos para guardar y usar esta persona en el interviniente.</p>
            </div>

            <div className="grid gap-3 lg:grid-cols-2">
              <label className="flex flex-col gap-1">
                <span className="text-sm font-medium text-primary">Tipo de documento</span>
                <select
                  value={draftPerson.document_type}
                  onChange={(event) => setDraftPerson((current) => ({ ...current, document_type: event.target.value }))}
                  className="ep-select h-11 rounded-xl px-3"
                >
                  {["CC", "CE", "TI", "PP", "NIT"].map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </label>
              <PersonField
                label="Número de documento"
                value={draftPerson.document_number}
                onChange={(value) => setDraftPerson((current) => ({ ...current, document_number: value }))}
              />
              <PersonField
                label="Nombre completo"
                value={draftPerson.full_name}
                onChange={(value) => setDraftPerson((current) => ({ ...current, full_name: value }))}
              />
              <label className="flex flex-col gap-1">
                <span className="text-sm font-medium text-primary">Sexo</span>
                <select
                  value={draftPerson.sex || ""}
                  onChange={(event) => setDraftPerson((current) => ({ ...current, sex: event.target.value }))}
                  className="ep-select h-11 rounded-xl px-3"
                >
                  <option value="">Sin definir</option>
                  {["F", "M", "No especifica"].map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </label>
              <PersonField
                label="Nacionalidad"
                value={draftPerson.nationality || ""}
                onChange={(value) => setDraftPerson((current) => ({ ...current, nationality: value }))}
              />
              <PersonField
                label="Estado civil"
                value={draftPerson.marital_status || ""}
                onChange={(value) => setDraftPerson((current) => ({ ...current, marital_status: value }))}
              />
              <PersonField
                label="Profesión u oficio"
                value={draftPerson.profession || ""}
                onChange={(value) => setDraftPerson((current) => ({ ...current, profession: value }))}
              />
              <PersonField
                label="Municipio de domicilio"
                value={draftPerson.municipality || ""}
                onChange={(value) => setDraftPerson((current) => ({ ...current, municipality: value }))}
              />
              <PersonField
                label="Teléfono"
                value={draftPerson.phone || ""}
                onChange={(value) => setDraftPerson((current) => ({ ...current, phone: value }))}
              />
              <PersonField
                label="Email"
                type="email"
                value={draftPerson.email || ""}
                onChange={(value) => setDraftPerson((current) => ({ ...current, email: value }))}
              />
            </div>

            <div className="flex flex-col gap-1">
              <span className="text-sm font-medium text-primary">Dirección</span>
              <textarea
                value={draftPerson.address || ""}
                onChange={(event) => setDraftPerson((current) => ({ ...current, address: event.target.value }))}
                className="ep-input min-h-[96px] rounded-2xl px-4 py-3"
              />
            </div>

            <label className="flex items-center gap-3 rounded-2xl bg-[var(--panel-soft)] px-4 py-3 text-sm text-secondary">
              <input
                type="checkbox"
                checked={Boolean(draftPerson.is_transient)}
                onChange={(event) => setDraftPerson((current) => ({ ...current, is_transient: event.target.checked }))}
              />
              ¿Está de tránsito?
            </label>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => void saveNewPerson()}
                className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white"
              >
                Guardar y usar
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
