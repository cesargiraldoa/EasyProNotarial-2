"use client";

import Link from "next/link";
import { Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { getNotaries, type NotaryRecord } from "@/lib/api";

const PAGE_SIZE = 20;

function normalizeText(value: string | null | undefined): string {
  return (value ?? "").trim().toLowerCase();
}

export function NotariesCatalog() {
  const [notaries, setNotaries] = useState<NotaryRecord[]>([]);
  const [query, setQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function loadNotaries() {
      setIsLoading(true);
      setError(null);
      try {
        const data = await getNotaries();
        if (!isMounted) {
          return;
        }
        setNotaries(data);
      } catch (loadError) {
        if (!isMounted) {
          return;
        }
        setError(loadError instanceof Error ? loadError.message : "No fue posible cargar el catálogo de notarías.");
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void loadNotaries();

    return () => {
      isMounted = false;
    };
  }, []);

  const filteredNotaries = useMemo(() => {
    const search = normalizeText(query);
    if (!search) {
      return notaries;
    }

    return notaries.filter((notary) => {
      const label = normalizeText(notary.notary_label);
      const municipality = normalizeText(notary.municipality);
      const holder = normalizeText(notary.current_notary_name);
      return label.includes(search) || municipality.includes(search) || holder.includes(search);
    });
  }, [notaries, query]);

  const totalPages = Math.max(1, Math.ceil(filteredNotaries.length / PAGE_SIZE));

  useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(totalPages);
    }
  }, [currentPage, totalPages]);

  useEffect(() => {
    setCurrentPage(1);
  }, [query]);

  const paginatedNotaries = useMemo(() => {
    const start = (currentPage - 1) * PAGE_SIZE;
    return filteredNotaries.slice(start, start + PAGE_SIZE);
  }, [currentPage, filteredNotaries]);

  const departmentsCount = useMemo(() => new Set(notaries.map((item) => normalizeText(item.department)).filter(Boolean)).size, [notaries]);

  const withAssignedUsersCount = useMemo(
    () => notaries.filter((item) => item.commercial_owner_user_id !== null).length,
    [notaries]
  );

  return (
    <div className="space-y-6">
      <section className="ep-card rounded-[2rem] p-6">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <h1 className="text-3xl font-semibold tracking-[-0.05em] text-primary sm:text-4xl">Notarías</h1>
            <p className="mt-3 text-base text-secondary">Catálogo operativo de notarías registradas en el sistema</p>
          </div>

          <div className="w-full max-w-xl">
            <label htmlFor="notaries-search" className="mb-2 block text-sm font-medium text-primary">
              Buscar por nombre, municipio o notario titular
            </label>
            <div className="ep-input flex h-12 items-center gap-3 rounded-2xl px-4">
              <Search className="h-4 w-4 text-secondary" />
              <input
                id="notaries-search"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Ej. Notaría 12, Medellín, Juan Pérez"
                className="h-full w-full bg-transparent text-sm text-primary placeholder:text-secondary/70 focus:outline-none"
              />
            </div>
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Total notarías</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{notaries.length}</p>
          </div>
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Departamentos</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{departmentsCount}</p>
          </div>
          <div className="ep-card-muted rounded-[1.5rem] p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-secondary">Con usuarios asignados</p>
            <p className="mt-3 text-3xl font-semibold text-primary">{withAssignedUsersCount}</p>
          </div>
        </div>
      </section>

      <section className="ep-card rounded-[2rem] p-6">
        {error ? <div className="ep-kpi-critical rounded-2xl px-4 py-3 text-sm">{error}</div> : null}

        <div className="mt-2 overflow-x-auto">
          <table className="min-w-full border-separate border-spacing-0">
            <thead>
              <tr className="text-left text-xs uppercase tracking-[0.16em] text-secondary">
                <th className="border-b border-white/10 px-4 py-3 font-semibold">Notaría</th>
                <th className="border-b border-white/10 px-4 py-3 font-semibold">Municipio</th>
                <th className="border-b border-white/10 px-4 py-3 font-semibold">Departamento</th>
                <th className="border-b border-white/10 px-4 py-3 font-semibold">Notario titular</th>
                <th className="border-b border-white/10 px-4 py-3 font-semibold">Teléfono</th>
                <th className="border-b border-white/10 px-4 py-3 font-semibold">Email</th>
                <th className="border-b border-white/10 px-4 py-3 font-semibold">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="px-4 py-6 text-sm text-secondary">
                    Cargando catálogo...
                  </td>
                </tr>
              ) : null}

              {!isLoading && paginatedNotaries.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-6 text-sm text-secondary">
                    No hay notarías para el criterio de búsqueda ingresado.
                  </td>
                </tr>
              ) : null}

              {!isLoading
                ? paginatedNotaries.map((notary) => (
                    <tr key={notary.id} className="text-sm text-primary">
                      <td className="border-b border-white/5 px-4 py-4 font-medium">{notary.notary_label || "—"}</td>
                      <td className="border-b border-white/5 px-4 py-4 text-secondary">{notary.municipality || "—"}</td>
                      <td className="border-b border-white/5 px-4 py-4 text-secondary">{notary.department || "—"}</td>
                      <td className="border-b border-white/5 px-4 py-4 text-secondary">{notary.current_notary_name || "—"}</td>
                      <td className="border-b border-white/5 px-4 py-4 text-secondary">{notary.phone || "—"}</td>
                      <td className="border-b border-white/5 px-4 py-4 text-secondary">{notary.email || "—"}</td>
                      <td className="border-b border-white/5 px-4 py-4">
                        <Link
                          href={`/dashboard/notarias/${notary.id}`}
                          className="inline-flex items-center rounded-xl border border-primary/20 px-3 py-2 text-xs font-semibold text-primary transition hover:border-primary/40 hover:bg-primary/5"
                        >
                          Ver detalle
                        </Link>
                      </td>
                    </tr>
                  ))
                : null}
            </tbody>
          </table>
        </div>

        <div className="mt-5 flex flex-col gap-3 border-t border-white/10 pt-4 text-sm text-secondary sm:flex-row sm:items-center sm:justify-between">
          <p>
            Mostrando {paginatedNotaries.length} de {filteredNotaries.length} resultados · Página {currentPage} de {totalPages}
          </p>
          <div className="flex items-center gap-2">
            <div
              onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}
              className={`inline-flex select-none items-center rounded-xl px-3 py-2 font-semibold ${
                currentPage === 1
                  ? "cursor-not-allowed border border-white/10 text-secondary/50"
                  : "cursor-pointer border border-primary/20 text-primary hover:border-primary/40 hover:bg-primary/5"
              }`}
            >
              Anterior
            </div>
            <div
              onClick={() => setCurrentPage((page) => Math.min(totalPages, page + 1))}
              className={`inline-flex select-none items-center rounded-xl px-3 py-2 font-semibold ${
                currentPage >= totalPages
                  ? "cursor-not-allowed border border-white/10 text-secondary/50"
                  : "cursor-pointer border border-primary/20 text-primary hover:border-primary/40 hover:bg-primary/5"
              }`}
            >
              Siguiente
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
