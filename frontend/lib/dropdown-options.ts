export type DropdownOption = {
  value: string;
  label: string;
};

function normalizeDropdownText(value: string) {
  return value
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}

export function isPlaceholderDropdownValue(value: string | null | undefined) {
  const normalized = normalizeDropdownText(String(value ?? ""));
  if (!normalized) return true;

  const compact = normalized.replace(/\s+/g, "");
  if (!compact) return true;

  if (/^x+$/.test(compact)) return true;
  if (/^_+$/.test(compact)) return true;
  if (/^\.+$/.test(compact)) return true;
  if (/^-+$/.test(compact)) return true;
  if (/^(?:x|_|\-|\.)+$/.test(compact)) return true;
  if (compact === "na" || compact === "n/a" || compact === "n-a") return true;
  if (compact === "selecciona" || compact === "selecciona..." || compact === "placeholder") return true;

  return false;
}

export function sanitizeDropdownOptions(options: DropdownOption[]) {
  const seen = new Set<string>();

  return (Array.isArray(options) ? options : [])
    .filter((option) => {
      if (!option || typeof option.value !== "string" || typeof option.label !== "string") {
        return false;
      }

      if (isPlaceholderDropdownValue(option.value) || isPlaceholderDropdownValue(option.label)) {
        return false;
      }

      return true;
    })
    .filter((option) => {
      const key = `${option.value}::${option.label}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
}
