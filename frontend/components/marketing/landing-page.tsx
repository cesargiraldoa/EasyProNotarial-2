import Link from "next/link";
import {
  ArrowRight,
  Building2,
  FileStack,
  Layers3,
  ShieldCheck,
  Sparkles,
  Workflow
} from "lucide-react";
import { defaultBranding } from "@/lib/branding";
import { LogoBadge } from "@/components/ui/logo-badge";

const pillars = [
  {
    title: "Arquitectura multinotaría",
    copy: "Branding, usuarios y operación desacoplados para múltiples sedes y equipos.",
    icon: Building2
  },
  {
    title: "Flujos notariales trazables",
    copy: "Estados, responsables, hitos y evidencia listos para escrituras y lotes masivos.",
    icon: Workflow
  },
  {
    title: "Base documental premium",
    copy: "Vista previa, validación y preparación para generación masiva y control por registro.",
    icon: FileStack
  }
];

const capabilities = [
  "Branding por notaría con colores, nombre comercial y datos institucionales.",
  "Casos individuales y lotes diseñados para proyectos residenciales de múltiples escrituras.",
  "Shell autenticado premium con paneles laterales, cards operativas y preview documental.",
  "Base lista para integrar Gari IA en captura, validación, generación y soporte."
];

const previewSteps = ["Identificación", "Comparecientes", "Inmueble", "Revisión"];
const previewMenu = ["Catálogo", "Casos", "Plantillas", "Lotes", "Configuración"];

export function LandingPage() {
  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(80,214,144,0.10),_transparent_32%),linear-gradient(180deg,#f8fbff_0%,#eef4fb_100%)] text-ink">
      <section className="mx-auto flex min-h-screen max-w-7xl flex-col px-6 pb-12 pt-6 lg:px-10">
        <header className="flex flex-col gap-4 rounded-[2rem] border border-white/70 bg-white/80 px-5 py-4 shadow-soft backdrop-blur sm:flex-row sm:items-center sm:justify-between sm:rounded-full">
          <div className="flex min-w-0 items-center gap-4">
            <LogoBadge initials={defaultBranding.logoInitials} compact />
            <div className="min-w-0">
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-primary/70">
                {defaultBranding.commercialName}
              </p>
              <p className="mt-1 text-xs text-secondary">{defaultBranding.legalName}</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Link
              href="/login"
              className="rounded-full border border-line px-4 py-2 text-sm font-semibold text-primary transition hover:border-primary/40 hover:bg-primary/5"
            >
              Ingresar
            </Link>
            <span className="hidden rounded-full bg-primary px-4 py-2 text-sm font-semibold text-white lg:inline-flex">
              {"Plataforma notarial nueva generación"}
            </span>
          </div>
        </header>

        <div className="grid flex-1 gap-10 py-12 lg:grid-cols-[1.08fr_0.92fr] lg:items-center xl:gap-14">
          <div className="space-y-8">
            <div className="inline-flex max-w-full items-center gap-2 rounded-full border border-accent/30 bg-accent/10 px-4 py-2 text-sm font-medium text-primary">
              <Sparkles className="h-4 w-4 shrink-0 text-accent" />
              <span>{"Plataforma multinotaría lista para escrituras, operación y escalamiento"}</span>
            </div>

            <div className="space-y-6">
              <h1 className="max-w-4xl text-5xl font-semibold leading-[1.02] tracking-[-0.05em] text-primary lg:text-7xl">
                {"Operación notarial premium con base sólida para crecer."}
              </h1>
              <p className="max-w-2xl text-lg leading-8 text-secondary">
                {"EasyPro 2 nace como una plataforma nueva: multinotaría, multiusuario, con branding por sede, shell operativo moderno y arquitectura preparada para flujo de escrituras, lotes masivos y Gari IA."}
              </p>
            </div>

            <div className="flex flex-col gap-4 sm:flex-row">
              <Link
                href="/login"
                className="inline-flex items-center justify-center gap-2 rounded-2xl bg-primary px-6 py-4 text-sm font-semibold text-white shadow-panel transition hover:-translate-y-0.5 hover:bg-primary/95"
              >
                {"Iniciar sesión"}
                <ArrowRight className="h-4 w-4" />
              </Link>
              <a
                href="#capabilities"
                className="inline-flex items-center justify-center rounded-2xl border border-line bg-white/80 px-6 py-4 text-sm font-semibold text-primary transition hover:border-primary/30"
              >
                Ver capacidades base
              </a>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              {pillars.map(({ title, copy, icon: Icon }) => (
                <article key={title} className="rounded-3xl border border-white/80 bg-white/90 p-5 shadow-soft">
                  <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/8">
                    <Icon className="h-5 w-5 text-primary" />
                  </div>
                  <h2 className="text-lg font-semibold leading-6 text-primary">{title}</h2>
                  <p className="mt-3 text-sm leading-6 text-secondary">{copy}</p>
                </article>
              ))}
            </div>
          </div>

          <div className="relative">
            <div className="absolute -left-6 top-10 hidden h-40 w-40 rounded-full bg-accent/20 blur-3xl lg:block" />
            <div className="relative overflow-hidden rounded-[2rem] border border-white/80 bg-white p-4 shadow-panel sm:p-6">
              <div className="grid gap-5 lg:grid-cols-[0.64fr_1fr]">
                <aside className="rounded-[1.5rem] bg-slate-50 p-4">
                  <div className="mb-6 flex items-center gap-3">
                    <LogoBadge initials={defaultBranding.logoInitials} compact />
                    <div>
                      <p className="font-semibold text-primary">EasyPro 2</p>
                      <p className="text-xs text-secondary">Software notarial</p>
                    </div>
                  </div>
                  <div className="space-y-3">
                    {previewMenu.map((item, index) => (
                      <div
                        key={item}
                        className={`rounded-2xl px-4 py-3 text-sm font-medium leading-5 ${
                          index === 1 ? "bg-white text-primary shadow-soft" : "text-secondary"
                        }`}
                      >
                        {item}
                      </div>
                    ))}
                  </div>
                </aside>

                <div className="space-y-5">
                  <div className="rounded-[1.5rem] bg-slate-50 p-5">
                    <div className="mb-4 flex items-start justify-between gap-4">
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-accent">
                          {"Operación inteligente"}
                        </p>
                        <h3 className="mt-2 text-2xl font-semibold leading-tight text-primary">
                          Dashboard de escrituras y lotes
                        </h3>
                      </div>
                      <ShieldCheck className="mt-1 h-10 w-10 shrink-0 text-accent" />
                    </div>

                    <div className="grid gap-4 md:grid-cols-2">
                      <div className="rounded-3xl bg-white p-4 shadow-soft">
                        <p className="text-xs uppercase tracking-[0.2em] text-secondary">{"Trámite activo"}</p>
                        <p className="mt-3 text-xl font-semibold leading-7 text-primary">
                          Compraventa Torre Reserva 14B
                        </p>
                        <div className="mt-4 grid gap-2 sm:grid-cols-4">
                          {previewSteps.map((step, index) => (
                            <div key={step} className="space-y-2">
                              <div className={`h-2 rounded-full ${index < 3 ? "bg-accent" : "bg-slate-200"}`} />
                              <p className="text-xs font-medium leading-5 text-secondary">{step}</p>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="rounded-3xl bg-primary p-4 text-white shadow-soft">
                        <p className="text-xs uppercase tracking-[0.2em] text-white/70">
                          {"Producción masiva preparada"}
                        </p>
                        <p className="mt-3 text-3xl font-semibold">128 casos</p>
                        <p className="mt-2 text-sm leading-6 text-white/80">
                          Arquitectura prevista para lotes, errores por registro y plantillas reutilizables.
                        </p>
                      </div>
                    </div>
                  </div>

                  <div id="capabilities" className="grid gap-4 rounded-[1.5rem] bg-primary p-5 text-white">
                    <div className="flex items-center gap-3">
                      <Layers3 className="h-5 w-5 text-accent" />
                      <p className="text-sm font-semibold uppercase tracking-[0.22em] text-white/80">
                        Base del producto
                      </p>
                    </div>
                    <div className="space-y-3">
                      {capabilities.map((item) => (
                        <div
                          key={item}
                          className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm leading-6 text-white/90"
                        >
                          {item}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
