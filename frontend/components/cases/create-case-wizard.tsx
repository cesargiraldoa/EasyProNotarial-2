"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import { ArrowRight, BadgeCheck, CheckCircle2 } from "lucide-react";
import { SearchableSelect } from "@/components/ui/searchable-select";
import { ValidatedInput } from "@/components/ui/validated-input";
import {
  createDocumentCase,
  getActiveTemplates,
  saveCaseActData,
  type DocumentFlowCase,
  type TemplateField,
  type TemplateRecord,
} from "@/lib/document-flow";
import { getEasyPro1CatalogOptions } from "@/lib/easypro1-notarial-catalogs";
import { getCurrentUser, getNotaries, getUserOptions, type UserOption } from "@/lib/api";

const steps = [
  "Plantilla",
  "Datos de la minuta",
  "Diligenciar",
];
const documentTypes = ["CC", "CE", "TI", "PP", "NIT"];
const sexOptions = ["F", "M", "No especifica"];
const nationalityOptions = ["Colombiana", "Extranjera", "Venezolana", "Española"];
const maritalStatusOptions = ["Soltero(a)", "Casado(a)", "Unión marital", "Divorciado(a)", "Viudo(a)"];
const professionSuggestions = ["Abogado", "Comerciante", "Administrador", "Ingeniero", "Contador", "Docente"];

type SelectOption = { value: string; label: string };

const demoData: Record<string, string> = {
  numero_escritura: "2045",
  numero_apartamento: "804",
  numero_matricula: "001-1528731",
  nombre_comprador_1: "JUAN CAMILO VASQUEZ MIRA",
  tipo_documento_comprador_1: "C.C.",
  numero_documento_comprador_1: "1.037.657.164",
  nombre_comprador_2: "MARIA FERNANDA LOPEZ GOMEZ",
  tipo_documento_comprador_2: "C.C.",
  numero_documento_comprador_2: "1.045.234.567",
  valor_de_la_venta_en_numeros: "212.600.000",
  valor_del_acto_de_la_hipoteca: "149.559.520",
  dia_elaboracion_escritura: "veintisiete (27)",
  mes_elaboracion_escritura: "abril",
  comprador_es_hombre_o_mujer: "varón",
  nacionalidad_comprador: "colombiana",
  municipio_domicilio_comprador: "Envigado",
  seleccione_si_comprador_esta_de_transito: "de tránsito por Caldas, Antioquia,",
  estado_civil_comprador: "Soltero sin unión marital de hecho",
  comprador_2_es_hombre_o_mujer: "mujer",
  nacionalidad_comprador_2: "colombiana",
  municipio_domicilio_comprador_2: "Medellín",
  seleccione_si_comprador_2_esta_de_transito: "de tránsito por Caldas, Antioquia,",
  estado_civil_comprador_2: "Soltera sin unión marital de hecho",
  fecha_celebracion_de_la_promesa_compraventa: "quince (15) de enero de dos mil veinticinco (2025)",
  numero_de_piso: "octavo (8°)",
  linderos: "con linderos según reglamento de propiedad horizontal",
  valor_apartamento_en_letras: "DOSCIENTOS DOCE MILLONES SEISCIENTOS MIL PESOS MONEDA CORRIENTE",
  en_letras_cuota_inicial: "SESENTA Y DOS MILLONES SEISCIENTOS MIL PESOS MONEDA CORRIENTE",
  en_numeros_cuota_inicial: "62.600.000",
  origen_cuota_inicial: "recursos propios",
  valor_del_acto_de_la_hipoteca_en_letras: "CIENTO CUARENTA Y NUEVE MILLONES QUINIENTOS CINCUENTA Y NUEVE MIL QUINIENTOS VEINTE PESOS MONEDA CORRIENTE",
  direccion_comprador_1: "Carrera 25 # 39 Sur 15, Apto 1203, Envigado",
  direccion_comprador_2: "Calle 10 # 43 A 22, Apto 502, Medellín",
  celular_comprador_1: "3003575071",
  celular_comprador_2: "3115678901",
  email_comprador_1: "jcamilovasquezm@gmail.com",
  email_comprador_2: "mflopez@gmail.com",
  inmueble_sera_su_casa: "el inmueble que adquiere",
  tiene_inmueble_afectado: "no",
  afectacion_cumple_ley_258: "no",
  queda_afectado: "no",
  nombre_pareja_o_conyuge: "",
  numero_documento_pareja_o_conyuge: "",
  constitucion_patrimonio_de_familia: "y a favor de sus hijos menores",
  acepta_notificacion_electronica: "si",
  coeficiente_copropiedad: "0.0234",
  derechos_notariales: "1.245.000",
  iva: "236.550",
  aporte_superintendencia: "12.450",
  fondo_nacional_notariado: "6.225",
  consecutivo_hojas_papel_notarial: "Aa117159580 al Aa117159595",
  profesion_u_oficio: "Ingeniero",
  actividad_economica_comprador: "Empleado",
  profesion_u_oficio_comprador_2: "Abogada",
  actividad_economica_comprador_2: "Independiente",
  protocolista: "Tatiana",
};

function safeString(value: unknown) {
  return typeof value === "string" ? value : "";
}

function normalizeUserOptions(users: UserOption[]): SelectOption[] {
  return (Array.isArray(users) ? users : []).map((item) => ({
    value: String(item.id ?? ""),
    label: [safeString(item.full_name), safeString(item.email)].filter(Boolean).join(" · ") || "Usuario sin nombre",
  })).filter((item) => item.value);
}

function sortByStepOrder<T extends { step_order?: number | null }>(items: T[]) {
  return [...items].sort((a, b) => Number(a.step_order ?? 0) - Number(b.step_order ?? 0));
}

function buildActDataFromTemplate(template: TemplateRecord | null) {
  const fields = sortByStepOrder(Array.isArray(template?.fields) ? template.fields : []);
  const initialData: Record<string, string> = {};
  const today = new Date();
  const commonValues = {
    dia_elaboracion: String(today.getDate()),
    mes_elaboracion: today.toLocaleDateString("es-CO", { month: "long" }),
    ano_elaboracion: String(today.getFullYear()),
  };

  for (const field of fields) {
    initialData[field.field_code] = "";
  }

  for (const [key, value] of Object.entries(commonValues)) {
    if (key in initialData) {
      initialData[key] = value;
    }
  }

  return initialData;
}

function parseTemplateFieldOptions(optionsJson: string | null | undefined): SelectOption[] {
  if (!optionsJson) {
    return [];
  }

  try {
    const parsed = JSON.parse(optionsJson);
    if (!Array.isArray(parsed)) {
      return [];
    }

    return parsed
      .map((item, index) => {
        if (typeof item === "string") {
          return { value: item, label: item };
        }
        if (item && typeof item === "object") {
          const rawValue = safeString((item as { value?: unknown; label?: unknown }).value);
          const rawLabel = safeString((item as { value?: unknown; label?: unknown }).label);
          const value = rawValue || rawLabel;
          const label = rawLabel || rawValue || `Opción ${index + 1}`;
          if (value || label) {
            return { value, label };
          }
        }
        return null;
      })
      .filter((item): item is SelectOption => Boolean(item?.value));
  } catch {
    return [];
  }
}

function normalizeCatalogText(value: string) {
  return value
    .trim()
    .toUpperCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^A-Z0-9]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function matchesAnyCatalogSource(sources: string[], patterns: string[]) {
  return patterns.some((pattern) => sources.some((source) => source.includes(pattern)));
}

function inferEasyPro1CatalogName(field: TemplateField): string | null {
  const sources = [field.table_master, field.field_code, field.label, field.section]
    .map((value) => normalizeCatalogText(safeString(value)))
    .filter(Boolean);

  const rules: Array<{ catalog: string; patterns: string[] }> = [
    { catalog: "TIPO DE DOCUMENTO", patterns: ["TIPO DE DOCUMENTO", "TIPO DOCUMENTO"] },
    { catalog: "ESTADO CIVIL", patterns: ["ESTADO CIVIL"] },
    { catalog: "NACIONALIDAD", patterns: ["NACIONALIDAD"] },
    { catalog: "SEXO", patterns: ["SEXO"] },
    { catalog: "GENERO", patterns: ["GENERO", "HOMBRE O MUJER"] },
    { catalog: "DE TRANSITO", patterns: ["DE TRANSITO", "TRANSITO", "ESTA DE TRANSITO"] },
    { catalog: "SI O NO", patterns: ["SI O NO", "SELECCIONE SI", "ACEPTA", "TIENE INMUEBLE", "TIENE OTRO BIEN", "CUMPLE", "QUEDA AFECTADO", "AFECTACION", "INMUEBLE SERA SU CASA", "CASA DE HABITACION", "NOTIFICACION ELECTRONICA"] },
    { catalog: "MES", patterns: ["MES"] },
    { catalog: "DÍAS", patterns: ["DIA", "DIAS"] },
    { catalog: "CUOTA INICIAL", patterns: ["CUOTA INICIAL", "ORIGEN CUOTA"] },
    { catalog: "PATRIMONIO DE FAMILIA", patterns: ["PATRIMONIO DE FAMILIA", "PATRIMONIO"] },
    { catalog: "PROTOCOLISTA", patterns: ["PROTOCOLISTA"] },
    { catalog: "MUNICIPIO", patterns: ["MUNICIPIO"] },
    { catalog: "PAIS", patterns: ["PAIS"] },
    { catalog: "PADRES", patterns: ["PADRES", "PADRE O MADRE"] },
    { catalog: "NOTARIO", patterns: ["NOTARIO"] },
  ];

  for (const rule of rules) {
    if (matchesAnyCatalogSource(sources, rule.patterns)) {
      return rule.catalog;
    }
  }

  return null;
}

function resolveCatalogOptions(field: TemplateField): SelectOption[] {
  const explicitOptions = parseTemplateFieldOptions(field.options_json);
  if (explicitOptions.length > 0) {
    return explicitOptions;
  }

  const inferredCatalogName = field.table_master || inferEasyPro1CatalogName(field);
  if (!inferredCatalogName) {
    return [];
  }

  return getEasyPro1CatalogOptions(inferredCatalogName);
}

function normalizeSelectValue(value: string) {
  return normalizeCatalogText(value);
}

function resolveDemoSelectValue(targetValue: string, options: SelectOption[]) {
  if (!options.length) {
    return "";
  }

  const normalizedTarget = normalizeSelectValue(targetValue);
  if (!normalizedTarget) {
    return options[0]?.value ?? "";
  }

  const exactMatch = options.find((option) => normalizeSelectValue(option.value) === normalizedTarget || normalizeSelectValue(option.label) === normalizedTarget);
  if (exactMatch) {
    return exactMatch.value;
  }

  const includesMatch = options.find((option) => {
    const optionValue = normalizeSelectValue(option.value);
    const optionLabel = normalizeSelectValue(option.label);
    return optionValue.includes(normalizedTarget) || optionLabel.includes(normalizedTarget) || normalizedTarget.includes(optionValue) || normalizedTarget.includes(optionLabel);
  });
  return includesMatch?.value ?? options[0]?.value ?? "";
}

function normalizeMoneyFieldCode(value: string) {
  return safeString(value)
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/_+/g, "_")
    .replace(/^_+|_+$/g, "");
}

function toMasculineSpanishWords(value: string) {
  return value
    .replace(/\bVEINTIUNO\b/g, "VEINTIUN")
    .replace(/\bUNO\b/g, "UN");
}

function convertUnderThousandToSpanish(value: number) {
  const units = [
    "",
    "UNO",
    "DOS",
    "TRES",
    "CUATRO",
    "CINCO",
    "SEIS",
    "SIETE",
    "OCHO",
    "NUEVE",
  ];
  const teens = [
    "DIEZ",
    "ONCE",
    "DOCE",
    "TRECE",
    "CATORCE",
    "QUINCE",
    "DIECISEIS",
    "DIECISIETE",
    "DIECIOCHO",
    "DIECINUEVE",
  ];
  const tens = [
    "",
    "",
    "VEINTE",
    "TREINTA",
    "CUARENTA",
    "CINCUENTA",
    "SESENTA",
    "SETENTA",
    "OCHENTA",
    "NOVENTA",
  ];
  const hundreds = [
    "",
    "CIENTO",
    "DOSCIENTOS",
    "TRESCIENTOS",
    "CUATROCIENTOS",
    "QUINIENTOS",
    "SEISCIENTOS",
    "SETECIENTOS",
    "OCHOCIENTOS",
    "NOVECIENTOS",
  ];

  if (value === 0) {
    return "";
  }
  if (value === 100) {
    return "CIEN";
  }

  const parts: string[] = [];
  const hundredPart = Math.floor(value / 100);
  const remainder = value % 100;

  if (hundredPart > 0) {
    parts.push(hundreds[hundredPart] ?? "");
  }

  if (remainder > 0) {
    if (remainder < 10) {
      parts.push(units[remainder] ?? "");
    } else if (remainder < 20) {
      parts.push(teens[remainder - 10] ?? "");
    } else if (remainder < 30) {
      if (remainder === 20) {
        parts.push("VEINTE");
      } else {
        const unitWord = units[remainder % 10] ?? "";
        parts.push(`VEINTI${unitWord.toLowerCase()}`.toUpperCase());
      }
    } else {
      const tenPart = Math.floor(remainder / 10);
      const unitPart = remainder % 10;
      const tenWord = tens[tenPart] ?? "";
      if (unitPart === 0) {
        parts.push(tenWord);
      } else {
        parts.push(`${tenWord} Y ${units[unitPart] ?? ""}`);
      }
    }
  }

  return parts.filter(Boolean).join(" ").trim();
}

function numberToColombianPesosWords(value: string): string {
  const cleaned = safeString(value).replace(/[$\s.,]/g, "");
  if (!cleaned || !/^\d+$/.test(cleaned)) {
    return "";
  }

  const normalizedDigits = cleaned.replace(/^0+(?=\d)/, "");
  if (normalizedDigits === "0") {
    return "CERO PESOS MONEDA CORRIENTE";
  }

  const groups: string[] = [];
  for (let index = normalizedDigits.length; index > 0; index -= 3) {
    groups.unshift(normalizedDigits.slice(Math.max(0, index - 3), index));
  }

  const scaleNames = [
    { singular: "", plural: "" },
    { singular: "MIL", plural: "MIL" },
    { singular: "MILLON", plural: "MILLONES" },
    { singular: "MIL MILLONES", plural: "MIL MILLONES" },
    { singular: "BILLON", plural: "BILLONES" },
    { singular: "MIL BILLONES", plural: "MIL BILLONES" },
    { singular: "TRILLON", plural: "TRILLONES" },
  ];

  const words = groups
    .map((group, index) => {
      const groupValue = Number(group);
      if (!groupValue) {
        return "";
      }

      const scaleIndex = groups.length - index - 1;
      const scale = scaleNames[scaleIndex];
      const baseWords = convertUnderThousandToSpanish(groupValue);

      if (scaleIndex === 0) {
        return toMasculineSpanishWords(baseWords);
      }

      if (scaleIndex === 1 || scaleIndex === 3 || scaleIndex === 5) {
        if (groupValue === 1) {
          return scale?.singular ?? "";
        }
        return `${toMasculineSpanishWords(baseWords)} ${scale?.singular ?? ""}`.trim();
      }

      if (groupValue === 1) {
        return `UN ${scale?.singular ?? ""}`.trim();
      }

      return `${toMasculineSpanishWords(baseWords)} ${scale?.plural ?? ""}`.trim();
    })
    .filter(Boolean)
    .join(" ")
    .trim();

  if (!words) {
    return "";
  }

  return `${words} PESOS MONEDA CORRIENTE`.toUpperCase();
}

function resolveDerivedMoneyField(fieldCode: string, allFieldCodes: string[]): string | null {
  const normalizedFieldCode = normalizeMoneyFieldCode(fieldCode);
  if (!normalizedFieldCode) {
    return null;
  }

  const normalizedFieldMap = new Map<string, string>();
  for (const code of allFieldCodes) {
    const normalizedCode = normalizeMoneyFieldCode(code);
    if (normalizedCode && !normalizedFieldMap.has(normalizedCode)) {
      normalizedFieldMap.set(normalizedCode, code);
    }
  }

  const explicitMappings: Record<string, string[]> = {
    valor_apartamento_en_letras: ["valor_de_la_venta_en_numeros", "en_numeros_valor_de_la_venta"],
    en_letras_valor_de_la_venta: ["en_numeros_valor_de_la_venta", "valor_de_la_venta_en_numeros"],
    valor_del_acto_de_la_hipoteca_en_letras: ["valor_del_acto_de_la_hipoteca", "numeros_valor_hipoteca"],
    letras_valor_hipoteca: ["numeros_valor_hipoteca", "valor_del_acto_de_la_hipoteca"],
    cuota_inicial_en_letras: ["cuota_inicial_en_numeros", "en_numeros_cuota_inicial"],
    en_letras_cuota_inicial: ["en_numeros_cuota_inicial", "cuota_inicial_en_numeros"],
    valor_del_credito_en_letras: ["valor_del_credito_en_numeros"],
  };

  const explicitSources = explicitMappings[normalizedFieldCode];
  if (Array.isArray(explicitSources)) {
    for (const sourceCode of explicitSources) {
      const actualSourceCode = normalizedFieldMap.get(sourceCode);
      if (actualSourceCode) {
        return actualSourceCode;
      }
    }
  }

  if (!normalizedFieldCode.includes("letras")) {
    return null;
  }

  const genericCandidates = [
    normalizedFieldCode.replace(/_en_letras\b/g, "_en_numeros"),
    normalizedFieldCode.replace(/\ben_letras\b/g, "en_numeros"),
    normalizedFieldCode.replace(/letras\b/g, "numeros"),
  ];

  for (const candidate of genericCandidates) {
    const actualCandidate = normalizedFieldMap.get(candidate);
    if (actualCandidate) {
      return actualCandidate;
    }
  }

  return null;
}

function hydrateDerivedMoneyFields(
  data: Record<string, string>,
  fields: Array<{ field_code: string }>,
) {
  const fieldCodes = fields.map((field) => field.field_code);
  if (fieldCodes.length === 0) {
    return data;
  }

  let nextData = data;
  for (const derivedFieldCode of fieldCodes) {
    const sourceFieldCode = resolveDerivedMoneyField(derivedFieldCode, fieldCodes);
    if (!sourceFieldCode) {
      continue;
    }

    const derivedValue = numberToColombianPesosWords(nextData[sourceFieldCode] ?? "");
    if ((nextData[derivedFieldCode] ?? "") === derivedValue) {
      continue;
    }

    if (nextData === data) {
      nextData = { ...data };
    }
    nextData[derivedFieldCode] = derivedValue;
  }

  return nextData;
}

export function CreateCaseWizard() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [templates, setTemplates] = useState<TemplateRecord[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateRecord | null>(null);
  const [templateSearch, setTemplateSearch] = useState("");
  const [templateTypeFilter, setTemplateTypeFilter] = useState("all");
  const [notaries, setNotaries] = useState<SelectOption[]>([]);
  const [users, setUsers] = useState<UserOption[]>([]);
  const [caseDetail, setCaseDetail] = useState<DocumentFlowCase | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [canSelectNotary, setCanSelectNotary] = useState(true);
  const [showSubstituteNotary, setShowSubstituteNotary] = useState(false);
  const [expandedGeneralField, setExpandedGeneralField] = useState<string | null>(null);
  const [generalForm, setGeneralForm] = useState({
    notary_id: "",
    client_user_id: "",
    current_owner_user_id: "",
    protocolist_user_id: "",
    approver_user_id: "",
    titular_notary_user_id: "",
    substitute_notary_user_id: "",
    requires_client_review: true,
    metadata_json: JSON.stringify({ clase: "Poder General" }, null, 2),
  });
  const [actData, setActData] = useState<Record<string, string>>({});
  const actDataRef = useRef<Record<string, string>>({});
  const demoFillRunIdRef = useRef(0);
  const demoFillTimeoutsRef = useRef<number[]>([]);
  const demoFillRunningRef = useRef(false);
  const demoFillStartedTemplateIdRef = useRef<number | null>(null);
  const actDataReadyRef = useRef(false);

  useEffect(() => {
    void load();
  }, []);

  useEffect(() => {
    actDataReadyRef.current = false;
    setActData(buildActDataFromTemplate(selectedTemplate));
  }, [selectedTemplate]);

  const templateFields = useMemo(() => sortByStepOrder(Array.isArray(selectedTemplate?.fields) ? selectedTemplate.fields : []), [selectedTemplate]);
  const templateFieldCodes = useMemo(() => templateFields.map((field) => field.field_code), [templateFields]);

  useEffect(() => {
    if (!selectedTemplate || templateFieldCodes.length === 0) {
      return;
    }

    setActData((current) => hydrateDerivedMoneyFields(current, templateFields));
  }, [selectedTemplate, templateFields, templateFieldCodes]);

  useEffect(() => {
    if (!selectedTemplate) {
      actDataReadyRef.current = false;
      return;
    }
    const templateFields = Array.isArray(selectedTemplate.fields) ? selectedTemplate.fields : [];
    actDataReadyRef.current = templateFields.every((field) => field.field_code in actData);
    actDataRef.current = actData;
  }, [actData, selectedTemplate]);

  function cancelDemoFill(resetStarted = false) {
    demoFillRunIdRef.current += 1;
    demoFillRunningRef.current = false;
    if (resetStarted) {
      demoFillStartedTemplateIdRef.current = null;
    }
    for (const timeoutId of demoFillTimeoutsRef.current) {
      window.clearTimeout(timeoutId);
    }
    demoFillTimeoutsRef.current = [];
  }

  function updateActField(fieldCode: string, value: string, source: "user" | "demo" = "user") {
    if (source === "user") {
      cancelDemoFill();
    }
    setActData((current) => {
      const nextData = { ...current, [fieldCode]: value };
      const normalizedFieldCode = normalizeMoneyFieldCode(fieldCode);

      if (templateFieldCodes.length > 0 && normalizedFieldCode) {
        for (const targetFieldCode of templateFieldCodes) {
          const sourceFieldCode = resolveDerivedMoneyField(targetFieldCode, templateFieldCodes);
          if (!sourceFieldCode || normalizeMoneyFieldCode(sourceFieldCode) !== normalizedFieldCode) {
            continue;
          }

          nextData[targetFieldCode] = numberToColombianPesosWords(nextData[sourceFieldCode] ?? "");
        }
      }

      return nextData;
    });
  }

  function autoFillDemo() {
    if (step !== 2 || !selectedTemplate) {
      return;
    }
    if (demoFillRunningRef.current) {
      return;
    }
    if (demoFillStartedTemplateIdRef.current === selectedTemplate.id) {
      return;
    }
    if (!actDataReadyRef.current) {
      return;
    }

    const currentActData = actDataRef.current;
    const templateFields = Array.isArray(selectedTemplate.fields) ? selectedTemplate.fields : [];
    const hasCurrentTemplateData = templateFields.every((field) => field.field_code in currentActData);
    if (!hasCurrentTemplateData) {
      return;
    }

    const templateFieldCodes = templateFields.map((field) => field.field_code);
    const demoKeys = Object.keys(demoData);
    const fieldCodes = Object.keys(demoData).filter((key) => key in currentActData);
    if (fieldCodes.length === 0) {
      return;
    }

    cancelDemoFill();
    demoFillRunningRef.current = true;
    demoFillStartedTemplateIdRef.current = selectedTemplate.id;
    const runId = demoFillRunIdRef.current;

    const scheduleField = (fieldIndex: number) => {
      if (runId !== demoFillRunIdRef.current) {
        return;
      }
      if (fieldIndex >= fieldCodes.length) {
        return;
      }

      const fieldCode = fieldCodes[fieldIndex];
      const field = templateFields.find((item) => item.field_code === fieldCode) ?? null;
      const options = field ? resolveCatalogOptions(field) : [];
      const targetValue = demoData[fieldCode] ?? "";
      const scheduleNextField = () => {
        if (runId !== demoFillRunIdRef.current) {
          return;
        }
        if (fieldIndex + 1 >= fieldCodes.length) {
          demoFillRunningRef.current = false;
          return;
        }
        const nextFieldTimer = window.setTimeout(() => scheduleField(fieldIndex + 1), 80);
        demoFillTimeoutsRef.current.push(nextFieldTimer);
      };

      if (options.length > 0) {
        const selectedValue = resolveDemoSelectValue(targetValue, options);
        if (selectedValue) {
          updateActField(fieldCode, selectedValue, "demo");
        }
        scheduleNextField();
        return;
      }

      let typedValue = "";
      let charIndex = 0;

      const typeNextChar = () => {
        if (runId !== demoFillRunIdRef.current) {
          return;
        }
        if (charIndex >= targetValue.length) {
          scheduleNextField();
          return;
        }

        typedValue += targetValue[charIndex] ?? "";
        charIndex += 1;
        updateActField(fieldCode, typedValue, "demo");
        const charTimer = window.setTimeout(typeNextChar, 18);
        demoFillTimeoutsRef.current.push(charTimer);
      };

      if (!targetValue) {
        scheduleNextField();
        return;
      }

      const firstCharTimer = window.setTimeout(typeNextChar, 18);
      demoFillTimeoutsRef.current.push(firstCharTimer);
    };

    scheduleField(0);
  }

  useEffect(() => {
    if (step !== 2) {
      cancelDemoFill(true);
      return;
    }

    void autoFillDemo();
    return () => cancelDemoFill();
  }, [step, selectedTemplate]);

  async function load() {
    setIsLoading(true);
    setError(null);
    try {
      const [templateData, notaryData, userData, currentUser] = await Promise.all([
        getActiveTemplates(),
        getNotaries(),
        getUserOptions(true),
        getCurrentUser(),
      ]);
      const safeTemplates = Array.isArray(templateData) ? templateData : [];
      const safeNotaries = Array.isArray(notaryData) ? notaryData : [];
      const safeUsers = Array.isArray(userData) ? userData : [];
      const notaryOptions = safeNotaries
        .map((item) => ({
          value: String(item.id ?? ""),
          label: [safeString(item.notary_label), safeString(item.municipality)].filter(Boolean).join(" · ") || "Notaría sin nombre",
        }))
        .filter((item) => item.value);
      const isSuperAdmin = Array.isArray(currentUser?.role_codes) && currentUser.role_codes.includes("super_admin");
      const defaultNotaryRaw = currentUser?.default_notary_id;
      const defaultNotaryId = String(defaultNotaryRaw ?? "");
      setTemplates(safeTemplates);
      setSelectedTemplate(
        safeTemplates[0] ?? null,
      );
      setNotaries(notaryOptions);
      setCanSelectNotary(isSuperAdmin);
      setGeneralForm((current) => ({
        ...current,
        notary_id: !isSuperAdmin ? defaultNotaryId : current.notary_id,
        client_user_id: current.client_user_id,
        current_owner_user_id: "",
        protocolist_user_id: "",
        approver_user_id: "",
        titular_notary_user_id: "",
        substitute_notary_user_id: "",
      }));
      setUsers(safeUsers);
    } catch (loadError) {
      setTemplates([]);
      setSelectedTemplate(null);
      setNotaries([]);
      setUsers([]);
      setError(loadError instanceof Error ? loadError.message : "No fue posible cargar la base del wizard.");
    } finally {
      setIsLoading(false);
    }
  }

  const userOptions = useMemo(() => normalizeUserOptions(users), [users]);
  const normalizedTemplateSearch = templateSearch.trim().toLowerCase();
  const templateTypeOptions = useMemo(() => {
    const seen = new Set<string>();
    const options: Array<{ value: string; label: string }> = [];

    for (const template of templates) {
      const typeLabel = safeString(template.document_type).trim() || "Sin tipo definido";
      if (seen.has(typeLabel)) {
        continue;
      }
      seen.add(typeLabel);
      options.push({
        value: typeLabel,
        label: typeLabel,
      });
    }

    return options;
  }, [templates]);
  const filteredTemplates = useMemo(() => {
    const query = normalizedTemplateSearch;

    return templates.filter((template) => {
      const typeLabel = safeString(template.document_type).trim() || "Sin tipo definido";
      const matchesType = templateTypeFilter === "all" || typeLabel === templateTypeFilter;
      if (!matchesType) {
        return false;
      }

      if (!query) {
        return true;
      }

      const searchableValues = [
        template.name,
        template.document_type,
        template.description,
        template.slug,
        template.source_filename,
      ]
        .map((value) => safeString(value).toLowerCase())
        .join(" ");

      const normalizedSearchableValues = searchableValues.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
      return normalizedSearchableValues.includes(query.normalize("NFD").replace(/[\u0300-\u036f]/g, ""));
    });
  }, [normalizedTemplateSearch, templateTypeFilter, templates]);
  const selectedTemplateMatchesFilter = Boolean(
    selectedTemplate && filteredTemplates.some((template) => template.id === selectedTemplate.id),
  );
  const selectedNotaryLabel = useMemo(() => {
    if (!generalForm.notary_id) {
      return "Notaría asignada";
    }

    return notaries.find((item) => item.value === generalForm.notary_id)?.label || "Notaría asignada";
  }, [generalForm.notary_id, notaries]);
  const generalManagerFields = useMemo<Array<{ key: "current_owner_user_id" | "protocolist_user_id" | "approver_user_id" | "titular_notary_user_id"; label: string; value: string }>>(() => [
    { key: "current_owner_user_id", label: "Responsable actual", value: generalForm.current_owner_user_id },
    { key: "protocolist_user_id", label: "Protocolista", value: generalForm.protocolist_user_id },
    { key: "approver_user_id", label: "Aprobador", value: generalForm.approver_user_id },
    { key: "titular_notary_user_id", label: "Notario titular", value: generalForm.titular_notary_user_id },
  ], [generalForm.current_owner_user_id, generalForm.protocolist_user_id, generalForm.approver_user_id, generalForm.titular_notary_user_id]);

  function renderTemplateSummary() {
    if (!selectedTemplate) {
      return (
        <div className="ep-card-soft rounded-[1.5rem] p-5">
          <p className="text-sm font-semibold text-primary">Plantilla seleccionada</p>
          <p className="mt-2 text-sm text-secondary">Selecciona una plantilla para ver aquí el resumen destacado antes de continuar.</p>
        </div>
      );
    }

    return (
      <div className="rounded-[1.75rem] border-2 border-primary/30 bg-gradient-to-br from-primary/10 via-[var(--panel)] to-[var(--panel-soft)] p-5 shadow-[0_18px_40px_rgba(15,23,42,0.08)]">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="space-y-3">
            <div className="inline-flex items-center gap-2 rounded-full bg-primary px-3 py-1 text-xs font-semibold text-white">
              <BadgeCheck className="h-4 w-4" />
              Seleccionada
            </div>
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-secondary">Plantilla seleccionada</p>
              <h3 className="mt-2 text-xl font-semibold text-primary">{selectedTemplate.name}</h3>
            </div>
            <p className="max-w-3xl text-sm leading-6 text-secondary">
              Esta plantilla define el formulario dinámico que diligenciarás en el siguiente paso.
            </p>
          </div>
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-white/80 px-4 py-2 text-sm font-semibold text-primary">
            <CheckCircle2 className="h-4 w-4" />
            Plantilla seleccionada
          </div>
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-[1.1rem] border border-[var(--line)] bg-[var(--panel)] px-4 py-3">
            <p className="text-xs uppercase tracking-[0.18em] text-secondary">Minuta</p>
            <p className="mt-2 text-sm font-semibold text-primary">{selectedTemplate.name}</p>
          </div>
          <div className="rounded-[1.1rem] border border-[var(--line)] bg-[var(--panel)] px-4 py-3">
            <p className="text-xs uppercase tracking-[0.18em] text-secondary">Tipo de minuta</p>
            <p className="mt-2 text-sm font-semibold text-primary">{selectedTemplate.document_type ?? "Sin definir"}</p>
          </div>
          <div className="rounded-[1.1rem] border border-[var(--line)] bg-[var(--panel)] px-4 py-3">
            <p className="text-xs uppercase tracking-[0.18em] text-secondary">Campos detectados</p>
            <p className="mt-2 text-sm font-semibold text-primary">{selectedTemplate.fields?.length ?? 0} campos configurados</p>
          </div>
          <div className="rounded-[1.1rem] border border-[var(--line)] bg-[var(--panel)] px-4 py-3">
            <p className="text-xs uppercase tracking-[0.18em] text-secondary">Intervinientes</p>
            <p className="mt-2 text-sm font-semibold text-primary">{selectedTemplate.required_roles?.length ?? 0} roles requeridos</p>
          </div>
        </div>
      </div>
    );
  }

  function updateGeneralManager(field: "current_owner_user_id" | "protocolist_user_id" | "approver_user_id" | "titular_notary_user_id", value: string) {
    setGeneralForm((current) => ({ ...current, [field]: value }));
    setExpandedGeneralField(null);
  }

  function clearTemplateFilters() {
    setTemplateSearch("");
    setTemplateTypeFilter("all");
  }

  async function handleCreateCase() {
    if (!selectedTemplate || !generalForm.notary_id) {
      throw new Error("Debes seleccionar la notaría y la plantilla para crear la minuta.");
    }
    const created = await createDocumentCase({
      template_id: selectedTemplate.id,
      notary_id: Number(generalForm.notary_id),
      client_user_id: generalForm.client_user_id ? Number(generalForm.client_user_id) : null,
      current_owner_user_id: generalForm.current_owner_user_id ? Number(generalForm.current_owner_user_id) : null,
      protocolist_user_id: generalForm.protocolist_user_id ? Number(generalForm.protocolist_user_id) : null,
      approver_user_id: generalForm.approver_user_id ? Number(generalForm.approver_user_id) : null,
      titular_notary_user_id: generalForm.titular_notary_user_id ? Number(generalForm.titular_notary_user_id) : null,
      substitute_notary_user_id: generalForm.substitute_notary_user_id ? Number(generalForm.substitute_notary_user_id) : null,
      requires_client_review: generalForm.requires_client_review,
      metadata_json: generalForm.metadata_json,
    });
    setCaseDetail(created);
    return created;
  }

  async function handlePrimaryAction() {
    setError(null);
    setFeedback(null);
    setIsSaving(true);
    try {
      if (step === 0) {
        if (!selectedTemplate) {
          throw new Error("Selecciona una plantilla antes de continuar.");
        }
        setStep((current) => Math.min(current + 1, steps.length - 1));
        return;
      }
      if (step === 1) {
        await handleCreateCase();
        setStep((current) => Math.min(current + 1, steps.length - 1));
        return;
      }
      if (step === 2) {
        if (!caseDetail) {
          throw new Error("Primero debes crear la minuta para guardar y generar el Word.");
        }
        const updated = await saveCaseActData(caseDetail.id, { data_json: JSON.stringify(actData) });
        setCaseDetail(updated);
        const base = process.env.NEXT_PUBLIC_API_URL ?? "";
        const token = typeof window !== "undefined" ? localStorage.getItem("easypro2_session") : null;
        const response = await fetch(`${base}/api/v1/document-flow/cases/${caseDetail.id}/generate-from-template`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({ act_data: actData }),
        });
        if (!response.ok) {
          const text = await response.text();
          throw new Error(text);
        }
        setFeedback("Minuta guardada y Word generado. Abriendo detalle de la minuta...");
        router.replace(`/dashboard/casos/${caseDetail.id}`);
        return;
      }
    } catch (stepError) {
      setError(stepError instanceof Error ? stepError.message : "No fue posible avanzar en el wizard.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="space-y-6">
      <section className="ep-card z-0 rounded-[2rem] p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-accent">
              {caseDetail?.internal_case_number ? `Minuta · ${caseDetail.internal_case_number}` : "Minuta"}
            </p>
            <h1 className="mt-3 text-3xl font-semibold tracking-[-0.05em] text-primary">Crear minuta desde plantilla Word</h1>
            <p className="mt-3 max-w-3xl text-base leading-7 text-secondary">
              Escoge una plantilla, completa los datos de la minuta, diligencia el formulario dinámico y guarda para generar el Word sin salir de este flujo.
            </p>
          </div>
          {caseDetail ? (
            <Link href={`/dashboard/casos/${caseDetail.id}`} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white">
              Abrir detalle de la minuta <ArrowRight className="h-4 w-4" />
            </Link>
          ) : null}
        </div>
      </section>

      <section className="ep-card z-0 rounded-[2rem] p-6">
        <div className="grid gap-3 xl:grid-cols-4">
          {steps.map((item, index) => (
            <div key={item} className={`rounded-[1.35rem] border px-4 py-4 ${index === step ? "border-primary/30 bg-primary text-white" : index < step ? "border-emerald-500/20 bg-emerald-500/10" : "border-[var(--line)] bg-[var(--panel-soft)]"}`}>
              <div className="flex items-center gap-3">
                <div className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold ${index === step ? "bg-white/15 text-white" : index < step ? "bg-emerald-500/20 text-primary" : "bg-[var(--panel)] text-primary"}`}>
                  {index < step ? <CheckCircle2 className="h-4 w-4" /> : index + 1}
                </div>
                <p className={`text-sm font-semibold ${index === step ? "text-white" : "text-primary"}`}>{item}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="space-y-6">
        <div className="ep-card z-0 rounded-[2rem] p-6 space-y-6">
          <div className="ep-card-muted rounded-[1.5rem] px-4 py-4 text-sm text-secondary">
            La plantilla seleccionada define los campos visibles. Si cambias de plantilla, el formulario cambia con ella.
          </div>
          {isLoading ? <div className="ep-card-muted z-0 rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Cargando plantillas, notarías y usuarios...</div> : null}
          {!isLoading && error && templates.length === 0 ? <div className="ep-kpi-critical z-0 rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
          {!isLoading && !error && templates.length === 0 ? <div className="ep-card-muted z-0 rounded-[1.5rem] px-4 py-6 text-sm text-secondary">No hay plantillas activas todavía.</div> : null}

          {!isLoading && templates.length > 0 ? (
            <>
              {step === 0 ? (
                <div className="space-y-6">
                  <h2 className="text-2xl font-semibold text-primary">1. Seleccionar plantilla</h2>
                  <div className="rounded-[1.75rem] border border-[var(--line)] bg-[var(--panel-soft)] p-4 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
                    <div className="flex flex-col gap-4">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-secondary">Buscar y filtrar plantillas</p>
                          <p className="mt-2 text-sm text-secondary">
                            Filtra por nombre, tipo de minuta, descripción y archivos relacionados.
                          </p>
                        </div>
                      </div>
                      <div className="grid gap-4 lg:grid-cols-[minmax(0,1.7fr)_minmax(240px,0.9fr)_auto] lg:items-end">
                        <label className="grid gap-2 text-sm font-medium text-primary">
                          <span>Buscar plantilla</span>
                          <input
                            type="search"
                            value={templateSearch}
                            onChange={(event) => setTemplateSearch(event.target.value)}
                            placeholder="Buscar por nombre, tipo de minuta o descripción..."
                            className="ep-input h-12 rounded-2xl px-4"
                          />
                        </label>
                        <label className="grid gap-2 text-sm font-medium text-primary">
                          <span>Tipo de minuta</span>
                          <select
                            value={templateTypeFilter}
                            onChange={(event) => setTemplateTypeFilter(event.target.value)}
                            className="ep-input h-12 rounded-2xl px-4"
                          >
                            <option value="all">Todos</option>
                            {templateTypeOptions.map((option) => (
                              <option key={option.value} value={option.value}>
                                {option.label}
                              </option>
                            ))}
                          </select>
                        </label>
                        <button
                          type="button"
                          onClick={clearTemplateFilters}
                          className="inline-flex h-12 items-center justify-center gap-2 rounded-2xl border border-[var(--line)] bg-white px-4 text-sm font-semibold text-primary transition-colors hover:border-primary/30 hover:text-primary lg:mt-auto"
                        >
                          Limpiar búsqueda
                        </button>
                      </div>
                      <div className="flex flex-col gap-2 border-t border-[var(--line)] pt-4 sm:flex-row sm:items-center sm:justify-between">
                        <p className="text-sm font-medium text-secondary">
                          Mostrando {filteredTemplates.length} de {templates.length} plantillas disponibles
                        </p>
                      </div>
                    </div>
                  </div>
                  {renderTemplateSummary()}
                  {filteredTemplates.length > 0 ? (
                    <div className="grid gap-4 lg:grid-cols-2">
                      {filteredTemplates.map((item) => (
                        <button
                          key={item.id}
                          type="button"
                          onClick={() => setSelectedTemplate(item)}
                          aria-pressed={selectedTemplate?.id === item.id}
                          className={`relative overflow-hidden rounded-[1.5rem] border p-5 text-left transition-all ${
                            selectedTemplate?.id === item.id
                              ? "border-2 border-primary/70 bg-gradient-to-br from-primary/10 via-white to-[var(--panel-soft)] shadow-[0_18px_40px_rgba(15,23,42,0.1)] ring-2 ring-primary/10"
                              : "border-[var(--line)] bg-[var(--panel-soft)] hover:border-primary/25 hover:bg-[var(--panel)]"
                          }`}
                        >
                          {selectedTemplate?.id === item.id ? (
                            <div className="absolute right-4 top-4 inline-flex items-center gap-1 rounded-full bg-primary px-3 py-1 text-xs font-semibold text-white shadow-sm">
                              <CheckCircle2 className="h-4 w-4" />
                              Seleccionada
                            </div>
                          ) : null}
                          <div className="flex items-start gap-3 pr-24">
                            <div className={`flex h-10 w-10 flex-none items-center justify-center rounded-2xl ${selectedTemplate?.id === item.id ? "bg-primary text-white" : "bg-white text-primary ring-1 ring-[var(--line)]"}`}>
                              <CheckCircle2 className="h-5 w-5" />
                            </div>
                            <div className="min-w-0">
                              <p className="text-lg font-semibold text-primary">{item.name}</p>
                              <p className="mt-1 text-sm text-secondary">Tipo de minuta: {item.document_type || "Sin tipo definido"}</p>
                            </div>
                          </div>
                          {item.description && (
                            <p className="mt-2 text-xs text-secondary">{item.description}</p>
                          )}
                          <p className="mt-3 text-xs text-secondary">
                            Campos detectados: {item.fields?.length ?? 0} · Intervinientes: {item.required_roles?.length ?? 0}
                          </p>
                          <p className={`mt-4 text-xs font-semibold uppercase tracking-[0.18em] ${selectedTemplate?.id === item.id ? "text-primary" : "text-secondary"}`}>
                            {selectedTemplate?.id === item.id ? "Plantilla seleccionada" : "Usar esta plantilla"}
                          </p>
                        </button>
                      ))}
                    </div>
                  ) : (
                    <div className="ep-card-soft rounded-[1.5rem] px-5 py-8 text-center">
                      <p className="text-base font-semibold text-primary">No encontramos plantillas con ese criterio.</p>
                      <p className="mt-2 text-sm text-secondary">Limpia la búsqueda o sube una nueva plantilla Word.</p>
                    </div>
                  )}
                  {selectedTemplate && !selectedTemplateMatchesFilter ? (
                    <div className="ep-card-soft rounded-[1.5rem] px-5 py-4 text-sm text-secondary">
                      La plantilla seleccionada sigue activa aunque no aparezca en el filtro actual.
                    </div>
                  ) : null}
                </div>
              ) : null}

              {step === 1 ? (
                <div className="space-y-5">
                  <h2 className="text-2xl font-semibold text-primary">2. Datos de la minuta</h2>
                  <p className="text-sm text-secondary">
                    {canSelectNotary
                      ? "Selecciona la notaría donde se creará la minuta."
                      : "La minuta se creará en tu notaría asignada."}
                  </p>
                  {renderTemplateSummary()}
                  <div className="grid gap-4">
                    {canSelectNotary ? (
                      <SearchableSelect label="Notaría" value={generalForm.notary_id} options={notaries} onChange={(value) => setGeneralForm((current) => ({ ...current, notary_id: value }))} />
                    ) : (
                      <div className="ep-card-soft rounded-[1.6rem] p-4">
                        <p className="text-sm font-medium text-primary">Notaría</p>
                        <p className="mt-2 text-sm text-secondary">{selectedNotaryLabel}</p>
                      </div>
                    )}
                    {generalManagerFields.map((field) => {
                      const isExpanded = expandedGeneralField === field.key;
                      const selectedLabel = userOptions.find((item) => item.value === field.value)?.label || "Sin asignar";
                      return (
                        <div key={field.key} className="ep-card-soft z-0 rounded-[1.6rem] p-4 space-y-3" style={{ position: "relative", zIndex: "auto" }}>
                          <button
                            type="button"
                            onClick={() => setExpandedGeneralField((current) => (current === field.key ? null : field.key))}
                            className="flex w-full items-center justify-between gap-3 rounded-[1.1rem] px-4 py-3 text-left"
                          >
                            <span className="text-sm font-medium text-primary">{field.label}</span>
                            <span className="text-sm font-medium text-secondary">{selectedLabel}</span>
                          </button>
                          {isExpanded ? (
                            <SearchableSelect
                              label={field.label}
                              value={field.value}
                              options={userOptions}
                              onChange={(value) => updateGeneralManager(field.key, value)}
                            />
                          ) : null}
                        </div>
                      );
                    })}
                    {showSubstituteNotary ? (
                      <div className="space-y-3">
                        <SearchableSelect label="Notario suplente" value={generalForm.substitute_notary_user_id} options={userOptions} onChange={(value) => setGeneralForm((current) => ({ ...current, substitute_notary_user_id: value }))} />
                        <button
                          type="button"
                          onClick={() => setShowSubstituteNotary(false)}
                          className="inline-flex items-center gap-2 text-sm font-semibold text-primary"
                        >
                          - Ocultar notario suplente
                        </button>
                      </div>
                    ) : (
                      <button
                        type="button"
                        onClick={() => setShowSubstituteNotary(true)}
                        className="inline-flex items-center gap-2 text-sm font-semibold text-primary"
                      >
                        + Agregar notario suplente
                      </button>
                    )}
                  </div>
                  <label className="ep-card-muted flex items-center gap-3 rounded-2xl px-4 py-3 text-sm text-secondary">
                    <input type="checkbox" checked={generalForm.requires_client_review} onChange={(event) => setGeneralForm((current) => ({ ...current, requires_client_review: event.target.checked }))} />
                    Requiere revisión del cliente
                  </label>
                </div>
              ) : null}

              {step === 2 ? (
                <div className="space-y-5">
                  <h2 className="text-2xl font-semibold text-primary">3. Diligenciar</h2>
                  <p className="text-sm text-secondary">
                    Completa solo los campos detectados por la plantilla seleccionada. Al terminar, guarda y genera el Word para abrir el detalle de la minuta.
                  </p>
                  {renderTemplateSummary()}
                  {(() => {
                    const templateFields = sortByStepOrder(Array.isArray(selectedTemplate?.fields) ? selectedTemplate.fields : []);

                    if (templateFields.length === 0) {
                      return <p>La plantilla no tiene campos detectados todavía.</p>;
                    }

                    return (
                      <div className="grid grid-cols-1 gap-4">
                        {templateFields.map((field) => {
                          const label = `${field.label || field.field_code}${field.is_required ? " *" : ""}`;
                          const value = actData[field.field_code] ?? "";
                          const derivedSourceFieldCode = resolveDerivedMoneyField(field.field_code, templateFieldCodes);
                          const derivedValue = derivedSourceFieldCode ? numberToColombianPesosWords(actData[derivedSourceFieldCode] ?? "") : "";
                          const options = resolveCatalogOptions(field);

                          if (derivedSourceFieldCode) {
                            return (
                              <label key={field.field_code} className="grid gap-2 text-sm font-medium text-primary">
                                <span>{label}</span>
                                <input
                                  value={derivedValue}
                                  type="text"
                                  readOnly
                                  aria-readonly="true"
                                  placeholder={field.placeholder_key || ""}
                                  className="ep-input h-12 rounded-2xl px-4 text-secondary"
                                />
                                <span className="text-xs font-normal text-secondary">Calculado automáticamente desde el valor numérico.</span>
                              </label>
                            );
                          }

                          if (options.length > 0) {
                            return (
                              <div key={field.field_code} className="w-full">
                                <SearchableSelect
                                  label={label}
                                  value={value}
                                  options={options}
                                  onChange={(nextValue) => updateActField(field.field_code, nextValue)}
                                />
                              </div>
                            );
                          }

                          if (field.field_type === "textarea") {
                            return (
                              <div key={field.field_code} className="grid gap-2 text-sm font-medium text-primary">
                                <span>{label}</span>
                                <textarea
                                  value={value}
                                  rows={3}
                                  onChange={(event) => updateActField(field.field_code, event.target.value)}
                                  placeholder={field.placeholder_key || ""}
                                  className="ep-textarea"
                                />
                              </div>
                            );
                          }

                          return (
                            <div key={field.field_code} className="w-full">
                              <ValidatedInput
                                label={label}
                                type={field.field_type === "number" || field.field_type === "currency" ? "number" : field.field_type === "date" ? "date" : "text"}
                                value={value}
                                placeholder={field.placeholder_key || ""}
                                onChange={(nextValue) => updateActField(field.field_code, nextValue)}
                              />
                            </div>
                          );
                        })}
                      </div>
                    );
                  })()}
                </div>
              ) : null}
            </>
          ) : null}

          {error && !(isLoading && templates.length === 0) ? <div className="ep-kpi-critical rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
          {feedback ? <div className="ep-kpi-success rounded-2xl px-4 py-3 text-sm">{feedback}</div> : null}
          {!isLoading && templates.length > 0 && step < steps.length - 1 ? (
            <button
              type="button"
              onClick={() => void handlePrimaryAction()}
              disabled={isSaving || (step === 0 && !selectedTemplate)}
              className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
            >
              Continuar <ArrowRight className="h-4 w-4" />
            </button>
          ) : null}
          {!isLoading && templates.length > 0 && step === steps.length - 1 ? (
            <button type="button" onClick={() => void handlePrimaryAction()} disabled={isSaving} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:opacity-60">
              Guardar y generar Word <ArrowRight className="h-4 w-4" />
            </button>
          ) : null}
        </div>
      </section>
    </div>
  );
}

