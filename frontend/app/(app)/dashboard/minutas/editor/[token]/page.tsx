"use client";

import { use, useEffect, useState } from "react";
import { getMinutaOnlyOfficeConfig } from "@/lib/minuta";

declare global {
  interface Window {
    DocsAPI?: {
      DocEditor: new (
        elementId: string,
        config: Record<string, unknown>,
      ) => { destroyEditor?: () => void };
    };
  }
}

type EditorPageProps = {
  params: Promise<{ token: string }>;
};

export default function MinutaEditorPage({ params }: EditorPageProps) {
  const { token } = use(params);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    let editorInstance: { destroyEditor?: () => void } | null = null;

    const loadEditor = async () => {
      const docServer = (process.env.NEXT_PUBLIC_ONLYOFFICE_DOCS_URL ?? "").replace(/\/$/, "");

      if (!docServer) {
        if (mounted) {
          setError("Falta NEXT_PUBLIC_ONLYOFFICE_DOCS_URL. Configurala para abrir el editor.");
          setIsLoading(false);
        }
        return;
      }

      try {
        const config = await getMinutaOnlyOfficeConfig(token);

        await new Promise<void>((resolve, reject) => {
          const existing = document.querySelector<HTMLScriptElement>(
            'script[data-onlyoffice="api"]',
          );
          if (existing) {
            if (window.DocsAPI?.DocEditor) {
              resolve();
            } else {
              existing.addEventListener("load", () => resolve(), { once: true });
              existing.addEventListener(
                "error",
                () => reject(new Error("No fue posible cargar el script de OnlyOffice.")),
                { once: true },
              );
            }
            return;
          }

          const script = document.createElement("script");
          script.src = `${docServer}/web-apps/apps/api/documents/api.js`;
          script.async = true;
          script.dataset.onlyoffice = "api";
          script.onload = () => resolve();
          script.onerror = () =>
            reject(new Error("No fue posible cargar el script de OnlyOffice."));
          document.body.appendChild(script);
        });

        if (!window.DocsAPI?.DocEditor) {
          throw new Error("OnlyOffice no esta disponible despues de cargar el script.");
        }

        editorInstance = new window.DocsAPI.DocEditor("onlyoffice-editor", config);

        if (mounted) {
          setError(null);
          setIsLoading(false);
        }
      } catch (issue) {
        if (mounted) {
          setError(
            issue instanceof Error
              ? issue.message
              : "No fue posible cargar el editor de la minuta.",
          );
          setIsLoading(false);
        }
      }
    };

    void loadEditor();

    return () => {
      mounted = false;
      editorInstance?.destroyEditor?.();
    };
  }, [token]);

  return (
    <main className="h-screen w-screen bg-white">
      {error ? (
        <div className="flex h-full items-center justify-center p-6 text-center text-sm text-red-600">
          {error}
        </div>
      ) : (
        <>
          {isLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-white text-sm text-slate-700">
              Cargando editor...
            </div>
          )}
          <div id="onlyoffice-editor" className="h-full w-full" />
        </>
      )}
    </main>
  );
}