"use client";

import {
  Bold,
  CheckCheck,
  Eraser,
  FileDown,
  Highlighter,
  Italic,
  Link2,
  Link2Off,
  MessageSquare,
  Printer,
  Save,
  Strikethrough,
  Underline,
  X,
} from "lucide-react";
import { forwardRef, useCallback, useEffect, useImperativeHandle, useMemo, useRef, useState, type ReactNode } from "react";
import { CumplimientoPanel } from "@/components/escritura/cumplimiento-panel";
import { LiquidacionPanel } from "@/components/escritura/liquidacion-panel";
import { bibliotecaRedaccionPorActo, type BibliotecaRedaccionItem } from "@/lib/escritura-redaccion-biblioteca";
import type { ActoCode, CancelacionState, CaseState, CompraventaState, Resultado } from "@/lib/motor-escritura";
import styles from "./escritura-preview.module.css";

export type RedaccionComment = {
  id: string;
  quote: string;
  text: string;
  resolved: boolean;
};

export type RedaccionDraft = {
  acto: ActoCode;
  html: string;
  comments: RedaccionComment[];
  updated_at: string;
};

export type EscrituraEditorHandle = {
  getDraft: () => RedaccionDraft;
  getHtmlForExport: () => string;
  isDirty: () => boolean;
  markClean: () => void;
};

type Props = {
  acto: ActoCode;
  state: CaseState;
  sourceHtml: string;
  cumplimiento: Resultado["cumplimiento"];
  liquidacionHtml: string;
  draft: RedaccionDraft | null;
  bloqueantes: number;
  isSaving?: boolean;
  isGenerating?: boolean;
  onSaveDraft: (draft: RedaccionDraft) => Promise<void>;
  onExportWord: (html: string) => Promise<void>;
  onDirtyChange?: (dirty: boolean) => void;
  onStatus?: (message: string) => void;
  bibliotecaItems?: BibliotecaRedaccionItem[] | null;
  bibliotecaError?: string | null;
};

type LinkedField = {
  field: string;
  label: string;
  value: string;
};

const HIGHLIGHTS = [
  { label: "Amarillo", value: "#FCE96A" },
  { label: "Verde", value: "#B7E4C7" },
  { label: "Rosa", value: "#F7C5D9" },
  { label: "Azul", value: "#BFE3F5" },
  { label: "Naranja", value: "#FBD9A8" },
] as const;

const FILL_LEADER = " ........................................................................................................";

const PRINT_CSS = `
@page{size:A4;margin:18mm}
body{background:#fff;color:#1b1e23;font-family:Georgia,"Times New Roman",serif;font-size:12pt;line-height:1.72}
.sheet{box-shadow:none;border:0;margin:0;max-width:none;padding:0}
.campo{background:transparent;border:0;padding:0}
.mark{box-shadow:none}
.cmt{background:transparent;border-bottom:1px dotted #b0781a}
ins.track{color:#167044;text-decoration:underline}
del.track{color:#a82f2f;text-decoration:line-through}
.fill{display:inline;color:#777}
.cite{display:none}
`;

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function isCompraventaState(value: CaseState): value is CompraventaState {
  return isRecord(value) && Array.isArray(value.V) && Array.isArray(value.C);
}

function isCancelacionState(value: CaseState): value is CancelacionState {
  return isRecord(value) && typeof value.cNum === "string";
}

function text(value: unknown) {
  return value == null ? "" : String(value);
}

function all<T extends Element = HTMLElement>(root: ParentNode, selector: string): T[] {
  return Array.from(root.querySelectorAll<T>(selector));
}

function elementFromNode(node: Node | null): HTMLElement | null {
  if (!node) return null;
  if (node instanceof HTMLElement) return node;
  const parent = node.parentElement;
  return parent instanceof HTMLElement ? parent : null;
}

function rangeIsInside(editor: HTMLElement, range: Range) {
  const node = range.commonAncestorContainer;
  const candidate = node.nodeType === Node.ELEMENT_NODE ? node : node.parentNode;
  return Boolean(candidate && editor.contains(candidate));
}

function getSelectionRange(editor: HTMLElement): Range | null {
  const selection = window.getSelection();
  if (!selection || selection.rangeCount === 0) return null;
  const range = selection.getRangeAt(0);
  return rangeIsInside(editor, range) ? range : null;
}

function unwrapWithChildren(element: HTMLElement) {
  const parent = element.parentNode;
  if (!parent) return;
  while (element.firstChild) parent.insertBefore(element.firstChild, element);
  parent.removeChild(element);
}

function unwrapAsText(element: HTMLElement) {
  const parent = element.parentNode;
  if (!parent) return;
  parent.replaceChild(document.createTextNode(element.textContent ?? ""), element);
}

function buildEditableHtml(html: string) {
  const root = document.createElement("div");
  root.innerHTML = html;
  all<HTMLElement>(root, "span.ins[data-f]").forEach((item) => {
    const field = item.getAttribute("data-f") || "";
    item.classList.remove("ins");
    item.classList.add("campo");
    item.setAttribute("data-field", field);
    item.removeAttribute("data-f");
  });
  all<HTMLElement>(root, "span.rulec").forEach((item) => {
    item.classList.remove("rulec");
  });
  all<HTMLElement>(root, "span.cite, span.fill").forEach((item) => {
    item.remove();
  });
  all<HTMLElement>(root, "span.ins").forEach((item) => {
    item.classList.remove("ins");
  });
  return root.innerHTML;
}

function materializeFillLeaders(html: string) {
  const root = document.createElement("div");
  root.innerHTML = html;
  all<HTMLElement>(root, ".fill").forEach((item) => item.remove());
  all<HTMLElement>(root, "p.cl, p.para").forEach((block) => {
    const span = document.createElement("span");
    span.className = "fill";
    span.textContent = FILL_LEADER;
    block.appendChild(span);
  });
  return root.innerHTML;
}

function createFragment(html: string) {
  const template = document.createElement("template");
  template.innerHTML = html.trim();
  return template.content;
}

function placeCaretAtEnd(element: HTMLElement) {
  const range = document.createRange();
  range.selectNodeContents(element);
  range.collapse(false);
  const selection = window.getSelection();
  selection?.removeAllRanges();
  selection?.addRange(range);
}

function selectedQuote(range: Range) {
  return range.toString().replace(/\s+/g, " ").trim().slice(0, 220);
}

function buildEditorLabels(acto: ActoCode, state: CaseState) {
  const labels: Record<string, string> = {};
  if (acto === "cancelacion" && isCancelacionState(state)) {
    Object.assign(labels, {
      cNum: "Numero de escritura",
      cFechaOtorg: "Fecha de otorgamiento",
      cNotario: "Notario",
      cCalidad: "Calidad",
      cActoAdmin: "Acto administrativo",
      cBanco: "Banco",
      cBancoNit: "NIT banco",
      cBancoDom: "Domicilio banco",
      cRepCargo: "Cargo compareciente",
      cApoNombre: "Compareciente",
      cApoCC: "Documento compareciente",
      cPoderEP: "Escritura del poder",
      cPoderFecha: "Fecha del poder",
      cPoderNotaria: "Notaria del poder",
      cDeudor: "Deudor",
      cHipEP: "Escritura hipoteca",
      cHipFecha: "Fecha hipoteca",
      cHipNotaria: "Notaria hipoteca",
      cHipRegFecha: "Registro hipoteca",
      cOrip: "ORIP",
      cHipMonto: "Monto hipoteca",
      cInmdesc: "Descripcion inmueble",
      cMatricula: "Matricula inmobiliaria",
      cCatastral: "Cedula catastral",
      cNupre: "NUPRE",
      cHojas: "Hojas notariales",
      cRecaudo: "Recaudo SNR",
      cCorreoNotif: "Correo notificaciones",
    });
    return labels;
  }

  if (isCompraventaState(state)) {
    Object.assign(labels, {
      inmdesc: "Descripcion del inmueble",
      linderos: "Linderos",
      matricula: "Matricula inmobiliaria",
      catastral: "Cedula catastral",
      nupre: "NUPRE",
      total: "Precio",
      inicial: "Pago inicial",
      saldo: "Saldo",
      numEscritura: "Numero de escritura",
      fechaOtorg: "Fecha de otorgamiento",
      tituloNum: "Titulo anterior",
      tituloFecha: "Fecha titulo anterior",
      tituloNotaria: "Notaria titulo anterior",
      phReg: "Reglamento PH",
      banco: "Banco acreedor",
      bancoNit: "NIT banco",
      apoderadoBanco: "Apoderado banco",
      poderBancoEP: "Poder banco",
      poderBancoNot: "Notaria poder banco",
      comprador: "Comprador",
      servidumbre: "Servidumbre",
    });
    state.V.forEach((party, index) => {
      const prefix = `v${index}`;
      labels[`${prefix}nombre`] = `Vendedor ${index + 1} - nombre`;
      labels[`${prefix}id`] = `Vendedor ${index + 1} - documento`;
      labels[`${prefix}ciudad`] = `Vendedor ${index + 1} - ciudad`;
      labels[`${prefix}tipoDoc`] = `Vendedor ${index + 1} - tipo documento`;
      labels[`${prefix}estado`] = `Vendedor ${index + 1} - estado civil`;
      labels[`${prefix}repr`] = `Vendedor ${index + 1} - representante`;
      labels[`${prefix}cuota`] = `Vendedor ${index + 1} - cuota`;
      labels[`${prefix}direccion`] = `Vendedor ${index + 1} - direccion`;
    });
    state.C.forEach((party, index) => {
      const prefix = `c${index}`;
      labels[`${prefix}nombre`] = `Comprador ${index + 1} - nombre`;
      labels[`${prefix}id`] = `Comprador ${index + 1} - documento`;
      labels[`${prefix}ciudad`] = `Comprador ${index + 1} - ciudad`;
      labels[`${prefix}tipoDoc`] = `Comprador ${index + 1} - tipo documento`;
      labels[`${prefix}estado`] = `Comprador ${index + 1} - estado civil`;
      labels[`${prefix}repr`] = `Comprador ${index + 1} - representante`;
      labels[`${prefix}cuota`] = `Comprador ${index + 1} - cuota`;
      labels[`${prefix}direccion`] = `Comprador ${index + 1} - direccion`;
    });
  }
  return labels;
}

function getTopBlock(editor: HTMLElement, range: Range | null) {
  if (!range) return null;
  let element = elementFromNode(range.startContainer);
  while (element && element.parentElement !== editor) {
    element = element.parentElement;
  }
  return element?.parentElement === editor ? element : null;
}

export const EscrituraRedaccionEditor = forwardRef<EscrituraEditorHandle, Props>(function EscrituraRedaccionEditor(
  {
    acto,
    state,
    sourceHtml,
    cumplimiento,
    liquidacionHtml,
    draft,
    bloqueantes,
    isSaving = false,
    isGenerating = false,
    onSaveDraft,
    onExportWord,
    onDirtyChange,
    onStatus,
    bibliotecaItems,
    bibliotecaError,
  },
  ref,
) {
  const editorRef = useRef<HTMLElement | null>(null);
  const lastRangeRef = useRef<Range | null>(null);
  const fieldValuesRef = useRef<Record<string, string[]>>({});
  const fieldMetaRef = useRef<Record<string, string>>(buildEditorLabels(acto, state));
  const fieldSeqRef = useRef(1);
  const commentsRef = useRef<RedaccionComment[]>([]);
  const dirtyRef = useRef(false);
  const trackRef = useRef(false);
  const sourceHtmlRef = useRef(sourceHtml);
  const loadedKeyRef = useRef("");
  const [linkedFields, setLinkedFields] = useState<LinkedField[]>([]);
  const [comments, setComments] = useState<RedaccionComment[]>([]);
  const [dirty, setDirtyState] = useState(false);
  const [trackEnabled, setTrackEnabledState] = useState(false);
  const [localStatus, setLocalStatus] = useState("Editor listo.");
  const fallbackBiblioteca = useMemo(() => bibliotecaRedaccionPorActo(acto), [acto]);
  const biblioteca = bibliotecaItems?.length ? bibliotecaItems : fallbackBiblioteca;

  const say = useCallback(
    (message: string) => {
      setLocalStatus(message);
      onStatus?.(message);
    },
    [onStatus],
  );

  const setDirty = useCallback(
    (next: boolean) => {
      dirtyRef.current = next;
      setDirtyState(next);
      onDirtyChange?.(next);
    },
    [onDirtyChange],
  );

  const saveSelection = useCallback(() => {
    const editor = editorRef.current;
    if (!editor) return;
    const range = getSelectionRange(editor);
    if (range) lastRangeRef.current = range.cloneRange();
  }, []);

  const restoreSelection = useCallback(() => {
    const editor = editorRef.current;
    const range = lastRangeRef.current;
    if (!editor || !range || !rangeIsInside(editor, range)) return false;
    const selection = window.getSelection();
    selection?.removeAllRanges();
    selection?.addRange(range);
    return true;
  }, []);

  const copies = useCallback((field: string) => {
    const editor = editorRef.current;
    if (!editor) return [];
    return all<HTMLElement>(editor, ".campo").filter((item) => item.dataset.field === field);
  }, []);

  const docFields = useCallback(() => {
    const editor = editorRef.current;
    if (!editor) return [];
    const seen = new Set<string>();
    const fields: string[] = [];
    all<HTMLElement>(editor, ".campo").forEach((item) => {
      const field = item.dataset.field;
      if (field && !seen.has(field)) {
        seen.add(field);
        fields.push(field);
      }
    });
    return fields;
  }, []);

  const rebuildLinkedFields = useCallback(() => {
    const fields = docFields().map((field) => {
      const value = copies(field)[0]?.textContent ?? "";
      return {
        field,
        value,
        label: fieldMetaRef.current[field] || field,
      };
    });
    setLinkedFields(fields);
  }, [copies, docFields]);

  const snapshot = useCallback(() => {
    const values: Record<string, string[]> = {};
    docFields().forEach((field) => {
      values[field] = copies(field).map((item) => item.textContent ?? "");
    });
    fieldValuesRef.current = values;
    rebuildLinkedFields();
  }, [copies, docFields, rebuildLinkedFields]);

  const resetFieldSequence = useCallback(() => {
    let max = 0;
    docFields().forEach((field) => {
      const match = /^campo(\d+)$/.exec(field);
      if (match) max = Math.max(max, Number(match[1]));
    });
    fieldSeqRef.current = max + 1;
  }, [docFields]);

  const cascade = useCallback(
    (field: string, value: string, source: HTMLElement | null = null) => {
      copies(field).forEach((item) => {
        if (item !== source) {
          item.textContent = value;
          item.classList.add("flash");
          window.setTimeout(() => item.classList.remove("flash"), 420);
        }
      });
      fieldValuesRef.current[field] = copies(field).map((item) => item.textContent ?? "");
      rebuildLinkedFields();
    },
    [copies, rebuildLinkedFields],
  );

  const detectAndCascade = useCallback(() => {
    const previous = fieldValuesRef.current;
    for (const field of docFields()) {
      const changed = copies(field).find((item, index) => (item.textContent ?? "") !== (previous[field]?.[index] ?? ""));
      if (changed) {
        cascade(field, changed.textContent ?? "", changed);
        break;
      }
    }
  }, [cascade, copies, docFields]);

  const markDirtyFromEdit = useCallback(() => {
    setDirty(true);
    saveSelection();
  }, [saveSelection, setDirty]);

  const handleEditorInput = useCallback(() => {
    if (!trackRef.current) detectAndCascade();
    else snapshot();
    markDirtyFromEdit();
  }, [detectAndCascade, markDirtyFromEdit, snapshot]);

  const syncFromForm = useCallback(
    (freshHtml: string) => {
      const editor = editorRef.current;
      if (!editor) return;
      const fresh = document.createElement("div");
      fresh.innerHTML = freshHtml;
      const fields = new Set<string>();
      all<HTMLElement>(fresh, ".campo").forEach((item) => {
        const field = item.dataset.field;
        if (field) fields.add(field);
      });
      fields.forEach((field) => {
        const nextValues = all<HTMLElement>(fresh, ".campo")
          .filter((item) => item.dataset.field === field)
          .map((item) => item.textContent ?? "");
        const live = copies(field);
        live.forEach((item, index) => {
          const next = nextValues[Math.min(index, nextValues.length - 1)];
          if (next != null && (item.textContent ?? "") !== next) {
            item.textContent = next;
            item.classList.add("flash");
            window.setTimeout(() => item.classList.remove("flash"), 420);
          }
        });
      });
      snapshot();
    },
    [copies, snapshot],
  );

  useEffect(() => {
    fieldMetaRef.current = { ...fieldMetaRef.current, ...buildEditorLabels(acto, state) };
    rebuildLinkedFields();
  }, [acto, rebuildLinkedFields, state]);

  useEffect(() => {
    const editor = editorRef.current;
    if (!editor) return;
    const loadKey = draft?.acto === acto && draft.html.trim() ? `${acto}:${draft.updated_at}:${draft.html.length}` : `${acto}:fresh`;
    if (loadedKeyRef.current === loadKey) return;
    loadedKeyRef.current = loadKey;
    fieldMetaRef.current = buildEditorLabels(acto, state);
    const restored = draft?.acto === acto && draft.html.trim() ? draft.html : buildEditableHtml(sourceHtml);
    editor.innerHTML = restored;
    commentsRef.current = draft?.acto === acto ? draft.comments : [];
    setComments(commentsRef.current);
    resetFieldSequence();
    snapshot();
    sourceHtmlRef.current = sourceHtml;
    setDirty(false);
    say(draft?.acto === acto && draft.html.trim() ? "Borrador de redaccion recuperado." : "Redaccion inicializada desde captura.");
  }, [acto, draft, resetFieldSequence, say, setDirty, snapshot, sourceHtml, state]);

  useEffect(() => {
    if (sourceHtmlRef.current === sourceHtml) return;
    sourceHtmlRef.current = sourceHtml;
    syncFromForm(buildEditableHtml(sourceHtml));
  }, [sourceHtml, syncFromForm]);

  useEffect(() => {
    const editor = editorRef.current;
    if (!editor) return undefined;
    editor.addEventListener("input", handleEditorInput);
    return () => editor.removeEventListener("input", handleEditorInput);
  }, [handleEditorInput]);

  useEffect(() => {
    const editor = editorRef.current;
    if (!editor) return undefined;
    const handleBeforeInput = (event: InputEvent) => {
      if (!trackRef.current) return;
      const inputType = event.inputType || "";
      if (inputType.startsWith("insert")) {
        const dataTransfer = (event as InputEvent & { dataTransfer?: DataTransfer | null }).dataTransfer;
        const value = event.data ?? dataTransfer?.getData("text/plain") ?? "";
        if (!value) return;
        event.preventDefault();
        insertTracked(value);
      } else if (inputType.startsWith("delete")) {
        event.preventDefault();
        deleteTracked(inputType.includes("Forward"));
      }
    };
    editor.addEventListener("beforeinput", handleBeforeInput);
    return () => editor.removeEventListener("beforeinput", handleBeforeInput);
  });

  useImperativeHandle(
    ref,
    () => ({
      getDraft: () => ({
        acto,
        html: editorRef.current?.innerHTML ?? "",
        comments: commentsRef.current,
        updated_at: new Date().toISOString(),
      }),
      getHtmlForExport: () => materializeFillLeaders(editorRef.current?.innerHTML ?? ""),
      isDirty: () => dirtyRef.current,
      markClean: () => setDirty(false),
    }),
    [acto, setDirty],
  );

  function currentRange() {
    const editor = editorRef.current;
    if (!editor) return null;
    restoreSelection();
    return getSelectionRange(editor);
  }

  function runCommand(command: "bold" | "italic" | "underline" | "strikeThrough") {
    restoreSelection();
    document.execCommand(command, false);
    snapshot();
    setDirty(true);
    say("Formato aplicado.");
  }

  function vincular() {
    const editor = editorRef.current;
    const range = currentRange();
    if (!editor || !range || range.collapsed) {
      say("Selecciona texto para vincular.");
      return;
    }
    if (range.cloneContents().querySelector(".campo")) {
      say("La seleccion ya contiene un campo vinculado.");
      return;
    }
    const id = `campo${fieldSeqRef.current++}`;
    const span = document.createElement("span");
    span.className = "campo";
    span.dataset.field = id;
    try {
      span.appendChild(range.extractContents());
      range.insertNode(span);
      fieldMetaRef.current[id] = `Vinculado ${id.replace("campo", "")}`;
      placeCaretAtEnd(span);
      saveSelection();
      snapshot();
      setDirty(true);
      say("Campo vinculado.");
    } catch {
      say("No fue posible vincular esa seleccion.");
    }
  }

  function desvincular() {
    const range = currentRange();
    const element = elementFromNode(range?.startContainer ?? null)?.closest(".campo") as HTMLElement | null;
    if (!element) {
      say("Ubica el cursor dentro de un campo vinculado.");
      return;
    }
    const textNode = document.createTextNode(element.textContent ?? "");
    element.replaceWith(textNode);
    snapshot();
    setDirty(true);
    say("Campo desvinculado.");
  }

  function applyHighlight(color: string | null) {
    const range = currentRange();
    if (!range || range.collapsed) {
      say("Selecciona texto para resaltar.");
      return;
    }
    if (!color) {
      const editor = editorRef.current;
      if (!editor) return;
      all<HTMLElement>(editor, ".mark, .hl").forEach((item) => {
        if (range.intersectsNode(item)) unwrapWithChildren(item);
      });
      snapshot();
      setDirty(true);
      say("Resaltado removido.");
      return;
    }
    const span = document.createElement("span");
    span.className = "mark hl";
    span.style.background = color;
    try {
      span.appendChild(range.extractContents());
      range.insertNode(span);
      placeCaretAtEnd(span);
      saveSelection();
      snapshot();
      setDirty(true);
      say("Resaltado aplicado.");
    } catch {
      say("No fue posible resaltar esa seleccion.");
    }
  }

  function comentar() {
    const range = currentRange();
    if (!range || range.collapsed) {
      say("Selecciona texto para comentar.");
      return;
    }
    const id = `c${Date.now().toString(36)}${commentsRef.current.length}`;
    const span = document.createElement("span");
    span.className = "cmt";
    span.dataset.cmt = id;
    try {
      span.appendChild(range.extractContents());
      range.insertNode(span);
      placeCaretAtEnd(span);
      saveSelection();
      const next = [...commentsRef.current, { id, quote: selectedQuote(range) || span.textContent || "Seleccion", text: "", resolved: false }];
      commentsRef.current = next;
      setComments(next);
      setDirty(true);
      say("Comentario anclado.");
    } catch {
      say("No fue posible anclar el comentario.");
    }
  }

  function updateComment(id: string, patch: Partial<RedaccionComment>) {
    const next = commentsRef.current.map((item) => (item.id === id ? { ...item, ...patch } : item));
    commentsRef.current = next;
    setComments(next);
    setDirty(true);
  }

  function removeComment(id: string) {
    const editor = editorRef.current;
    const anchor = editor?.querySelector<HTMLElement>(`.cmt[data-cmt="${id}"]`);
    if (anchor) unwrapWithChildren(anchor);
    const next = commentsRef.current.filter((item) => item.id !== id);
    commentsRef.current = next;
    setComments(next);
    setDirty(true);
    say("Comentario eliminado.");
  }

  function focusComment(id: string) {
    const editor = editorRef.current;
    const anchor = editor?.querySelector<HTMLElement>(`.cmt[data-cmt="${id}"]`);
    if (!anchor) return;
    anchor.scrollIntoView({ block: "center" });
    const range = document.createRange();
    range.selectNodeContents(anchor);
    const selection = window.getSelection();
    selection?.removeAllRanges();
    selection?.addRange(range);
    anchor.classList.add("sel");
    window.setTimeout(() => anchor.classList.remove("sel"), 900);
    saveSelection();
  }

  function insertBiblioteca(html: string) {
    const editor = editorRef.current;
    if (!editor) return;
    restoreSelection();
    const range = getSelectionRange(editor);
    const block = getTopBlock(editor, range);
    const fragment = createFragment(html);
    const first = fragment.firstElementChild as HTMLElement | null;
    if (block?.parentNode) block.parentNode.insertBefore(fragment, block.nextSibling);
    else editor.appendChild(fragment);
    if (first) placeCaretAtEnd(first);
    saveSelection();
    resetFieldSequence();
    snapshot();
    setDirty(true);
    say("Clausula insertada.");
  }

  function setTrack(next: boolean) {
    trackRef.current = next;
    setTrackEnabledState(next);
    say(next ? "Control de cambios activo." : "Control de cambios inactivo.");
  }

  function insertTracked(value: string) {
    const range = currentRange();
    if (!range) return;
    if (!range.collapsed) deleteTracked(false);
    const latest = currentRange();
    if (!latest) return;
    const ins = document.createElement("ins");
    ins.className = "track";
    ins.textContent = value;
    latest.insertNode(ins);
    placeCaretAtEnd(ins);
    snapshot();
    setDirty(true);
  }

  function deleteTracked(forward: boolean) {
    const editor = editorRef.current;
    restoreSelection();
    const selection = window.getSelection();
    if (!editor || !selection || selection.rangeCount === 0) return;
    let range = selection.getRangeAt(0);
    if (!rangeIsInside(editor, range)) return;
    if (range.collapsed) {
      const selectionWithModify = selection as Selection & {
        modify?: (alter: "extend", direction: "forward" | "backward", granularity: "character") => void;
      };
      selectionWithModify.modify?.("extend", forward ? "forward" : "backward", "character");
      if (selection.rangeCount === 0 || selection.isCollapsed) return;
      range = selection.getRangeAt(0);
    }
    const fragment = range.extractContents();
    const onlyInserted = Array.from(fragment.childNodes).every(
      (node) => node.nodeType === Node.ELEMENT_NODE && (node as Element).matches("ins.track"),
    );
    if (!onlyInserted) {
      const del = document.createElement("del");
      del.className = "track";
      del.appendChild(fragment);
      range.insertNode(del);
      placeCaretAtEnd(del);
    }
    saveSelection();
    snapshot();
    setDirty(true);
  }

  function acceptChanges() {
    const editor = editorRef.current;
    if (!editor) return;
    all<HTMLElement>(editor, "ins.track").forEach(unwrapWithChildren);
    all<HTMLElement>(editor, "del.track").forEach((item) => item.remove());
    snapshot();
    setDirty(true);
    say("Cambios aceptados.");
  }

  function rejectChanges() {
    const editor = editorRef.current;
    if (!editor) return;
    all<HTMLElement>(editor, "ins.track").forEach((item) => item.remove());
    all<HTMLElement>(editor, "del.track").forEach(unwrapWithChildren);
    snapshot();
    setDirty(true);
    say("Cambios rechazados.");
  }

  async function saveDraft() {
    try {
      await onSaveDraft({
        acto,
        html: editorRef.current?.innerHTML ?? "",
        comments: commentsRef.current,
        updated_at: new Date().toISOString(),
      });
      setDirty(false);
    } catch {
      // The workspace owns the visible API error; keep the editor marked dirty.
    }
  }

  async function exportWord() {
    await onExportWord(materializeFillLeaders(editorRef.current?.innerHTML ?? ""));
  }

  function exportPdf() {
    const html = materializeFillLeaders(editorRef.current?.innerHTML ?? "");
    const printWindow = window.open("", "_blank", "noopener,noreferrer");
    if (!printWindow) {
      say("El navegador bloqueo la ventana de impresion.");
      return;
    }
    printWindow.document.write(`<!doctype html><html><head><title>Escritura</title><style>${PRINT_CSS}</style></head><body><article class="sheet">${html}</article><script>window.print();</script></body></html>`);
    printWindow.document.close();
    say("Vista de impresion abierta.");
  }

  return (
    <div className="grid min-w-0 gap-5 xl:grid-cols-[minmax(0,1fr)_340px]">
      <main className="min-w-0 space-y-4">
        <div
          className="rounded-xl border border-line-strong bg-white p-3 shadow-sm"
          onMouseDown={(event) => {
            if (event.target instanceof HTMLElement && event.target.closest("button")) event.preventDefault();
          }}
        >
          <div className="flex flex-wrap items-center gap-2">
            <ToolbarButton label="Negrita" data-cmd="bold" onClick={() => runCommand("bold")}>
              <Bold className="h-4 w-4" aria-hidden="true" />
            </ToolbarButton>
            <ToolbarButton label="Cursiva" data-cmd="italic" onClick={() => runCommand("italic")}>
              <Italic className="h-4 w-4" aria-hidden="true" />
            </ToolbarButton>
            <ToolbarButton label="Subrayado" data-cmd="underline" onClick={() => runCommand("underline")}>
              <Underline className="h-4 w-4" aria-hidden="true" />
            </ToolbarButton>
            <ToolbarButton label="Tachado" data-cmd="strikeThrough" onClick={() => runCommand("strikeThrough")}>
              <Strikethrough className="h-4 w-4" aria-hidden="true" />
            </ToolbarButton>
            <span className="mx-1 h-8 w-px bg-line-strong" aria-hidden="true" />
            <ToolbarButton label="Vincular seleccion" data-act="vincular" onClick={vincular}>
              <Link2 className="h-4 w-4" aria-hidden="true" />
            </ToolbarButton>
            <ToolbarButton label="Desvincular campo" data-act="desvincular" onClick={desvincular}>
              <Link2Off className="h-4 w-4" aria-hidden="true" />
            </ToolbarButton>
            <ToolbarButton label="Comentar seleccion" data-act="comentar" onClick={comentar}>
              <MessageSquare className="h-4 w-4" aria-hidden="true" />
            </ToolbarButton>
            <ToolbarButton label={trackEnabled ? "Desactivar control de cambios" : "Activar control de cambios"} data-act="track" active={trackEnabled} onClick={() => setTrack(!trackEnabled)}>
              <Highlighter className="h-4 w-4" aria-hidden="true" />
            </ToolbarButton>
            <ToolbarButton label="Aceptar cambios" data-act="accept" onClick={acceptChanges}>
              <CheckCheck className="h-4 w-4" aria-hidden="true" />
            </ToolbarButton>
            <ToolbarButton label="Rechazar cambios" data-act="reject" onClick={rejectChanges}>
              <X className="h-4 w-4" aria-hidden="true" />
            </ToolbarButton>
            <span className="mx-1 h-8 w-px bg-line-strong" aria-hidden="true" />
            <div className="flex items-center gap-1" aria-label="Resaltado">
              {HIGHLIGHTS.map((item) => (
                <button
                  key={item.value}
                  type="button"
                  data-hl={item.value}
                  title={item.label}
                  aria-label={`Resaltar ${item.label}`}
                  onClick={() => applyHighlight(item.value)}
                  className="hl-sw h-8 w-8 rounded-full border border-line-strong shadow-sm"
                  style={{ background: item.value }}
                />
              ))}
              <button
                type="button"
                data-hl="none"
                title="Quitar resaltado"
                aria-label="Quitar resaltado"
                onClick={() => applyHighlight(null)}
                className="hl-sw inline-flex h-8 w-8 items-center justify-center rounded-full border border-line-strong bg-white text-secondary"
              >
                <Eraser className="h-4 w-4" aria-hidden="true" />
              </button>
            </div>
            <span className="mx-1 h-8 w-px bg-line-strong" aria-hidden="true" />
            <ToolbarButton label="Guardar borrador" onClick={saveDraft} disabled={isSaving}>
              <Save className="h-4 w-4" aria-hidden="true" />
            </ToolbarButton>
            <ToolbarButton label="Exportar Word" onClick={exportWord} disabled={isGenerating}>
              <FileDown className="h-4 w-4" aria-hidden="true" />
            </ToolbarButton>
            <ToolbarButton label="Exportar PDF" onClick={exportPdf}>
              <Printer className="h-4 w-4" aria-hidden="true" />
            </ToolbarButton>
          </div>
          <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-secondary">
            <span>{localStatus}</span>
            {dirty ? <span className="rounded-full bg-amber-50 px-2 py-0.5 font-semibold text-amber-700">Borrador sin guardar</span> : null}
            {bloqueantes > 0 ? <span className="rounded-full bg-red-50 px-2 py-0.5 font-semibold text-red-700">Exportacion Word bloqueada</span> : null}
          </div>
        </div>
        <div className={styles.previewShell}>
          <article
            ref={editorRef}
            className={`${styles.sheet} ${styles.editorSheet}`}
            contentEditable
            suppressContentEditableWarning
            spellCheck={false}
            aria-label="Editor de redaccion"
            onBlur={saveSelection}
            onKeyUp={saveSelection}
            onMouseUp={saveSelection}
          />
        </div>
      </main>
      <aside className="space-y-5 xl:sticky xl:top-4 xl:max-h-[calc(100vh-2rem)] xl:overflow-auto">
        <Panel title="Biblioteca">
          <div className="space-y-2" onMouseDown={(event) => event.preventDefault()}>
            {bibliotecaError ? <p className="rounded-lg bg-amber-50 px-3 py-2 text-xs font-semibold text-amber-700">Biblioteca local: {bibliotecaError}</p> : null}
            {biblioteca.map((item) => (
              <button
                key={item.titulo}
                type="button"
                onClick={() => insertBiblioteca(item.html)}
                className="w-full rounded-lg border border-line bg-white px-3 py-2 text-left shadow-sm hover:border-primary hover:bg-primary/5"
              >
                <span className="block text-sm font-semibold text-primary">{item.titulo}</span>
                <span className="mt-1 block text-xs leading-5 text-secondary">{item.detalle}</span>
              </button>
            ))}
          </div>
        </Panel>
        <Panel title="Campos vinculados">
          {linkedFields.length ? (
            <div className="space-y-3">
              {linkedFields.map((item) => (
                <label key={item.field} className="block">
                  <span className="mb-1 block text-xs font-semibold uppercase tracking-[0.08em] text-secondary">{item.label}</span>
                  <input
                    value={item.value}
                    onMouseDown={(event) => event.stopPropagation()}
                    onChange={(event) => {
                      cascade(item.field, event.target.value);
                      setDirty(true);
                    }}
                    className="w-full rounded-lg border border-line-strong bg-white px-3 py-2 text-sm text-primary outline-none focus:border-primary focus:ring-2 focus:ring-primary/15"
                  />
                </label>
              ))}
            </div>
          ) : (
            <p className="text-sm leading-6 text-secondary">No hay campos vinculados en el documento.</p>
          )}
        </Panel>
        <Panel title="Comentarios" id="comentarios">
          {comments.length ? (
            <div className="space-y-3">
              {comments.map((item) => (
                <div key={item.id} className={`rounded-lg border p-3 ${item.resolved ? "border-emerald-200 bg-emerald-50" : "border-line bg-white"}`}>
                  <button type="button" onMouseDown={(event) => event.preventDefault()} onClick={() => focusComment(item.id)} className="block text-left text-xs font-semibold text-primary">
                    {item.quote}
                  </button>
                  <textarea
                    value={item.text}
                    onChange={(event) => updateComment(item.id, { text: event.target.value })}
                    placeholder="Comentario"
                    className="mt-2 min-h-20 w-full rounded-lg border border-line-strong bg-white px-3 py-2 text-sm text-primary outline-none focus:border-primary focus:ring-2 focus:ring-primary/15"
                  />
                  <div className="mt-2 flex flex-wrap gap-2">
                    <button type="button" onMouseDown={(event) => event.preventDefault()} onClick={() => updateComment(item.id, { resolved: !item.resolved })} className="rounded-lg border border-line-strong px-2.5 py-1 text-xs font-semibold text-secondary hover:bg-slate-50">
                      {item.resolved ? "Reabrir" : "Resolver"}
                    </button>
                    <button type="button" onMouseDown={(event) => event.preventDefault()} onClick={() => removeComment(item.id)} className="rounded-lg border border-red-200 px-2.5 py-1 text-xs font-semibold text-red-700 hover:bg-red-50">
                      Eliminar
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm leading-6 text-secondary">Selecciona texto y usa comentar para anclar una nota.</p>
          )}
        </Panel>
        <CumplimientoPanel cumplimiento={cumplimiento} />
        <LiquidacionPanel html={liquidacionHtml} />
      </aside>
    </div>
  );
});

function ToolbarButton({
  label,
  active,
  disabled,
  children,
  onClick,
  ...attrs
}: {
  label: string;
  active?: boolean;
  disabled?: boolean;
  children: ReactNode;
  onClick: () => void | Promise<void>;
} & Record<`data-${string}`, string | undefined>) {
  return (
    <button
      {...attrs}
      type="button"
      title={label}
      aria-label={label}
      aria-pressed={active}
      disabled={disabled}
      onClick={() => {
        void onClick();
      }}
      className={`inline-flex h-9 min-w-9 items-center justify-center rounded-lg border px-2.5 text-sm font-semibold shadow-sm transition disabled:cursor-not-allowed disabled:opacity-50 ${
        active ? "border-primary bg-primary text-white" : "border-line-strong bg-white text-primary hover:bg-slate-50"
      }`}
    >
      {children}
    </button>
  );
}

function Panel({ title, id, children }: { title: string; id?: string; children: ReactNode }) {
  return (
    <section id={id} className="rounded-xl border border-line-strong bg-white p-4 shadow-sm">
      <h2 className="mb-3 font-serif text-lg font-semibold text-primary">{title}</h2>
      {children}
    </section>
  );
}
