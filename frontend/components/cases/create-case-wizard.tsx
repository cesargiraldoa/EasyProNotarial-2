"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ArrowRight, CheckCircle2, FileSignature } from "lucide-react";
import { PersonLookup } from "@/components/persons/person-lookup";
import { LegalEntityLookup, type LegalEntityPayload, type LegalEntityRecord } from "@/components/persons/legal-entity-lookup";
import { SearchableSelect } from "@/components/ui/searchable-select";
import { ValidatedInput } from "@/components/ui/validated-input";
import {
  createDocumentCase,
  generateCaseDraft,
  getActCatalog,
  getActiveTemplates,
  saveCaseActData,
  saveCaseActs,
  saveCaseParticipants,
  type ActCatalogItem,
  type CaseActItem,
  type PersonRecord,
  type DocumentFlowCase,
  type PersonPayload,
  type TemplateRecord,
} from "@/lib/document-flow";
import { getCurrentUser, getNotaries, getUserOptions, type UserOption } from "@/lib/api";

const steps = [
  "Tipo y actos",
  "Datos generales",
  "Intervinientes",
  "Datos del acto",
  "Revisión",
];
const documentTypes = ["CC", "CE", "TI", "PP", "NIT"];
const sexOptions = ["F", "M", "No especifica"];
const nationalityOptions = ["Colombiana", "Extranjera", "Venezolana", "Española"];
const maritalStatusOptions = ["Soltero(a)", "Casado(a)", "Unión marital", "Divorciado(a)", "Viudo(a)"];
const professionSuggestions = ["Abogado", "Comerciante", "Administrador", "Ingeniero", "Contador", "Docente"];

type SelectOption = { value: string; label: string };

type ParticipantItem = {
  uid: string;
  kind: "person" | "entity";
  roleCode: string;
  roleLabel: string;
  personId: number | null;
  person: PersonPayload | null;
  legalEntityId: number | null;
  legalEntity: LegalEntityPayload | null;
  representative: PersonRecord | PersonPayload | null;
  representativeId: number | null;
  isComplete: boolean;
};

const entityRoleOptions: SelectOption[] = [
  { value: "apoderado_banco_libera", label: "Banco que libera hipoteca" },
  { value: "apoderado_fideicomiso", label: "Fideicomiso / vendedor" },
  { value: "apoderado_fideicomitente", label: "Fideicomitente / constructora" },
  { value: "apoderado_banco_hipoteca", label: "Banco hipotecante" },
  { value: "apoderado_otro", label: "Otra entidad" },
];

const entityRoleLabelMap: Record<string, string> = {
  apoderado_banco_libera: "Banco que libera hipoteca",
  apoderado_fideicomiso: "Fideicomiso / vendedor",
  apoderado_fideicomitente: "Fideicomitente / constructora",
  apoderado_banco_hipoteca: "Banco hipotecante",
  apoderado_otro: "Otra entidad",
};

const ESCRITURA_TYPES = [
  {
    code: "compraventa_vis_contado",
    label: "Compraventa VIS  Contado",
    description: "Sin crédito hipotecario nuevo",
    defaultActs: ["liberacion_hipoteca", "protocolizacion_cto", "compraventa_vis", "renuncia_resolutoria", "cancelacion_comodato", "patrimonio_familia", "poder_especial"],
    templateSlug: "aragua-parq-1c",
  },
  {
    code: "compraventa_vis_hipoteca",
    label: "Compraventa VIS  Con crédito hipotecario",
    description: "Con constitución de hipoteca nueva",
    defaultActs: ["liberacion_hipoteca", "protocolizacion_cto", "compraventa_vis", "renuncia_resolutoria", "cancelacion_comodato", "constitucion_hipoteca", "patrimonio_familia", "poder_especial"],
    templateSlug: "jaggua-bogota-1c",
  },
  {
    code: "correccion_rc",
    label: "Corrección de Registro Civil",
    description: "Corrección de acta de nacimiento",
    defaultActs: ["correccion_rc"],
    templateSlug: "correccion-registro-civil",
  },
  {
    code: "salida_pais",
    label: "Permiso de salida del país",
    description: "Autorización para menor de edad",
    defaultActs: ["salida_pais"],
    templateSlug: "salida-del-pais",
  },
  {
    code: "poder_general",
    label: "Poder general",
    description: "Otorgamiento de poder",
    defaultActs: ["poder_general"],
    templateSlug: "poder-general",
  },
];

const ROLE_PARTICIPANT_MAP: Record<string, { kind: "person" | "entity"; roleCode: string; roleLabel: string }> = {
  compradores: { kind: "person", roleCode: "comprador_1", roleLabel: "Comprador(a)" },
  fideicomiso: { kind: "entity", roleCode: "apoderado_fideicomiso", roleLabel: "Fideicomiso / Vendedor" },
  banco_libera: { kind: "entity", roleCode: "apoderado_banco_libera", roleLabel: "Banco que libera hipoteca" },
  constructora: { kind: "entity", roleCode: "apoderado_fideicomitente", roleLabel: "Constructora" },
  banco_hipoteca: { kind: "entity", roleCode: "apoderado_banco_hipoteca", roleLabel: "Banco hipotecante" },
  inscrito: { kind: "person", roleCode: "inscrito", roleLabel: "Inscrito(a) / Compareciente" },
  padre_otorgante: { kind: "person", roleCode: "padre_otorgante", roleLabel: "Padre otorgante" },
  madre_aceptante: { kind: "person", roleCode: "madre_aceptante", roleLabel: "Madre aceptante" },
  menor: { kind: "person", roleCode: "menor", roleLabel: "Menor de edad" },
  poderdante: { kind: "person", roleCode: "poderdante", roleLabel: "Poderdante" },
  apoderado: { kind: "person", roleCode: "apoderado", roleLabel: "Apoderado(a)" },
};

interface ActWizardItem {
  uid: string;
  code: string;
  label: string;
  roles: string[];
}

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

function hasEntitySelection(item: ParticipantItem) {
  return item.legalEntityId !== null || item.legalEntity !== null;
}

function hasRepresentativeSelection(item: ParticipantItem) {
  return item.representativeId !== null || item.representative !== null;
}

function computeEntityComplete(item: ParticipantItem) {
  return hasEntitySelection(item) && hasRepresentativeSelection(item);
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

export function CreateCaseWizard() {
  const [step, setStep] = useState(0);
  const [templates, setTemplates] = useState<TemplateRecord[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateRecord | null>(null);
  const [escrituraType, setEscrituraType] = useState<string | null>(null);
  const [actWizardItems, setActWizardItems] = useState<ActWizardItem[]>([]);
  const [actCatalog, setActCatalog] = useState<ActCatalogItem[]>([]);
  const [dragIndex, setDragIndex] = useState<number | null>(null);
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
  const [expandedParticipantItems, setExpandedParticipantItems] = useState<Record<string, boolean>>({});
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
  const [participantItems, setParticipantItems] = useState<ParticipantItem[]>([]);
  const [actData, setActData] = useState<Record<string, string>>({});

  useEffect(() => {
    void load();
  }, []);

  useEffect(() => {
    setParticipantItems([]);
  }, [selectedTemplate]);

  useEffect(() => {
    setActData(buildActDataFromTemplate(selectedTemplate));
  }, [selectedTemplate]);

  function deriveParticipantsFromActs(acts: ActWizardItem[]): ParticipantItem[] {
    const seenRoles = new Set<string>();
    const derived: ParticipantItem[] = [];

    for (const act of acts) {
      for (const role of act.roles) {
        if (role === "compradores") continue;
        if (seenRoles.has(role)) continue;
        seenRoles.add(role);
        const mapping = ROLE_PARTICIPANT_MAP[role];
        if (!mapping) continue;
        derived.push({
          uid: crypto.randomUUID(),
          kind: mapping.kind,
          roleCode: mapping.roleCode,
          roleLabel: mapping.roleLabel,
          personId: null,
          person: null,
          legalEntityId: null,
          legalEntity: null,
          representative: null,
          representativeId: null,
          isComplete: false,
        });
      }
    }

    return derived;
  }

  async function load() {
    setIsLoading(true);
    setError(null);
    try {
      const [templateData, notaryData, userData, currentUser, catalogData] = await Promise.all([
        getActiveTemplates(),
        getNotaries(),
        getUserOptions(true),
        getCurrentUser(),
        getActCatalog(),
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
      console.log("notary_id seteado:", String(defaultNotaryRaw ?? ""));

      setTemplates(safeTemplates);
      setSelectedTemplate(
        safeTemplates.find((item) => item.slug === "poder-general") ?? safeTemplates[0] ?? null,
      );
      setNotaries(notaryOptions);
      setActCatalog(Array.isArray(catalogData) ? catalogData : []);
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
  const templateRoles = useMemo(() => sortByStepOrder(Array.isArray(selectedTemplate?.required_roles) ? selectedTemplate.required_roles : []), [selectedTemplate]);
  const templateFields = useMemo(() => sortByStepOrder(Array.isArray(selectedTemplate?.fields) ? selectedTemplate.fields : []), [selectedTemplate]);
  const buyerParticipantItems = useMemo(() => participantItems.filter((item) => item.kind === "person"), [participantItems]);
  const entityParticipantItems = useMemo(() => participantItems.filter((item) => item.kind === "entity"), [participantItems]);
  const showAside = step >= 3;
  const generalManagerFields = useMemo<Array<{ key: "current_owner_user_id" | "protocolist_user_id" | "approver_user_id" | "titular_notary_user_id"; label: string; value: string }>>(() => [
    { key: "current_owner_user_id", label: "Responsable actual", value: generalForm.current_owner_user_id },
    { key: "protocolist_user_id", label: "Protocolista", value: generalForm.protocolist_user_id },
    { key: "approver_user_id", label: "Aprobador", value: generalForm.approver_user_id },
    { key: "titular_notary_user_id", label: "Notario titular", value: generalForm.titular_notary_user_id },
  ], [generalForm.current_owner_user_id, generalForm.protocolist_user_id, generalForm.approver_user_id, generalForm.titular_notary_user_id]);

  function updateGeneralManager(field: "current_owner_user_id" | "protocolist_user_id" | "approver_user_id" | "titular_notary_user_id", value: string) {
    setGeneralForm((current) => ({ ...current, [field]: value }));
    setExpandedGeneralField(null);
  }

  function toPersonPayload(person: PersonRecord | PersonPayload): PersonPayload {
    return {
      document_type: person.document_type || "CC",
      document_number: person.document_number || "",
      full_name: person.full_name || "",
      sex: person.sex || "",
      nationality: person.nationality || "",
      marital_status: person.marital_status || "",
      profession: person.profession || "",
      municipality: person.municipality || "",
      is_transient: Boolean(person.is_transient),
      phone: person.phone || "",
      address: person.address || "",
      email: person.email || "",
      metadata_json: person.metadata_json || "{}",
    };
  }

  function normalizeParticipantItems(items: ParticipantItem[]) {
    const buyers = items.filter((item) => item.kind === "person");
    const entities = items.filter((item) => item.kind === "entity");
    const renumberedBuyers = buyers.map((item, index) => ({
      ...item,
      roleCode: `comprador_${index + 1}`,
      roleLabel: `Comprador(a) ${index + 1}`,
      isComplete: Boolean(item.personId || item.person),
    }));
    return [...renumberedBuyers, ...entities.map((item) => ({
      ...item,
      isComplete: Boolean(item.legalEntityId && item.representativeId && item.legalEntity && item.representative),
    }))];
  }

  function makeBuyerItem(index: number): ParticipantItem {
    return {
      uid: crypto.randomUUID(),
      kind: "person",
      roleCode: `comprador_${index}`,
      roleLabel: `Comprador(a) ${index}`,
      personId: null,
      person: null,
      legalEntityId: null,
      legalEntity: null,
      representative: null,
      representativeId: null,
      isComplete: false,
    };
  }

  function makeEntityItem(): ParticipantItem {
    return {
      uid: crypto.randomUUID(),
      kind: "entity",
      roleCode: "apoderado_otro",
      roleLabel: entityRoleLabelMap.apoderado_otro,
      personId: null,
      person: null,
      legalEntityId: null,
      legalEntity: null,
      representative: null,
      representativeId: null,
      isComplete: false,
    };
  }

  function updateParticipantItem(uid: string, updater: (current: ParticipantItem) => ParticipantItem) {
    setParticipantItems((current) => normalizeParticipantItems(current.map((item) => (item.uid === uid ? updater(item) : item))));
  }

  function updateBuyerPerson(uid: string, person: PersonRecord | PersonPayload, personId: number | null) {
    updateParticipantItem(uid, (current) => {
      const nextPerson = toPersonPayload(person);
      return {
        ...current,
        personId,
        person: nextPerson,
        isComplete: true,
      };
    });
  }

  function updateBuyerNewPerson(uid: string, person: PersonPayload) {
    updateParticipantItem(uid, (current) => ({
      ...current,
      personId: null,
      person: toPersonPayload(person),
      isComplete: true,
    }));
  }

  function clearBuyer(uid: string) {
    updateParticipantItem(uid, (current) => ({
      ...current,
      personId: null,
      person: null,
      isComplete: false,
    }));
  }

  function updateEntityRole(uid: string, roleCode: string) {
    updateParticipantItem(uid, (current) => ({
      ...current,
      roleCode,
      roleLabel: entityRoleLabelMap[roleCode] || "Otra entidad",
    }));
  }

  function updateEntityLegal(uid: string, entity: LegalEntityRecord | LegalEntityPayload, entityId: number | null) {
    updateParticipantItem(uid, (current) => ({
      ...current,
      legalEntityId: entityId,
      legalEntity: {
        nit: entity.nit || "",
        name: entity.name || "",
        legal_representative: entity.legal_representative || "",
        municipality: entity.municipality || "",
        address: entity.address || "",
        phone: entity.phone || "",
        email: entity.email || "",
      },
      isComplete: computeEntityComplete({
        ...current,
        legalEntityId: entityId,
        legalEntity: {
          nit: entity.nit || "",
          name: entity.name || "",
          legal_representative: entity.legal_representative || "",
          municipality: entity.municipality || "",
          address: entity.address || "",
          phone: entity.phone || "",
          email: entity.email || "",
        },
      }),
    }));
  }

  function updateEntityRepresentative(uid: string, person: PersonRecord | PersonPayload, personId: number | null) {
    updateParticipantItem(uid, (current) => ({
      ...current,
      representativeId: personId,
      representative: person,
      isComplete: computeEntityComplete({
        ...current,
        representativeId: personId,
        representative: person,
      }),
    }));
  }

  function clearEntityLegal(uid: string) {
    updateParticipantItem(uid, (current) => ({
      ...current,
      legalEntityId: null,
      legalEntity: null,
      isComplete: false,
    }));
  }

  function clearEntityRepresentative(uid: string) {
    updateParticipantItem(uid, (current) => ({
      ...current,
      representativeId: null,
      representative: null,
      isComplete: false,
    }));
  }

  function addBuyer() {
    const nextItem = makeBuyerItem(participantItems.filter((item) => item.kind === "person").length + 1);
    setParticipantItems((current) => normalizeParticipantItems([...current, nextItem]));
    setExpandedParticipantItems((current) => ({ ...current, [nextItem.uid]: true }));
  }

  function addEntity() {
    const nextItem = makeEntityItem();
    setParticipantItems((current) => normalizeParticipantItems([...current, nextItem]));
    setExpandedParticipantItems((current) => ({ ...current, [nextItem.uid]: true }));
  }

  function removeParticipant(uid: string) {
    setParticipantItems((current) => normalizeParticipantItems(current.filter((item) => item.uid !== uid)));
    setExpandedParticipantItems((current) => {
      const next = { ...current };
      delete next[uid];
      return next;
    });
  }

  function validateParticipants() {
    const buyers = participantItems.filter((item) => item.kind === "person");
    const entities = participantItems.filter((item) => item.kind === "entity");
    if (!buyers.some((item) => item.isComplete && (item.personId !== null || item.person !== null))) {
      return "Debes agregar al menos 1 comprador completo.";
    }
    for (const entity of entities) {
      const entityReady = hasEntitySelection(entity) && hasRepresentativeSelection(entity);
      if (!entityReady) {
        return "Cada entidad agregada debe tener entidad y apoderado completos.";
      }
    }
    return null;
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

  async function continueStep() {
    setError(null);
    setFeedback(null);
    setIsSaving(true);
    try {
      let activeCase = caseDetail;
      if (step === 0) {
        if (!escrituraType || actWizardItems.length === 0) {
          throw new Error("Selecciona el tipo de escritura y confirma los actos antes de continuar.");
        }
        if (!selectedTemplate) {
          throw new Error("No hay plantilla base disponible. Contacta al administrador.");
        }
        const derived = deriveParticipantsFromActs(actWizardItems);
        setParticipantItems(derived);
      }
      if (step === 1 && !activeCase) {
        activeCase = await handleCreateCase();
      }
      if (step === 1 && activeCase) {
  const actsPayload = actWizardItems.map((a, idx) => ({
    code: a.code,
    label: a.label,
    act_order: idx + 1,
    roles_json: Array.isArray(a.roles) ? JSON.stringify(a.roles) : (a.roles ?? "[]"),
  }));
        await saveCaseActs(activeCase.id, actsPayload);
      }
      if (step === 2 && activeCase) {
        const participantError = validateParticipants();
        if (participantError) {
          throw new Error(participantError);
        }
        const payload = participantItems.map((item) =>
          item.kind === "person"
            ? {
                role_code: item.roleCode,
                role_label: item.roleLabel,
                person_id: item.personId,
                person: item.person,
              }
            : {
                role_code: item.roleCode,
                role_label: item.roleLabel,
                person_id: item.representativeId,
                person: item.representative,
                legal_entity_id: item.legalEntityId,
                legal_entity: item.legalEntity,
              },
        );
        const updated = await saveCaseParticipants(
          activeCase.id,
          payload as any,
        );
        setCaseDetail(updated);
      }
      if (step === 3 && activeCase) {
        const missingRequiredField = templateFields.find((field) => field.is_required && !(actData[field.field_code] ?? "").trim());
        if (missingRequiredField) {
          throw new Error(`Completa el campo obligatorio ${missingRequiredField.label || missingRequiredField.field_code}.`);
        }
        const updated = await saveCaseActData(activeCase.id, { data_json: JSON.stringify(actData) });
        setCaseDetail(updated);
      }
      if (step === 4 && caseDetail) {
        const updated = await generateCaseDraft(caseDetail.id, "Generado con Gari desde el wizard.");
        setCaseDetail(updated);
        window.location.href = `/dashboard/casos/${caseDetail.id}?tab=documento-gari`;
        return;
      }
      setStep((current) => Math.min(current + 1, steps.length - 1));
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
              {caseDetail?.internal_case_number ? `Crear Minuta · ${caseDetail.internal_case_number}` : "Crear Minuta"}
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
        <div className="grid gap-3 xl:grid-cols-5">
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

      <section className={`grid gap-6 ${showAside ? "xl:grid-cols-[minmax(0,1.2fr)_360px]" : "xl:grid-cols-1"}`}>
        <div className="ep-card z-0 rounded-[2rem] p-6 space-y-6">
          {isLoading ? <div className="ep-card-muted z-0 rounded-[1.5rem] px-4 py-6 text-sm text-secondary">Cargando plantillas, notarías y usuarios...</div> : null}
          {!isLoading && error && templates.length === 0 ? <div className="ep-kpi-critical z-0 rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
          {!isLoading && !error && templates.length === 0 ? <div className="ep-card-muted z-0 rounded-[1.5rem] px-4 py-6 text-sm text-secondary">No hay plantillas activas todavía.</div> : null}

          {!isLoading && templates.length > 0 ? (
            <>
              {step === 0 ? (
                <div className="space-y-6">
                  {!escrituraType ? (
                    <div className="space-y-5">
                      <div>
                        <h2 className="text-2xl font-semibold text-primary">1. Tipo de escritura</h2>
                        <p className="mt-1 text-sm text-secondary">Selecciona la operación que vas a escriturar.</p>
                      </div>
                      <div className="grid gap-4 lg:grid-cols-2">
                        {ESCRITURA_TYPES.map((tipo) => (
                          <button
                            key={tipo.code}
                            type="button"
                            onClick={() => {
                              setEscrituraType(tipo.code);
                              const matched = tipo.defaultActs.map((actCode) => {
                                const found = actCatalog.find((a) => a.code === actCode);
                                if (!found) return null;
                                return {
                                  uid: crypto.randomUUID(),
                                  code: found.code,
                                  label: found.label,
                                  roles: JSON.parse(found.roles_json || "[]"),
                                } as ActWizardItem;
                              }).filter(Boolean) as ActWizardItem[];
                              setActWizardItems(matched);
                              const tmpl = templates.find((t) => t.slug === tipo.templateSlug) ?? templates[0] ?? null;
                              setSelectedTemplate(tmpl);
                            }}
                            className="rounded-[1.5rem] border p-5 text-left hover:border-primary/30 hover:bg-primary/5 transition-colors border-[var(--line)]"
                          >
                            <p className="text-lg font-semibold text-primary">{tipo.label}</p>
                            <p className="mt-2 text-sm text-secondary">{tipo.description}</p>
                            <p className="mt-3 text-xs text-secondary">{tipo.defaultActs.length} acto{tipo.defaultActs.length !== 1 ? "s" : ""} sugeridos</p>
                          </button>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-5">
                      <div className="flex items-center justify-between gap-3">
                        <div>
                          <h2 className="text-2xl font-semibold text-primary">1. Actos de la escritura</h2>
                          <p className="mt-1 text-sm text-secondary">
                            {ESCRITURA_TYPES.find((t) => t.code === escrituraType)?.label} · Reordena arrastrando, quita o agrega actos según el caso.
                          </p>
                        </div>
                        <button
                          type="button"
                          onClick={() => { setEscrituraType(null); setActWizardItems([]); }}
                          className="text-sm font-semibold text-primary underline"
                        >
                          Cambiar tipo
                        </button>
                      </div>

                      <div className="space-y-2">
                        {actWizardItems.map((act, index) => (
                          <div
                            key={act.uid}
                            draggable
                            onDragStart={() => setDragIndex(index)}
                            onDragOver={(e) => e.preventDefault()}
                            onDrop={() => {
                              if (dragIndex === null || dragIndex === index) return;
                              const reordered = [...actWizardItems];
                              const [moved] = reordered.splice(dragIndex, 1);
                              reordered.splice(index, 0, moved);
                              setActWizardItems(reordered);
                              setDragIndex(null);
                            }}
                            onDragEnd={() => setDragIndex(null)}
                            className={`flex items-center gap-3 rounded-[1.4rem] border bg-[var(--panel)] px-4 py-3 cursor-grab active:cursor-grabbing transition-opacity ${dragIndex === index ? "opacity-40" : "opacity-100"} border-[var(--line)]`}
                          >
                            <span className="text-secondary select-none text-lg leading-none"></span>
                            <span className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">
                              {index + 1}
                            </span>
                            <span className="flex-1 text-sm font-medium text-primary">{act.label}</span>
                            <button
                              type="button"
                              onClick={() => setActWizardItems((prev) => prev.filter((a) => a.uid !== act.uid))}
                              className="text-rose-500 text-xs font-semibold px-3 py-1 rounded-xl hover:bg-rose-50 transition-colors"
                            >
                              Quitar
                            </button>
                          </div>
                        ))}
                      </div>

                      {actCatalog.filter((a) => !actWizardItems.some((item) => item.code === a.code)).length > 0 ? (
                        <div className="space-y-3">
                          <p className="text-sm font-semibold text-primary">+ Agregar acto</p>
                          <div className="grid gap-2 lg:grid-cols-2">
                            {actCatalog
                              .filter((a) => !actWizardItems.some((item) => item.code === a.code))
                              .map((a) => (
                                <button
                                  key={a.code}
                                  type="button"
                                  onClick={() =>
                                    setActWizardItems((prev) => [
                                      ...prev,
                                      {
                                        uid: crypto.randomUUID(),
                                        code: a.code,
                                        label: a.label,
                                        roles: JSON.parse(a.roles_json || "[]"),
                                      },
                                    ])
                                  }
                                  className="rounded-[1.2rem] border border-dashed border-[var(--line)] px-4 py-2 text-left text-sm text-secondary hover:border-primary/30 hover:text-primary transition-colors"
                                >
                                  + {a.label}
                                </button>
                              ))}
                          </div>
                        </div>
                      ) : null}

                      {actWizardItems.length === 0 ? (
                        <div className="ep-card-muted rounded-[1.5rem] px-4 py-5 text-sm text-secondary">
                          Agrega al menos un acto para continuar.
                        </div>
                      ) : null}
                    </div>
                  )}
                </div>
              ) : null}

              {step === 1 ? (
                <div className="space-y-5">
                  <h2 className="text-2xl font-semibold text-primary">2. Datos generales de la minuta</h2>
                  <div className="grid gap-4">
                    {canSelectNotary ? (
                      <SearchableSelect label="Notaría" value={generalForm.notary_id} options={notaries} onChange={(value) => setGeneralForm((current) => ({ ...current, notary_id: value }))} />
                    ) : null}
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
                    Requiere revisión cliente
                  </label>
                </div>
              ) : null}

              {step === 2 ? (
                <div className="space-y-6">
                  <h2 className="text-2xl font-semibold text-primary">3. Intervinientes</h2>
                  <p className="mt-1 text-sm text-secondary">
                    El sistema identificó los intervinientes requeridos según los actos seleccionados. Completa cada uno y agrega los compradores.
                  </p>

                  <section className="space-y-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <h3 className="text-xl font-semibold text-primary">Compradores</h3>
                        <p className="text-sm text-secondary">Agrega una o varias personas naturales compradoras.</p>
                      </div>
                      <button
                        type="button"
                        onClick={addBuyer}
                        className="inline-flex items-center gap-2 rounded-2xl bg-primary px-4 py-2 text-sm font-semibold text-white"
                      >
                        + Agregar comprador
                      </button>
                    </div>

                    <div className="space-y-4">
                      {buyerParticipantItems.length > 0 ? buyerParticipantItems.map((item) => {
                        const isExpanded = Boolean(expandedParticipantItems[item.uid]);
                        const displayPerson = item.personId !== null || item.person ? item.person : null;
                        return (
                          <div key={item.uid} className="ep-card-soft rounded-[1.8rem] p-5 space-y-4">
                            <button
                              type="button"
                              onClick={() => setExpandedParticipantItems((current) => ({ ...current, [item.uid]: !current[item.uid] }))}
                              className="flex w-full min-h-12 items-center justify-between gap-3 rounded-[1.25rem] px-4 py-3 text-left"
                            >
                              <div className="space-y-1">
                                <p className="text-sm font-medium text-primary">{item.roleLabel}</p>
                                <h3 className="text-sm font-medium text-secondary">Comprador natural</h3>
                              </div>
                              <span className={`ep-pill rounded-full px-3 py-1 text-xs font-semibold ${item.isComplete ? "bg-emerald-500/10 text-emerald-700" : "text-secondary"}`}>
                                {item.isComplete ? "Completo" : "Incompleto"}
                              </span>
                            </button>
                            {isExpanded ? (
                              <div className="space-y-4">
                                {item.isComplete && displayPerson ? (
                                  <div className="rounded-[1.35rem] border border-emerald-500/20 bg-emerald-500/10 p-4">
                                    <div className="flex items-start justify-between gap-3">
                                      <div>
                                        <p className="text-sm font-semibold text-primary">{displayPerson.full_name || "Comprador asignado"}</p>
                                        <p className="mt-1 text-sm text-secondary">
                                          {displayPerson.document_type || "DOC"} {displayPerson.document_number || "Sin número"} · {displayPerson.municipality || "Sin municipio"}
                                        </p>
                                      </div>
                                      <CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-600" />
                                    </div>
                                    <div className="mt-4 flex flex-wrap items-center gap-3">
                                      <button
                                        type="button"
                                        onClick={() => clearBuyer(item.uid)}
                                        className="inline-flex items-center gap-2 text-sm font-semibold text-primary"
                                      >
                                        Cambiar
                                      </button>
                                      <button
                                        type="button"
                                        onClick={() => removeParticipant(item.uid)}
                                        className="inline-flex items-center gap-2 text-sm font-semibold text-rose-600"
                                      >
                                        Eliminar
                                      </button>
                                    </div>
                                  </div>
                                ) : (
                                  <PersonLookup
                                    onPick={(selected) => updateBuyerPerson(item.uid, selected, selected.id)}
                                    onNotFound={(person) => updateBuyerNewPerson(item.uid, person)}
                                  />
                                )}
                              </div>
                            ) : null}
                          </div>
                        );
                      }) : (
                        <div className="ep-card-muted rounded-[1.5rem] px-4 py-5 text-sm text-secondary">
                          Todavía no hay compradores agregados.
                        </div>
                      )}
                    </div>
                  </section>

                  <section className="space-y-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <h3 className="text-xl font-semibold text-primary">Entidades y apoderados</h3>
                        <p className="text-sm text-secondary">Agrega bancos, fiducias o constructoras con su apoderado.</p>
                      </div>
                      <button
                        type="button"
                        onClick={addEntity}
                        className="inline-flex items-center gap-2 rounded-2xl bg-primary px-4 py-2 text-sm font-semibold text-white"
                      >
                        + Agregar entidad
                      </button>
                    </div>

                    <div className="space-y-4">
                      {entityParticipantItems.length > 0 ? entityParticipantItems.map((item) => {
                        const isExpanded = Boolean(expandedParticipantItems[item.uid]);
                        const entitySummary = item.legalEntity;
                        const representativeSummary = item.representative;
                        return (
                          <div key={item.uid} className="ep-card-soft rounded-[1.8rem] p-5 space-y-4">
                            <button
                              type="button"
                              onClick={() => setExpandedParticipantItems((current) => ({ ...current, [item.uid]: !current[item.uid] }))}
                              className="flex w-full min-h-12 items-center justify-between gap-3 rounded-[1.25rem] px-4 py-3 text-left"
                            >
                              <div className="space-y-1">
                                <p className="text-sm font-medium text-primary">{item.roleLabel}</p>
                                <h3 className="text-sm font-medium text-secondary">Entidad y apoderado</h3>
                              </div>
                              <span className={`ep-pill rounded-full px-3 py-1 text-xs font-semibold ${item.isComplete ? "bg-emerald-500/10 text-emerald-700" : "text-secondary"}`}>
                                {item.isComplete ? "Completo" : "Incompleto"}
                              </span>
                            </button>

                            {isExpanded ? (
                              <div className="space-y-4">
                                <div className="space-y-3 rounded-[1.4rem] border border-[var(--line)] bg-[var(--panel-soft)] p-4">
                                  <div className="flex items-center justify-between gap-3">
                                    <p className="text-sm font-semibold text-primary">Rol de la entidad</p>
                                  </div>
                                  <label className="grid gap-2 text-sm font-medium text-primary">
                                    <span>Rol</span>
                                    <select
                                      value={item.roleCode}
                                      onChange={(event) => updateEntityRole(item.uid, event.target.value)}
                                      className="ep-select h-11 rounded-2xl px-4"
                                    >
                                      {entityRoleOptions.map((option) => (
                                        <option key={option.value} value={option.value}>
                                          {option.label}
                                        </option>
                                      ))}
                                    </select>
                                  </label>
                                </div>

                                <div className="space-y-3 rounded-[1.4rem] border border-[var(--line)] bg-[var(--panel-soft)] p-4">
                                  <div className="flex items-center justify-between gap-3">
                                    <p className="text-sm font-semibold text-primary">Entidad</p>
                                    {item.legalEntity && item.legalEntityId ? (
                                      <span className="ep-pill rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-700">Completo</span>
                                    ) : null}
                                  </div>
                                {hasEntitySelection(item) ? (
                                  <div className="rounded-[1.35rem] border border-emerald-500/20 bg-emerald-500/10 p-4">
                                    <div className="flex items-start justify-between gap-3">
                                      <div>
                                        <p className="text-sm font-semibold text-primary">{entitySummary?.name || "Entidad asignada"}</p>
                                          <p className="mt-1 text-sm text-secondary">
                                            {entitySummary?.nit || "Sin NIT"}{entitySummary?.municipality ? ` · ${entitySummary.municipality}` : ""}
                                          </p>
                                        </div>
                                        <CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-600" />
                                      </div>
                                      <button
                                        type="button"
                                        onClick={() => clearEntityLegal(item.uid)}
                                        className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-primary"
                                      >
                                        Cambiar
                                      </button>
                                    </div>
                                  ) : (
                                    <LegalEntityLookup
                                      onPick={(entity) => updateEntityLegal(item.uid, entity, entity.id)}
                                      onNotFound={(entity) => updateEntityLegal(item.uid, entity, null)}
                                    />
                                  )}
                                </div>

                                {hasEntitySelection(item) ? (
                                  <div className="space-y-3 rounded-[1.4rem] border border-[var(--line)] bg-[var(--panel-soft)] p-4">
                                    <div className="flex items-center justify-between gap-3">
                                      <p className="text-sm font-semibold text-primary">Apoderado</p>
                                      {hasRepresentativeSelection(item) ? (
                                        <span className="ep-pill rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-700">Completo</span>
                                      ) : null}
                                    </div>
                                    {hasRepresentativeSelection(item) ? (
                                      <div className="rounded-[1.35rem] border border-emerald-500/20 bg-emerald-500/10 p-4">
                                        <div className="flex items-start justify-between gap-3">
                                          <div>
                                            <p className="text-sm font-semibold text-primary">{representativeSummary?.full_name || "Apoderado asignado"}</p>
                                            <p className="mt-1 text-sm text-secondary">
                                              {representativeSummary?.document_type || "DOC"} {representativeSummary?.document_number || "Sin número"} · {representativeSummary?.municipality || "Sin municipio"}
                                            </p>
                                          </div>
                                          <CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-600" />
                                        </div>
                                        <button
                                          type="button"
                                          onClick={() => clearEntityRepresentative(item.uid)}
                                          className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-primary"
                                        >
                                          Cambiar
                                        </button>
                                      </div>
                                    ) : (
                                      <PersonLookup
                                        onPick={(selected) => updateEntityRepresentative(item.uid, selected, selected.id)}
                                        onNotFound={(person) => updateEntityRepresentative(item.uid, person, null)}
                                      />
                                    )}
                                  </div>
                                ) : null}

                                <button
                                  type="button"
                                  onClick={() => removeParticipant(item.uid)}
                                  className="inline-flex items-center gap-2 text-sm font-semibold text-rose-600"
                                >
                                  Eliminar
                                </button>
                              </div>
                            ) : null}
                          </div>
                        );
                      }) : (
                        <div className="ep-card-muted rounded-[1.5rem] px-4 py-5 text-sm text-secondary">
                          Todavía no hay entidades agregadas.
                        </div>
                      )}
                    </div>
                  </section>
                </div>
              ) : null}

              {step === 3 ? (
                <div className="space-y-5">
                  <h2 className="text-2xl font-semibold text-primary">4. Datos del acto</h2>
                  {templateFields.length > 0 ? (
                    <div className="grid grid-cols-1 gap-4">
                      {templateFields.map((field) => {
                        const label = `${field.label || field.field_code}${field.is_required ? " *" : ""}`;
                        const value = actData[field.field_code] ?? "";

                        if (field.field_type === "select") {
                          return (
                            <div key={field.field_code} className="w-full">
                              <SearchableSelect
                                label={label}
                                value={value}
                                options={parseTemplateFieldOptions(field.options_json)}
                                onChange={(nextValue) => setActData((current) => ({ ...current, [field.field_code]: nextValue }))}
                              />
                            </div>
                          );
                        }

                        if (field.field_type === "textarea") {
                          return (
                            <label key={field.field_code} className="grid gap-2 text-sm font-medium text-primary">
                              <span>{label}</span>
                              <textarea
                                value={value}
                                onChange={(event) => setActData((current) => ({ ...current, [field.field_code]: event.target.value }))}
                                placeholder={field.placeholder_key || ""}
                                className="ep-input rounded-2xl px-4 py-3 w-full"
                              />
                            </label>
                          );
                        }

                        if (field.field_type === "date") {
                          return (
                            <label key={field.field_code} className="grid gap-2 text-sm font-medium text-primary">
                              <span>{label}</span>
                              <input
                                type="date"
                                value={value}
                                onChange={(event) => setActData((current) => ({ ...current, [field.field_code]: event.target.value }))}
                                className="ep-input h-12 rounded-2xl px-4"
                              />
                            </label>
                          );
                        }

                        if (field.field_type === "currency") {
                          return (
                            <label key={field.field_code} className="grid gap-2 text-sm font-medium text-primary">
                              <span>{label}</span>
                              <div className="relative">
                                <span className="pointer-events-none absolute inset-y-0 left-4 flex items-center text-sm text-secondary">$</span>
                                <input
                                  type="number"
                                  value={value}
                                  onChange={(event) => setActData((current) => ({ ...current, [field.field_code]: event.target.value }))}
                                  placeholder={field.placeholder_key || ""}
                                  className="ep-input h-12 rounded-2xl px-4 pl-8"
                                />
                              </div>
                            </label>
                          );
                        }

                        if (field.field_type === "number") {
                          return (
                            <ValidatedInput
                              key={field.field_code}
                              label={label}
                              type="number"
                              value={value}
                              placeholder={field.placeholder_key || ""}
                              onChange={(nextValue) => setActData((current) => ({ ...current, [field.field_code]: nextValue }))}
                            />
                          );
                        }

                        return (
                          <ValidatedInput
                            key={field.field_code}
                            label={label}
                            value={value}
                            placeholder={field.placeholder_key || ""}
                            onChange={(nextValue) => setActData((current) => ({ ...current, [field.field_code]: nextValue }))}
                          />
                        );
                      })}
                    </div>
                  ) : (
                    <div className="ep-card-muted z-0 rounded-[1.5rem] px-4 py-6 text-sm text-secondary">La plantilla seleccionada no tiene campos configurados.</div>
                  )}
                </div>
              ) : null}

              {step === 4 ? (
                <div className="space-y-5">
                  <h2 className="text-2xl font-semibold text-primary">5. Revisión</h2>
                  <div className="ep-card-soft rounded-[1.5rem] p-5 space-y-3">
                    <p className="text-sm font-semibold text-primary">Tipo de escritura</p>
                    <p className="text-sm text-secondary">
                      {ESCRITURA_TYPES.find((t) => t.code === escrituraType)?.label ?? "Sin definir"}
                    </p>
                    <p className="mt-3 text-sm font-semibold text-primary">Actos confirmados</p>
                    <div className="space-y-1">
                      {actWizardItems.map((a, i) => (
                        <p key={a.uid} className="text-sm text-secondary">{i + 1}. {a.label}</p>
                      ))}
                    </div>
                    <p className="mt-3 text-sm font-semibold text-primary">Número interno</p>
                    <p className="text-sm text-secondary">{caseDetail?.internal_case_number ?? ""}</p>
                  </div>
                  <div className="ep-card-muted rounded-[1.5rem] px-4 py-4 text-sm text-secondary">
                    Todo listo. Al continuar, el sistema generará la escritura con Gari y podrás previsualizarla, descargarla o regenerarla.
                  </div>
                </div>
              ) : null}
            </>
          ) : null}

          {error && !(isLoading && templates.length === 0) ? <div className="ep-kpi-critical rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
          {feedback ? <div className="ep-kpi-success rounded-2xl px-4 py-3 text-sm">{feedback}</div> : null}
          {!isLoading && templates.length > 0 && step < 4 ? (
            <button type="button" onClick={() => void continueStep()} disabled={isSaving} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:opacity-60">
              Continuar <ArrowRight className="h-4 w-4" />
            </button>
          ) : null}
          {!isLoading && templates.length > 0 && step === 4 ? (
            <button type="button" onClick={() => void continueStep()} disabled={isSaving} className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-3 text-sm font-semibold text-white disabled:opacity-60">
              Generar con Gari <ArrowRight className="h-4 w-4" />
            </button>
          ) : null}
        </div>

        {showAside ? (
          <aside className="space-y-4">
            <div className="ep-card z-0 rounded-[1.8rem] p-5">
              <p className="text-xs uppercase tracking-[0.2em] text-secondary">Minuta activa</p>
              <p className="mt-2 text-lg font-semibold text-primary">{caseDetail?.internal_case_number || "Aún no creado"}</p>
              <p className="mt-3 text-sm text-secondary">Plantilla: {selectedTemplate?.name || "Sin selección"}</p>
              <p className="mt-2 text-sm text-secondary">Estado: {caseDetail?.current_state || "borrador"}</p>
              <p className="mt-2 text-sm text-secondary">Escritura oficial: {caseDetail?.official_deed_number || "Pendiente de aprobación"}</p>
            </div>
            <div className="ep-card z-0 rounded-[1.8rem] p-5">
              <p className="text-xs uppercase tracking-[0.2em] text-secondary">Reglas funcionales</p>
              <ul className="mt-3 space-y-2 text-sm leading-6 text-secondary">
                <li>La plantilla define el trámite.</li>
                <li>El número oficial no se asigna al crear.</li>
                <li>Poderdante y apoderado son obligatorios.</li>
                <li>Las personas se reutilizan por tipo y número.</li>
              </ul>
            </div>
          </aside>
        ) : null}
      </section>
    </div>
  );
}

