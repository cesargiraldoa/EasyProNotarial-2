"use client";

import { useState } from "react";
import { Search } from "lucide-react";
import { lookupPersons, type PersonRecord } from "@/lib/document-flow";

export function PersonLookup({ onPick }: { onPick: (person: PersonRecord) => void }) {
  const [documentType, setDocumentType] = useState("CC");
  const [documentNumber, setDocumentNumber] = useState("");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<PersonRecord[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runLookup() {
    setIsLoading(true);
    setError(null);
    try {
      const data = await lookupPersons({ document_type: documentType, document_number: documentNumber, q: query });
      setResults(Array.isArray(data) ? data : []);
    } catch (issue) {
      setResults([]);
      setError(issue instanceof Error ? issue.message : "No fue posible buscar la persona.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="ep-card-muted rounded-[1.5rem] p-4">
      <div className="grid gap-3 lg:grid-cols-[110px_minmax(0,1fr)_minmax(0,1fr)_auto]">
        <select value={documentType} onChange={(event) => setDocumentType(event.target.value)} className="ep-select h-11 rounded-xl px-3">
          {["CC", "CE", "TI", "PP", "NIT"].map((item) => <option key={item} value={item}>{item}</option>)}
        </select>
        <input value={documentNumber} onChange={(event) => setDocumentNumber(event.target.value)} placeholder="Número de documento" className="ep-input h-11 rounded-xl px-3" />
        <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar por nombre" className="ep-input h-11 rounded-xl px-3" />
        <button type="button" onClick={() => void runLookup()} className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white"><Search className="h-4 w-4" />Buscar</button>
      </div>
      <div className="mt-3 space-y-2">
        {isLoading ? <p className="text-sm text-secondary">Buscando persona...</p> : null}
        {error ? <p className="text-sm text-rose-500">{error}</p> : null}
        {!isLoading && !error && results.length === 0 ? <p className="text-sm text-secondary">Sin resultados todavía.</p> : null}
        {results.map((item) => (
          <button key={item.id} type="button" onClick={() => onPick(item)} className="flex w-full items-center justify-between rounded-xl border border-[var(--line)] px-3 py-3 text-left hover:bg-[var(--panel)]">
            <div>
              <p className="text-sm font-semibold text-primary">{item.full_name || "Sin nombre"}</p>
              <p className="text-xs text-secondary">{item.document_type || "DOC"} {item.document_number || "Sin número"} · {item.municipality || "Sin municipio"}</p>
            </div>
            <span className="text-xs font-semibold text-primary">Reutilizar</span>
          </button>
        ))}
      </div>
    </div>
  );
}

