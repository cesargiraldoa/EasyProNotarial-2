"use client";

import { useEffect, useState } from "react";
import { BadgeCheck, Building2, Mail, ShieldCheck, UserRound } from "lucide-react";
import { getCurrentUser, type CurrentUser } from "@/lib/api";

export function UserProfileWorkspace() {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getCurrentUser()
      .then((response) => {
        if (!cancelled) {
          setUser(response);
        }
      })
      .catch((loadError) => {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "No fue posible cargar el perfil.");
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) {
    return <div className="ep-kpi-critical rounded-[2rem] px-6 py-5 text-sm">{error}</div>;
  }

  if (!user) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">Cargando perfil...</div>;
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1.05fr)_360px]">
      <section className="ep-card rounded-[2rem] p-6 sm:p-7">
        <p className="text-xs uppercase tracking-[0.2em] text-secondary">Perfil</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-[-0.05em] text-primary">{user.full_name}</h1>
        <p className="mt-3 max-w-2xl text-base leading-7 text-secondary">Perfil base de operación para validar sesión, roles activos y contexto notarial dentro de EasyPro 2.</p>

        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <div className="ep-card-muted rounded-[1.5rem] p-5">
            <div className="flex items-center gap-3">
              <div className="rounded-2xl bg-primary/10 p-3"><Mail className="h-5 w-5 text-primary" /></div>
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-secondary">Correo</p>
                <p className="mt-1 text-sm font-semibold text-primary">{user.email}</p>
              </div>
            </div>
          </div>
          <div className="ep-card-muted rounded-[1.5rem] p-5">
            <div className="flex items-center gap-3">
              <div className="rounded-2xl bg-primary/10 p-3"><BadgeCheck className="h-5 w-5 text-primary" /></div>
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-secondary">Estado</p>
                <p className="mt-1 text-sm font-semibold text-primary">{user.is_active ? "Activo" : "Inactivo"}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="ep-filter-panel mt-6 rounded-[1.7rem] p-5">
          <p className="text-sm font-semibold text-primary">Roles vigentes</p>
          <div className="mt-4 flex flex-wrap gap-2">
            {user.roles.map((role) => (
              <span key={role} className="ep-badge rounded-full px-3 py-2 text-xs font-semibold text-primary">{role}</span>
            ))}
          </div>
        </div>
      </section>

      <aside className="space-y-6">
        <section className="ep-card rounded-[2rem] p-6">
          <div className="flex items-center gap-3">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary text-lg font-semibold text-white">
              {user.full_name.split(" ").slice(0, 2).map((item) => item[0]).join("").toUpperCase()}
            </div>
            <div>
              <p className="text-lg font-semibold text-primary">{user.full_name}</p>
              <p className="text-sm text-secondary">Sesión autenticada</p>
            </div>
          </div>
          <div className="mt-5 space-y-3">
            {user.assignments.length === 0 ? (
              <div className="ep-card-muted rounded-2xl px-4 py-3 text-sm text-secondary">Sin asignaciones específicas registradas.</div>
            ) : (
              user.assignments.map((assignment) => (
                <div key={assignment.id} className="ep-card-muted rounded-2xl px-4 py-3">
                  <p className="text-sm font-semibold text-primary">{assignment.role_name}</p>
                  <p className="mt-1 text-sm text-secondary">{assignment.notary_label || "Ámbito global"}</p>
                </div>
              ))
            )}
          </div>
        </section>

        <section className="ep-card rounded-[2rem] p-6">
          <p className="text-xs uppercase tracking-[0.2em] text-secondary">Contexto operativo</p>
          <div className="mt-4 space-y-3">
            <div className="flex items-start gap-3 ep-card-muted rounded-2xl px-4 py-3 text-sm text-primary"><UserRound className="mt-0.5 h-4 w-4 text-primary" />Responsable actual del entorno autenticado.</div>
            <div className="flex items-start gap-3 ep-card-muted rounded-2xl px-4 py-3 text-sm text-primary"><Building2 className="mt-0.5 h-4 w-4 text-primary" />Notaría por defecto: {user.default_notary || "No asignada"}</div>
            <div className="flex items-start gap-3 ep-card-muted rounded-2xl px-4 py-3 text-sm text-primary"><ShieldCheck className="mt-0.5 h-4 w-4 text-primary" />Permisos funcionales cargados desde backend.</div>
          </div>
        </section>
      </aside>
    </div>
  );
}
