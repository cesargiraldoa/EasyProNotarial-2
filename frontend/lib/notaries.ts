export type NotaryLabelSource = {
  municipality?: string | null;
  city?: string | null;
  notary_label?: string | null;
  commercial_name?: string | null;
};

function cleanPart(value: string | null | undefined): string {
  return (value ?? "").trim();
}

export function formatNotaryOptionLabel(notary: NotaryLabelSource): string {
  const location = cleanPart(notary.municipality) || cleanPart(notary.city);
  const notaryName = cleanPart(notary.notary_label) || cleanPart(notary.commercial_name);

  if (!location && !notaryName) {
    return "Notaría sin nombre";
  }

  if (!location) {
    return notaryName || "Notaría sin nombre";
  }

  if (!notaryName) {
    return `${location} · Notaría sin nombre`;
  }

  return `${location} · ${notaryName}`;
}
