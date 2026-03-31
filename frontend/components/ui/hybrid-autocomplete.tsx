"use client";

import { useMemo } from "react";

export function HybridAutocomplete({ label, value, options = [], onChange, placeholder = "" }: { label: string; value: string; options?: string[]; onChange: (value: string) => void; placeholder?: string }) {
  const safeValue = typeof value === "string" ? value : "";
  const safeOptions = Array.isArray(options) ? options : [];
  const suggestions = useMemo(() => safeOptions.filter((item) => item.toLowerCase().includes(safeValue.toLowerCase())).slice(0, 6), [safeOptions, safeValue]);
  const listId = `${label}-options`.replace(/\s+/g, "-").toLowerCase();

  return (
    <label className="grid gap-2 text-sm font-medium text-primary">
      <span>{label}</span>
      <input value={safeValue} onChange={(event) => onChange(event.target.value)} list={listId} placeholder={placeholder} className="ep-input h-12 rounded-2xl px-4" />
      <datalist id={listId}>
        {suggestions.map((item) => <option key={item} value={item} />)}
      </datalist>
    </label>
  );
}
