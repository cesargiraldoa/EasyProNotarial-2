"use client";

export function ValidatedInput({ label, value, onChange, type = "text", placeholder = "", error }: { label: string; value: string; onChange: (value: string) => void; type?: string; placeholder?: string; error?: string | null }) {
  const safeValue = typeof value === "string" ? value : value == null ? "" : String(value);
  return (
    <label className="grid gap-2 text-sm font-medium text-primary">
      <span>{label}</span>
      <input value={safeValue} onChange={(event) => onChange(event.target.value)} type={type} placeholder={placeholder} className={`ep-input h-12 rounded-2xl px-4 ${error ? "border-rose-500/60" : ""}`} />
      {error ? <span className="text-xs text-rose-500">{error}</span> : null}
    </label>
  );
}
