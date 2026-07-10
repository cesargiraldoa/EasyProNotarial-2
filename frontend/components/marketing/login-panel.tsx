"use client";

import Image from "next/image";
import { FormEvent, useState } from "react";
import { login, completeLogin } from "@/lib/api";

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
  const [consentAccepted, setConsentAccepted] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!consentAccepted) {
      setError("Debes aceptar el tratamiento de datos para continuar.");
      return;
    }

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
    <main className="min-h-screen bg-[#101418] text-white">
      <div className="grid min-h-screen lg:grid-cols-[1.16fr_0.84fr]">
        <section className="relative hidden flex-col justify-center bg-[#101418] p-10 lg:flex">
          <div className="mb-8 flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-md border border-[#d89b45]/45 bg-[#171c22] text-sm font-bold text-[#f7cf8a]">
              EN
            </div>
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-white">Ecosistema Notarial</p>
              <p className="mt-1 text-xs text-[#9aa6b2]">Acceso institucional seguro</p>
            </div>
          </div>

          <div className="relative w-full max-w-xl overflow-hidden rounded-lg shadow-[0_28px_80px_rgba(0,0,0,0.42)]">
            <Image
              src="/images/ecosistema-notarial-hero.png"
              alt="Ecosistema Notarial con sello Notarias de Colombia y documentos notariales"
              width={960}
              height={1200}
              className="w-full object-cover"
              priority
            />
          </div>
        </section>

        <section className="flex items-center justify-center bg-[#101418] px-6 py-10 sm:px-8">
          <div className="w-full max-w-md rounded-lg border border-[#d89b45]/22 bg-[#171c22] p-6 shadow-[0_24px_70px_rgba(0,0,0,0.36)] sm:p-8">
            <div className="space-y-5">
              <div className="flex items-center gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-md border border-[#d89b45]/45 bg-[#242a33] text-sm font-bold text-[#f7cf8a]">
                  EN
                </div>
                <p className="text-xs font-bold uppercase tracking-[0.3em] text-[#f7cf8a]">ACCESO</p>
              </div>

              <div>
                <h1 className="text-4xl font-semibold tracking-tight text-white">Ingresa a Ecosistema Notarial</h1>
                <p className="mt-3 text-sm leading-6 text-[#d7dee8]">Usa tus credenciales institucionales para continuar.</p>
              </div>
            </div>

            <form onSubmit={onSubmit} className="mt-8 space-y-5">
              <div>
                <label htmlFor="email" className="mb-1 block text-sm text-[#d7dee8]">
                  Usuario
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  defaultValue="superadmin@easypro.co"
                  className="w-full rounded-md border border-[#d89b45]/22 bg-[#101418] px-4 py-3 text-white placeholder:text-[#9aa6b2] transition focus:border-[#d89b45] focus:outline-none focus:ring-2 focus:ring-[#d89b45]/22"
                />
              </div>

              <div>
                <label htmlFor="password" className="mb-1 block text-sm text-[#d7dee8]">
                  Contraseña
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  defaultValue="ChangeMe123!"
                  className="w-full rounded-md border border-[#d89b45]/22 bg-[#101418] px-4 py-3 text-white placeholder:text-[#9aa6b2] transition focus:border-[#d89b45] focus:outline-none focus:ring-2 focus:ring-[#d89b45]/22"
                />
              </div>

              <label className="mt-2 flex cursor-pointer items-start gap-3">
                <input
                  type="checkbox"
                  checked={consentAccepted}
                  onChange={(event) => setConsentAccepted(event.target.checked)}
                  style={{ accentColor: "#d89b45" }}
                  className="mt-1 h-4 w-4 rounded border-[#d89b45]/35 bg-transparent"
                />
                <span className="text-xs leading-5 text-[#9aa6b2]">
                  He leido y acepto la <span className="font-medium text-[#f7cf8a]">politica de tratamiento de datos</span> y autorizo el uso institucional de la plataforma.
                </span>
              </label>

              <label className="flex items-center gap-3 text-sm text-[#d7dee8]">
                <input
                  type="checkbox"
                  checked={rememberSession}
                  onChange={(event) => setRememberSession(event.target.checked)}
                  style={{ accentColor: "#d89b45" }}
                  className="h-4 w-4 rounded border-[#d89b45]/35 bg-transparent"
                />
                <span>Recordar sesión</span>
              </label>

              {error ? (
                <div className="rounded-md border border-red-500/25 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                  {error}
                </div>
              ) : null}

              <button
                type="submit"
                disabled={isSubmitting || !consentAccepted}
                className="w-full rounded-md bg-[#d89b45] py-4 text-sm font-bold text-[#101418] transition hover:bg-[#f0b968] focus:outline-none focus:ring-2 focus:ring-[#f7cf8a]/50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isSubmitting ? "Ingresando..." : "Ingresar"}
              </button>
            </form>

            <p className="mt-6 text-center text-xs text-[#9aa6b2]">© 2026 Ecosistema Notarial · Acceso institucional</p>
          </div>
        </section>
      </div>
    </main>
  );
}
