"use client";

import { useMemo, useState } from "react";
import { ChevronDown, Search } from "lucide-react";

type Option = { value: string; label: string };

export function SearchableSelect({ label, value, options = [], onChange, placeholder = "Buscar..." }: { label: string; value: string; options?: Option[]; onChange: (value: string) => void; placeholder?: string }) {
  const [query, setQuery] = useState("");
  const safeOptions = Array.isArray(options) ? options : [];
  const filtered = useMemo(() => safeOptions.filter((item) => String(item?.label ?? "").toLowerCase().includes(query.toLowerCase())), [safeOptions, query]);
  return (
    <div className="grid gap-2 text-sm font-medium text-primary">
      <span>{label}</span>
      <div className="relative overflow-visible ep-card-muted rounded-2xl p-3">
        <div className="flex items-center gap-2 rounded-xl border border-[var(--line)] bg-[var(--input)] px-3 py-2">
          <Search className="h-4 w-4 text-secondary" />
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder={placeholder} className="w-full bg-transparent text-sm text-primary outline-none placeholder:text-secondary" />
          <ChevronDown className="h-4 w-4 text-secondary" />
        </div>
        <div className="absolute left-0 right-0 top-full z-50 mt-2 max-h-[200px] space-y-1 overflow-y-auto rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-2 shadow-lg">
          {filtered.length === 0 ? <div className="rounded-xl px-3 py-2 text-sm text-secondary">Sin opciones.</div> : null}
          {filtered.map((item) => (
            <button key={item.value} type="button" onClick={() => { onChange(item.value); setQuery(item.label); }} className={`flex w-full items-center justify-between rounded-xl px-3 py-2 text-left text-sm transition ${value === item.value ? "bg-primary text-white" : "hover:bg-[var(--panel)] text-primary"}`}>
              <span>{item.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
