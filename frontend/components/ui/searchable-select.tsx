"use client";

import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { ChevronDown, Search } from "lucide-react";

type Option = { value: string; label: string };

export function SearchableSelect({ label, value, options = [], onChange, placeholder = "Buscar..." }: { label: string; value: string; options?: Option[]; onChange: (value: string) => void; placeholder?: string }) {
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [coords, setCoords] = useState<{ top: number; left: number; width: number; height: number } | null>(null);
  const triggerRef = useRef<HTMLDivElement | null>(null);
  const dropdownRef = useRef<HTMLDivElement | null>(null);
  const safeOptions = Array.isArray(options) ? options : [];
  const filtered = useMemo(() => safeOptions.filter((item) => String(item?.label ?? "").toLowerCase().includes(query.toLowerCase())), [safeOptions, query]);

  useLayoutEffect(() => {
    if (!isOpen) {
      return;
    }
    const updatePosition = () => {
      if (triggerRef.current) {
        const rect = triggerRef.current.getBoundingClientRect();
        setCoords({ top: rect.top, left: rect.left, width: rect.width, height: rect.height });
      }
    };
    updatePosition();
    window.addEventListener("resize", updatePosition);
    window.addEventListener("scroll", updatePosition, true);
    return () => {
      window.removeEventListener("resize", updatePosition);
      window.removeEventListener("scroll", updatePosition, true);
    };
  }, [isOpen]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    function handleClickOutside(event: MouseEvent) {
      const target = event.target as Node;
      const clickedTrigger = Boolean(triggerRef.current && triggerRef.current.contains(target));
      const clickedDropdown = Boolean(dropdownRef.current && dropdownRef.current.contains(target));
      if (!clickedTrigger && !clickedDropdown) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const dropdown = isOpen && coords ? (
    <div
      ref={dropdownRef}
      className="rounded-2xl border border-[var(--line)] bg-[var(--panel)] p-2 shadow-lg"
      style={{
        position: "fixed",
        top: coords.top + coords.height + 8,
        left: coords.left,
        width: coords.width,
        zIndex: 9999,
      }}
    >
      <div className="max-h-[200px] space-y-1 overflow-y-auto">
        {filtered.length === 0 ? <div className="rounded-xl px-3 py-2 text-sm text-secondary">Sin opciones.</div> : null}
        {filtered.map((item) => (
          <button
            key={item.value}
            type="button"
            onClick={() => {
              onChange(item.value);
              setQuery(item.label);
              setIsOpen(false);
            }}
            className={`flex w-full items-center justify-between rounded-xl px-3 py-2 text-left text-sm transition ${value === item.value ? "bg-primary text-white" : "hover:bg-[var(--panel)] text-primary"}`}
          >
            <span>{item.label}</span>
          </button>
        ))}
      </div>
    </div>
  ) : null;

  return (
    <div className="grid gap-2 text-sm font-medium text-primary">
      <span>{label}</span>
      <div ref={triggerRef} className="relative overflow-visible ep-card-muted rounded-2xl p-3">
        <div
          role="button"
          tabIndex={0}
          onClick={() => setIsOpen((current) => !current)}
          onKeyDown={(event) => {
            if (event.key === "Enter" || event.key === " ") {
              event.preventDefault();
              setIsOpen((current) => !current);
            }
          }}
          className="flex w-full items-center gap-2 rounded-xl border border-[var(--line)] bg-[var(--input)] px-3 py-2 text-left"
        >
          <Search className="h-4 w-4 text-secondary" />
          <input
            value={query}
            onChange={(event) => {
              setQuery(event.target.value);
              setIsOpen(true);
            }}
            onFocus={() => setIsOpen(true)}
            placeholder={placeholder}
            className="w-full bg-transparent text-sm text-primary outline-none placeholder:text-secondary"
          />
          <ChevronDown className="h-4 w-4 text-secondary" />
        </div>
      </div>
      {dropdown}
    </div>
  );
}
