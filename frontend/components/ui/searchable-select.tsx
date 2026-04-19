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
  const containerRef = useRef<HTMLDivElement | null>(null);
  const searchInputRef = useRef<HTMLInputElement | null>(null);

  const safeOptions = Array.isArray(options) ? options : [];
  const selected = safeOptions.find((option) => option.value === value) ?? null;
  const filtered = useMemo(() => {
    const term = query.trim().toLowerCase();
    if (!term) {
      return safeOptions;
    }
    return safeOptions.filter((option) => option.label.toLowerCase().includes(term));
  }, [safeOptions, query]);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    setQuery("");
    const timer = window.setTimeout(() => {
      searchInputRef.current?.focus();
    }, 0);

    return () => window.clearTimeout(timer);
  }, [isOpen]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    function handleOutsideClick(event: MouseEvent) {
      if (!containerRef.current?.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, []);

  function select(option: Option) {
    onChange(option.value);
    setIsOpen(false);
    setQuery("");
  }

  function clear(event: React.MouseEvent | React.KeyboardEvent) {
    event.stopPropagation();
    onChange("");
    setIsOpen(false);
    setQuery("");
  }

  return (
    <div className="flex flex-col gap-1.5">
      <span className="text-sm font-medium text-primary">{label}</span>
      <div ref={containerRef} className="z-0">
        <button
          type="button"
          onClick={() => setIsOpen((current) => !current)}
          className="flex w-full items-center gap-2 rounded-2xl border border-[var(--line)] bg-[var(--input)] px-3 py-2 text-left"
        >
          <span className="truncate text-sm text-primary">{selected?.label ?? placeholder}</span>
          <div className="ml-auto flex items-center gap-1">
            {selected ? (
              <span
                role="button"
                tabIndex={0}
                onClick={clear}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    clear(event);
                  }
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
          <div className="mt-2 rounded-2xl border border-[var(--line)] bg-[var(--panel)] shadow-xl">
            <div className="border-b border-[var(--line)] p-2">
              <div className="flex items-center gap-2 rounded-xl border border-[var(--line)] bg-[var(--input)] px-2 py-1.5">
                <Search className="h-4 w-4 text-secondary" />
                <input
                  ref={searchInputRef}
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="Buscar..."
                  className="w-full bg-transparent text-sm text-primary outline-none placeholder:text-secondary"
                />
              </div>
            </div>
            <div className="max-h-[240px] overflow-y-auto p-1">
              {filtered.length === 0 ? (
                <div className="px-3 py-2 text-sm text-secondary">Sin opciones.</div>
              ) : (
                filtered.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => select(option)}
                    className={`w-full rounded-xl px-3 py-2 text-left text-sm ${
                      value === option.value ? "bg-primary text-white" : "text-primary hover:bg-[var(--input)]"
                    }`}
                  >
                    {option.label}
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
