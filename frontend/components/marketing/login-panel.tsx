"use client";

import Image from "next/image";
import { FormEvent, useState } from "react";
import { ArrowRight } from "lucide-react";
import { defaultBranding } from "@/lib/branding";
import { completeLogin, login } from "@/lib/api";
import { LogoBadge } from "@/components/ui/logo-badge";

function resolveAppOrigin() {
  if (typeof window === "undefined") {
    return "http://127.0.0.1:5179";
  }
  return window.location.origin;
}

export function LoginPanel() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [rememberSession, setRememberSession] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    const formData = new FormData(event.currentTarget);
    const email = String(formData.get("email") ?? "");
    const password = String(formData.get("password") ?? "");
    const nextPath = typeof window !== "undefined" ? new URLSearchParams(window.location.search).get("next") : null;

    try {
      const payload = await login({ email, password });
      completeLogin(payload.access_token, rememberSession);
      window.location.assign(`${resolveAppOrigin()}${nextPath ?? "/dashboard"}`);
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : "No fue posible iniciar sesión.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="ep-login-shell min-h-screen px-5 py-6 text-ink lg:px-8 lg:py-8">
      <div className="mx-auto grid min-h-[calc(100vh-3rem)] max-w-7xl overflow-hidden rounded-[2rem] border border-line ep-card lg:grid-cols-[1.05fr_0.95fr]">
        <section className="relative hidden overflow-hidden lg:block">
          <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(13,46,93,0.16))]" />
          <Image src="/login-cafetero.png" alt="Paisaje cafetero premium para acceso EasyPro 2" fill priority className="object-cover object-center" sizes="50vw" />
        </section>

        <section className="flex items-center justify-center px-5 py-8 sm:px-8 lg:px-10 lg:py-10">
          <div className="w-full max-w-md space-y-8">
            <div className="space-y-5">
              <div className="flex items-center gap-4">
                <LogoBadge initials={defaultBranding.logoInitials} compact />
                <div>
                  <p className="text-sm font-semibold uppercase tracking-[0.24em] text-primary/70">{defaultBranding.commercialName}</p>
                  <p className="text-xs text-secondary">{defaultBranding.legalName}</p>
                </div>
              </div>
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-accent">Acceso</p>
                <h1 className="mt-3 text-4xl font-semibold tracking-[-0.05em] text-primary">Inicia sesión</h1>
              </div>
            </div>

            <form onSubmit={onSubmit} className="ep-filter-panel space-y-5 rounded-[2rem] p-6 sm:p-7">
              <label className="grid gap-2 text-sm font-medium text-primary">Usuario<input name="email" type="email" defaultValue="superadmin@easypro.co" className="ep-input h-14 rounded-2xl px-4 text-base" /></label>
              <label className="grid gap-2 text-sm font-medium text-primary">Contraseña<input name="password" type="password" defaultValue="ChangeMe123!" className="ep-input h-14 rounded-2xl px-4 text-base" /></label>
              <label className="ep-card flex items-center gap-3 rounded-2xl px-4 py-3 text-sm text-secondary"><input type="checkbox" checked={rememberSession} onChange={(event) => setRememberSession(event.target.checked)} className="h-4 w-4 rounded border-line text-primary focus:ring-primary" /><span>Recordar sesión</span></label>
              {error ? <div className="ep-kpi-critical rounded-2xl px-4 py-3 text-sm">{error}</div> : null}
              <button type="submit" disabled={isSubmitting} className="inline-flex h-14 w-full items-center justify-center gap-2 rounded-2xl bg-primary text-sm font-semibold text-white shadow-panel transition hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-70">{isSubmitting ? "Ingresando..." : "Ingresar"}<ArrowRight className="h-4 w-4" /></button>
            </form>
          </div>
        </section>
      </div>
    </main>
  );
}
