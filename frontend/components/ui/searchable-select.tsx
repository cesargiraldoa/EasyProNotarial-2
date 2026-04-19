"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { ChevronDown, Search, X } from "lucide-react";

type Option = { value: string; label: string };

type SearchableSelectProps = {
  label: string;
  value: string;
  options?: Option[];
  onChange: (value: string) => void;
  placeholder?: string;
};

export function SearchableSelect({
  label,
  value,
  options,
  onChange,
  placeholder = "Seleccionar...",
}: SearchableSelectProps) {
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [openUpward, setOpenUpward] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);

  const safeOptions = Array.isArray(options) ? options : [];
  const selected = safeOptions.find((o) => o.value === value) ?? null;
  const filtered = useMemo(() => {
    const term = query.trim().toLowerCase();
    if (!term) return safeOptions;
    return safeOptions.filter((o) => o.label.toLowerCase().includes(term));
  }, [safeOptions, query]);

  useEffect(() => {
    function handleOutside(event: MouseEvent) {
      if (!containerRef.current?.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleOutside);
    return () => document.removeEventListener("mousedown", handleOutside);
  }, []);

  function select(opt: Option) {
    onChange(opt.value);
    setIsOpen(false);
    setQuery("");
  }

  function clear(e: { stopPropagation: () => void }) {
    e.stopPropagation();
    onChange("");
    setIsOpen(false);
    setQuery("");
  }

  return (
    <div className="flex flex-col gap-1.5">
      <span>{label}</span>
      <div ref={containerRef} className="relative">
        <button
          type="button"
          onClick={() => {
            const rect = containerRef.current?.getBoundingClientRect();
            const spaceBelow = window.innerHeight - (rect?.bottom ?? 0);
            setOpenUpward(spaceBelow < 250);
            setIsOpen((prev) => !prev);
          }}
          className="flex w-full items-center gap-2 rounded-2xl border border-[var(--line)] bg-[var(--input)] px-3 py-2 text-left"
        >
          <span className="truncate text-sm text-primary">{selected?.label ?? placeholder}</span>
          <div className="ml-auto flex items-center gap-1">
            {selected ? (
              <span
                role="button"
                tabIndex={0}
                onClick={clear}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") clear(e);
                }}
                aria-label="Limpiar selección"
                className="rounded p-0.5 text-secondary hover:bg-[var(--panel)]"
              >
                <X className="h-4 w-4" />
              </span>
            ) : null}
            <ChevronDown className={`h-4 w-4 text-secondary transition-transform ${isOpen ? "rotate-180" : ""}`} />
          </div>
        </button>

        {isOpen ? (
          <div
            className="absolute left-0 right-0 mt-1 rounded-2xl border border-[var(--line)] bg-[var(--panel)] shadow-xl"
            style={{
              zIndex: 9999,
              top: openUpward ? "auto" : "calc(100% + 4px)",
              bottom: openUpward ? "calc(100% + 4px)" : "auto",
            }}
          >
            <div className="border-b border-[var(--line)] p-2">
              <div className="flex items-center gap-2 rounded-xl border border-[var(--line)] bg-[var(--input)] px-2 py-1.5">
                <Search className="h-4 w-4 text-secondary" />
                <input
                  autoFocus
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Buscar..."
                  className="w-full bg-transparent text-sm text-primary outline-none placeholder:text-secondary"
                />
              </div>
            </div>
            <div className="max-h-56 overflow-auto p-1">
              {filtered.length === 0 ? (
                <div className="px-3 py-2 text-sm text-secondary">Sin opciones.</div>
              ) : (
                filtered.map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => select(opt)}
                    className={`w-full rounded-xl px-3 py-2 text-left text-sm ${
                      value === opt.value ? "bg-primary text-white" : "text-primary hover:bg-[var(--input)]"
                    }`}
                  >
                    {opt.label}
                  </button>
                ))
              )}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
