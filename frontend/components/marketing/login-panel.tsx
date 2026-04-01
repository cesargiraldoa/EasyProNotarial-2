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
    <main className="min-h-screen bg-[#0D1B2A] text-white">
      <div className="grid min-h-screen lg:grid-cols-[1.22fr_0.78fr]">
        <section className="relative hidden lg:flex flex-col items-center justify-center bg-[#0D1B2A] p-10">
          <div className="relative w-full max-w-sm overflow-hidden rounded-3xl shadow-2xl">
            <Image
              src="/notario-hero.png"
              alt="EasyPro Notarial"
              width={480}
              height={560}
              className="w-full rounded-3xl object-cover"
              priority
            />
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-[#0D1B2A] to-transparent p-6">
              <p className="text-xs font-semibold uppercase tracking-widest text-[#00E5A0]">Plataforma activa</p>
              <p className="mt-1 text-lg font-bold text-white">Notaría de Caldas</p>
              <p className="mt-1 text-xs text-[#8892A4]">Notaría Primera del Círculo · Go-live 9 Abr 2026</p>
            </div>
          </div>

          <p className="mt-8 max-w-xs text-center text-sm leading-relaxed text-[#8892A4]">"La plataforma que modernizó nuestra operación notarial desde el primer día."</p>
          <p className="mt-2 text-xs font-semibold text-[#00E5A0]">Notaría de Caldas</p>
        </section>

        <section className="flex items-center justify-center bg-[#0D1B2A] px-8 py-10">
          <div className="w-full max-w-sm rounded-[2rem] border border-[#1E3A5F] bg-[#112236] p-6 shadow-2xl sm:p-7">
            <div className="space-y-5">
              <div className="flex items-center gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#00E5A0] text-sm font-black text-[#0D1B2A]">
                  EP
                </div>
                <p className="text-xs font-bold uppercase tracking-[0.3em] text-[#00E5A0]">ACCESO</p>
              </div>

              <div>
                <h1 className="text-4xl font-black tracking-tight text-white">Inicia sesión</h1>
                <p className="mt-3 text-sm text-[#8892A4]">Ingresa con tus credenciales institucionales</p>
              </div>
            </div>

            <form onSubmit={onSubmit} className="mt-8 space-y-5">
              <div>
                <label htmlFor="email" className="mb-1 block text-sm text-[#8892A4]">
                  Usuario
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  defaultValue="superadmin@easypro.co"
                  className="w-full rounded-2xl border border-[#1E3A5F] bg-[#1A3350] px-4 py-3 text-white placeholder:text-[#8892A4] transition focus:border-[#00E5A0] focus:outline-none"
                />
              </div>

              <div>
                <label htmlFor="password" className="mb-1 block text-sm text-[#8892A4]">
                  Contraseña
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  defaultValue="ChangeMe123!"
                  className="w-full rounded-2xl border border-[#1E3A5F] bg-[#1A3350] px-4 py-3 text-white placeholder:text-[#8892A4] transition focus:border-[#00E5A0] focus:outline-none"
                />
              </div>

              <label className="mt-2 flex cursor-pointer items-start gap-3">
                <input
                  type="checkbox"
                  checked={consentAccepted}
                  onChange={(event) => setConsentAccepted(event.target.checked)}
                  style={{ accentColor: "#00E5A0" }}
                  className="mt-1 h-4 w-4 rounded border-[#1E3A5F] bg-transparent"
                />
                <span className="text-xs leading-5 text-[#8892A4]">
                  He leído y acepto la <span className="font-medium text-[#00E5A0]">política de tratamiento de datos</span> y autorizo el uso institucional de la plataforma.
                </span>
              </label>

              <label className="flex items-center gap-3 text-sm text-[#8892A4]">
                <input
                  type="checkbox"
                  checked={rememberSession}
                  onChange={(event) => setRememberSession(event.target.checked)}
                  style={{ accentColor: "#00E5A0" }}
                  className="h-4 w-4 rounded border-[#1E3A5F] bg-transparent"
                />
                <span>Recordar sesión</span>
              </label>

              {error ? (
                <div className="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">
                  {error}
                </div>
              ) : null}

              <button
                type="submit"
                disabled={isSubmitting || !consentAccepted}
                className="w-full rounded-2xl bg-[#00E5A0] py-4 text-sm font-bold text-[#0D1B2A] transition hover:bg-[#00C98A] disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isSubmitting ? "Ingresando..." : "Ingresar"}
              </button>
            </form>

            <p className="mt-6 text-center text-xs text-[#8892A4]">© 2026 EasyPro Notarial · Acceso institucional</p>
          </div>
        </section>
      </div>
    </main>
  );
}