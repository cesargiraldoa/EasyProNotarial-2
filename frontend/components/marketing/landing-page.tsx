"use client";

import Link from "next/link";
import Image from "next/image";
import { useState } from "react";
import {
  ArrowRight,
  Building2,
  CheckCircle2,
  FileStack,
  Layers3,
  Mail,
  Play,
  Plus,
  Phone,
  ShieldCheck,
  Sparkles,
  Workflow,
  X,
  XCircle,
} from "lucide-react";
import { defaultBranding } from "@/lib/branding";
import { LogoBadge } from "@/components/ui/logo-badge";

const beforeItems = [
  "Plantillas Word con etiquetas manuales",
  "Errores de digitación sin validación",
  "Sin trazabilidad ni historial",
  "Proceso lento minuta a minuta",
  "Sin control de calidad interno",
];

const afterItems = [
  "Formulario guiado por tipo de acto",
  "Validación automática de campos",
  "Flujo protocolista - revisor - aprobador - notario",
  "Generación del documento en segundos",
  "Historial completo por minuta e interviniente",
];

const features = [
  {
    title: "Multinotaría nativa",
    description: "Cada notaría con su branding, usuarios y datos completamente separados.",
    icon: Layers3,
  },
  {
    title: "Flujo de aprobación",
    description: "Protocolista - Revisor - Aprobador - Firma del notario. Trazable en cada paso.",
    icon: Workflow,
  },
  {
    title: "Actos masivos en lote",
    description: "Procese cientos de escrituras similares en un solo flujo automatizado.",
    icon: FileStack,
  },
  {
    title: "Motor documental dinámico",
    description: "Sin etiquetas manuales. El sistema construye el documento con los datos ingresados.",
    icon: Sparkles,
  },
  {
    title: "Trazabilidad completa",
    description: "Historial por minuta, interviniente y acto. Auditable en cualquier momento.",
    icon: ShieldCheck,
  },
  {
    title: "Personalizado por notaría",
    description: "Colores, logo, imagen de acceso y nombre comercial propios por sede.",
    icon: Building2,
  },
];

const faqs = [
  {
    question: "¿Necesito modificar mis plantillas Word actuales?",
    answer:
      "No. EasyPro genera los documentos a partir de los datos que ingresa el protocolista. Sus plantillas Word son el punto de partida, no el centro del proceso.",
  },
  {
    question: "¿Cuánto tiempo toma implementar EasyPro en mi notaría?",
    answer:
      "La configuración inicial toma menos de un día. En 24 horas su equipo puede estar operando la primera minuta real.",
  },
  {
    question: "¿Funciona para múltiples notarías?",
    answer:
      "Sí. EasyPro está diseñado para operar varias notarías desde una sola plataforma, con datos completamente separados entre sí.",
  },
  {
    question: "¿Qué pasa con las minutas que ya tenemos en proceso?",
    answer:
      "Las minutas anteriores pueden migrarse o continuar en el sistema anterior. EasyPro inicia con minutas nuevas y crece con su operación.",
  },
  {
    question: "¿Es seguro?",
    answer:
      "Sí. HTTPS en todos los accesos, autenticación con JWT, datos separados por notaría y backups automáticos diarios en Supabase.",
  },
];

const identityChips = ["Colores propios", "URL propia", "Imagen propia"];

const successCases = [
  {
    initials: "NC",
    status: "Live desde Abr 2026",
    title: "Notaría Única del Círculo de Caldas",
    subtitle: "Caldas, Antioquia  Colombia",
    description:
      "La primera notaría en operar en vivo con EasyPro, consolidando el flujo completo de atención, validación y generación documental en producción.",
    tags: ["Poder General", "Venta sin RPH", "Salida del País"],
    href: "https://wa.me/573107932844",
    cta: "Contactar como referencia",
    videoUrl: "https://www.youtube.com/embed/TODO_CALDAS",
    live: true,
  },
  {
    initials: "NB",
    status: "Demo disponible",
    title: "Notaría Primera del Círculo de Bello",
    subtitle: "Bello, Antioquia  Colombia",
    description:
      "Notaría piloto de referencia con acceso a demo guiada para validar el flujo, resolver dudas y revisar minutas reales antes de salir a producción.",
    tags: ["Entorno de demo", "Minutas reales", "Acceso guiado"],
    href: "https://wa.me/573107932844",
    cta: "Solicitar demo",
    videoUrl: "https://www.youtube.com/embed/TODO_BELLO",
    live: false,
  },
];

export function LandingPage() {
  const [openFaq, setOpenFaq] = useState<number | null>(0);
  const [newsletterEmail, setNewsletterEmail] = useState("");
  const [newsletterAccepted, setNewsletterAccepted] = useState(false);
  const [videoModal, setVideoModal] = useState<{ open: boolean; url: string; title: string }>({
    open: false,
    url: "",
    title: "",
  });

  return (
    <main className="min-h-screen bg-[#0D1B2A] font-sans text-white">
      <header className="sticky top-0 z-50 border-b border-[#1A3350] bg-[#0D1B2A]">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex min-w-0 items-center gap-3 sm:gap-4">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-[#00E5A0] text-sm font-black text-black shadow-sm">
              EP
            </div>
            <span className="sr-only">
              <LogoBadge initials={defaultBranding.logoInitials} compact />
            </span>
            <div className="min-w-0">
              <p className="truncate text-base font-black uppercase tracking-[0.24em] text-white">
                {defaultBranding.commercialName}
              </p>
              <p className="truncate text-xs font-medium uppercase tracking-[0.18em] text-[#8892A4]">{defaultBranding.legalName}</p>
            </div>
          </div>

          <Link
            href="/login"
            className="inline-flex items-center justify-center rounded-full border border-white px-5 py-2.5 text-sm font-semibold text-white transition-all duration-200 hover:bg-white hover:text-[#0D1B2A]"
          >
            Ingresar
          </Link>
        </div>
      </header>

      <section className="relative overflow-hidden bg-[#0D1B2A] bg-[radial-gradient(ellipse_at_20%_50%,#1A3350_0%,transparent_60%)]">
        <div className="relative flex min-h-screen items-center py-20 px-6 md:px-10 lg:px-16">
          <div className="mx-auto grid w-full max-w-7xl items-center gap-14 lg:grid-cols-[1.15fr_0.85fr]">
            <div className="max-w-3xl">
              <div className="inline-flex items-center gap-3 rounded-full border border-[#1A3350] bg-[#1A3350] px-4 py-2 text-sm font-medium text-[#00E5A0]">
                <span className="relative flex h-2.5 w-2.5">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#00E5A0] opacity-40" />
                  <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-[#00E5A0]" />
                </span>
                Plataforma notarial nueva generación
              </div>

              <h1 className="mt-10 text-5xl font-black leading-none tracking-tight text-white md:text-7xl lg:text-8xl">
                La notaría del futuro,
                <br />
                operando <span className="text-[#00E5A0]">hoy.</span>
              </h1>

              <p className="mt-6 max-w-xl text-lg leading-relaxed text-[#8892A4]">
                EasyPro digitaliza y estandariza cada acto notarial: escrituras, poderes, declaraciones y actos masivos sin plantillas con etiquetas manuales.
              </p>

              <div className="mt-8 flex flex-col gap-4 sm:flex-row">
                <Link
                  href="/login"
                  className="inline-flex items-center justify-center gap-2 rounded-full bg-[#00E5A0] px-8 py-4 text-base font-bold text-[#0D1B2A] transition-all duration-200 hover:bg-[#00C98A]"
                >
                  Iniciar sesión
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <a
                  href="#funcionamiento"
                  className="inline-flex items-center justify-center rounded-full border border-white/30 px-8 py-4 text-base font-semibold text-white transition-all duration-200 hover:bg-white/10"
                >
                  Ver cómo funciona
                </a>
              </div>

              <div className="mt-12 grid gap-6 sm:grid-cols-3 sm:divide-x sm:divide-white/10">
                <div className="space-y-2 sm:pr-6">
                  <p className="text-lg font-bold text-white">9 Abr 2026</p>
                  <p className="text-sm text-[#8892A4]">Go-live</p>
                </div>
                <div className="space-y-2 sm:pl-6 sm:pr-6">
                  <p className="text-lg font-bold text-white">100% digital</p>
                  <p className="text-sm text-[#8892A4]">Sin papel</p>
                </div>
                <div className="space-y-2 sm:pl-6">
                  <p className="text-lg font-bold text-white">Multinotaría</p>
                  <p className="text-sm text-[#8892A4]">Una plataforma</p>
                </div>
              </div>
            </div>

            <div className="hidden md:block">
              <div className="relative mx-auto w-full max-w-md">
                <div className="absolute -inset-4 rounded-[2rem] bg-[#00E5A0]/10 blur-3xl" />
                <Image
                  src="/notario-hero.png"
                  alt="Imagen notarial de referencia para EasyPro"
                  width={720}
                  height={900}
                  priority
                  className="relative z-10 w-full rounded-3xl object-cover drop-shadow-2xl"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="funcionamiento" className="bg-white py-24 text-[#0D1B2A]">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <p className="text-sm font-bold uppercase tracking-[0.28em] text-[#00E5A0]">OPERACIÓN INTELIGENTE</p>
          <h2 className="mt-4 text-4xl font-bold tracking-tight md:text-5xl">
            De lo manual a la operación
            <br />
            <span className="text-[#00E5A0]">inteligente.</span>
          </h2>

          <div className="mt-12 grid gap-6 lg:grid-cols-2">
            <article className="rounded-3xl border border-[#E5E7EB] bg-[#F8F9FA] p-8">
              <div className="flex items-center gap-3">
                <XCircle className="h-6 w-6 text-[#EF4444]" />
                <h3 className="text-lg font-bold text-[#EF4444]">Antes</h3>
              </div>
              <ul className="mt-6 space-y-4">
                {beforeItems.map((item) => (
                  <li key={item} className="flex items-start gap-3 text-base leading-relaxed text-[#0D1B2A]">
                    <span className="mt-2 h-2.5 w-2.5 shrink-0 rounded-full bg-[#EF4444]" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </article>

            <article className="rounded-3xl bg-[#0D1B2A] p-8 text-white">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="h-6 w-6 text-[#22C55E]" />
                <h3 className="text-lg font-bold text-[#22C55E]">Con EasyPro</h3>
              </div>
              <ul className="mt-6 space-y-4">
                {afterItems.map((item) => (
                  <li key={item} className="flex items-start gap-3 text-base leading-relaxed text-[#F0F4FF]">
                    <span className="mt-2 h-2.5 w-2.5 shrink-0 rounded-full bg-[#00E5A0]" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </article>
          </div>
        </div>
      </section>

      <section className="bg-[#112236] py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <p className="text-sm font-bold uppercase tracking-[0.28em] text-[#00E5A0]">CAPACIDADES</p>
          <h2 className="mt-4 text-4xl font-bold tracking-tight text-white md:text-5xl">
            Todo lo que su notaría
            <br />
            <span className="text-[#00E5A0]">necesita.</span>
          </h2>

          <div className="mt-12 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
            {features.map(({ title, description, icon: Icon }) => (
              <article
                key={title}
                className="rounded-2xl border border-[#1E3A5F] bg-[#1A3350] p-8 transition-all duration-200 hover:border-[#00E5A0]/60 hover:bg-[#223351]"
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#00E5A0]/10 text-[#00E5A0]">
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="mt-4 text-xl font-semibold text-white">{title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-[#8892A4]">{description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-white py-24 text-[#0D1B2A]">
        <div className="mx-auto grid max-w-7xl gap-12 px-4 sm:px-6 lg:grid-cols-[1.05fr_0.95fr] lg:px-8">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.28em] text-[#00E5A0]">IDENTIDAD INSTITUCIONAL</p>
            <h2 className="mt-4 text-4xl font-bold tracking-tight md:text-5xl">
              Cada notaría,
              <br />
              <span className="text-[#00E5A0]">su propia identidad.</span>
            </h2>
            <p className="mt-6 max-w-2xl text-lg leading-relaxed text-[#8892A4]">
              EasyPro se adapta al branding de cada notaría. Colores institucionales, logo, imagen de acceso y nombre comercial configurado en minutos, sin código.
            </p>

            <ul className="mt-8 space-y-4">
              {["Colores y logo propios por sede", "URL personalizada por notaría", "Imagen de acceso institucional"].map((item) => (
                <li key={item} className="flex items-center gap-3 text-base text-[#0D1B2A]">
                  <CheckCircle2 className="h-5 w-5 text-[#00E5A0]" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="flex items-center">
            <div className="w-full rounded-3xl bg-[#0D1B2A] p-8 text-white">
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#00E5A0] text-sm font-black text-black">EP</div>
                <div>
                  <p className="text-lg font-bold tracking-tight">NOTARÍA DE CALDAS</p>
                  <p className="text-sm text-[#8892A4]">Notaría Primera del Círculo</p>
                </div>
              </div>

              <div className="mt-8 flex flex-wrap gap-3">
                {identityChips.map((chip) => (
                  <span key={chip} className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white">
                    {chip}
                  </span>
                ))}
              </div>

              <div className="my-8 h-px bg-[#1A3350]" />

              <p className="text-sm text-[#8892A4]">Configuración activa · Notaría de Caldas</p>
            </div>
          </div>
        </div>
      </section>

      <section id="casos-de-exito" className="bg-[#0D1B2A] py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <p className="text-sm font-bold uppercase tracking-[0.28em] text-[#00E5A0]">CASOS DE ÉXITO</p>
          <h2 className="mt-4 text-4xl font-bold tracking-tight text-white md:text-5xl">
            Notarías que ya operan
            <br />
            <span className="text-[#00E5A0]">con EasyPro.</span>
          </h2>
          <p className="mt-6 max-w-3xl text-lg leading-relaxed text-[#8892A4]">
            Estas notarías ya trabajan con una operación más clara, trazable y ordenada. Una está en producción y la otra funciona como referencia guiada para evaluación y demo.
          </p>

          <div className="mt-12 grid gap-6 md:grid-cols-2">
            {successCases.map((caseItem) => (
              <article
                key={caseItem.title}
                className="rounded-3xl border border-[#1E3A5F] bg-[#112236] p-8 transition-all duration-200 hover:border-[#00E5A0]/60"
              >
                <div className="flex items-start justify-between gap-6">
                  <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-[#00E5A0] text-base font-black text-black">
                    {caseItem.initials}
                  </div>

                  <div
                    className={`inline-flex items-center gap-2 rounded-full border border-[#1E3A5F] px-4 py-2 text-sm font-medium ${caseItem.live ? "text-[#00E5A0]" : "text-[#8892A4]"}`}
                  >
                    {caseItem.live ? (
                      <span className="relative flex h-2.5 w-2.5">
                        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#00E5A0] opacity-40" />
                        <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-[#00E5A0]" />
                      </span>
                    ) : null}
                    <span>{caseItem.status}</span>
                  </div>
                </div>

                <h3 className="mt-6 text-2xl font-bold tracking-tight text-white">{caseItem.title}</h3>
                <p className="mt-2 text-sm font-medium text-[#8892A4]">{caseItem.subtitle}</p>
                <p className="mt-5 text-base leading-relaxed text-[#8892A4]">{caseItem.description}</p>

                <div className="mt-6 flex flex-wrap gap-3">
                  {caseItem.tags.map((tag) => (
                    <span
                      key={tag}
                      className="rounded-full border border-[#1E3A5F] bg-[#1A3350] px-4 py-2 text-sm text-[#E6EBF5]"
                    >
                      {tag}
                    </span>
                  ))}
                </div>

                <div className="mt-8 border-t border-[#1E3A5F] pt-6 flex items-center justify-between gap-4 flex-wrap">
                  <button
                    type="button"
                    onClick={() =>
                      setVideoModal({
                        open: true,
                        url: caseItem.videoUrl,
                        title: caseItem.title,
                      })
                    }
                    className="inline-flex items-center gap-2 rounded-full border border-[#00E5A0]/40 px-4 py-2 text-sm font-semibold text-[#00E5A0] transition-colors hover:bg-[#00E5A0]/10"
                  >
                    <Play className="h-4 w-4" />
                    Ver testimonio
                  </button>

                  <a
                    href={caseItem.href}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-2 text-sm font-semibold text-[#00E5A0] transition-colors hover:text-[#00C98A]"
                  >
                    {caseItem.cta}
                    <ArrowRight className="h-4 w-4" />
                  </a>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-[#0D1B2A] py-24">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
          <p className="text-sm font-bold uppercase tracking-[0.28em] text-[#00E5A0]">SOPORTE Y CLARIDAD</p>
          <h2 className="mt-4 text-4xl font-bold tracking-tight text-white md:text-5xl">
            Preguntas
            <br />
            <span className="text-[#00E5A0]">frecuentes.</span>
          </h2>

          <div className="mt-12 space-y-4">
            {faqs.map((faq, index) => {
              const isOpen = openFaq === index;

              return (
                <div
                  key={faq.question}
                  className={`rounded-2xl border bg-[#112236] transition-all duration-200 ${isOpen ? "border-[#00E5A0]" : "border-[#1A3350]"}`}
                >
                  <button
                    type="button"
                    onClick={() => setOpenFaq(isOpen ? null : index)}
                    className="flex w-full items-center justify-between gap-4 px-6 py-5 text-left"
                    aria-expanded={isOpen}
                  >
                    <span className="text-lg font-medium text-white">{faq.question}</span>
                    <span className="flex h-8 w-8 items-center justify-center rounded-full border border-[#1A3350] text-[#00E5A0]">
                      {isOpen ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
                    </span>
                  </button>
                  {isOpen ? (
                    <div className="px-6 pb-6 pt-0 text-base leading-relaxed text-[#8892A4]">
                      {faq.answer}
                    </div>
                  ) : null}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="bg-gradient-to-b from-[#0D1B2A] to-[#112236] py-32">
        <div className="mx-auto max-w-5xl px-4 text-center sm:px-6 lg:px-8">
          <h2 className="text-5xl font-black leading-none tracking-tight text-white md:text-7xl">
            Su notaría lista
            <br />
            para el <span className="text-[#00E5A0]">siguiente nivel.</span>
          </h2>
          <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-[#8892A4]">
            Únase a las notarías que ya operan con EasyPro Notarial.
          </p>

          <div className="mt-10">
            <Link
              href="/login"
              className="inline-flex items-center justify-center rounded-full bg-[#00E5A0] px-12 py-5 text-lg font-bold text-[#0D1B2A] transition-all duration-200 hover:bg-[#00C98A]"
            >
              Solicitar acceso
            </Link>
          </div>

          <p className="mt-14 text-sm text-[#8892A4]">© 2026 EasyPro Notarial · Todos los derechos reservados</p>
        </div>
      </section>
      {videoModal.open ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
          onClick={() => setVideoModal({ open: false, url: "", title: "" })}
        >
          <div
            className="relative mx-4 w-full max-w-3xl rounded-3xl border border-[#1E3A5F] bg-[#0D1B2A] p-6"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="flex items-center justify-between gap-4">
              <h3 className="text-lg font-bold text-white">{videoModal.title}</h3>
              <button
                type="button"
                onClick={() => setVideoModal({ open: false, url: "", title: "" })}
                className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-[#1E3A5F] text-[#8892A4] transition-colors hover:border-[#00E5A0]/60 hover:text-[#00E5A0]"
                aria-label="Cerrar modal"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <iframe
              className="mt-4 aspect-video w-full rounded-2xl"
              src={videoModal.url}
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              title={videoModal.title}
            />

            <p className="mt-3 text-center text-xs text-[#8892A4]">Video testimonial  próximamente disponible</p>
          </div>
        </div>
      ) : null}
      <footer>
        <section className="bg-black py-12 px-6">
          <div className="mx-auto grid max-w-7xl gap-8 lg:grid-cols-[1fr_1.1fr] lg:items-center">
            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full border border-[#1E3A5F] bg-[#0D1B2A] text-[#00E5A0]">
                <Mail className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white">Mantente al día con EasyPro</h3>
                <p className="mt-2 max-w-xl text-sm leading-relaxed text-[#8892A4]">
                  Recibe novedades sobre la plataforma y el sector notarial colombiano.
                </p>
              </div>
            </div>

            <div className="grid gap-4">
              <div className="flex flex-col gap-3 sm:flex-row">
                <input
                  type="email"
                  value={newsletterEmail}
                  onChange={(event) => setNewsletterEmail(event.target.value)}
                  placeholder="Correo electrónico"
                  className="h-12 min-w-0 flex-1 rounded-full border border-[#1E3A5F] bg-[#0D1B2A] px-5 text-sm text-white placeholder:text-[#8892A4] focus:border-[#00E5A0] focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => {
                    if (!newsletterAccepted || !newsletterEmail.trim()) return;
                  }}
                  className="inline-flex h-12 items-center justify-center rounded-full bg-[#00E5A0] px-7 text-sm font-bold text-black transition-colors hover:bg-[#00d895]"
                >
                  Suscribirse
                </button>
              </div>

              <label className="flex items-start gap-3 text-sm text-[#8892A4]">
                <input
                  type="checkbox"
                  checked={newsletterAccepted}
                  onChange={(event) => setNewsletterAccepted(event.target.checked)}
                  className="mt-1 h-4 w-4 rounded border-[#1E3A5F] bg-transparent text-[#00E5A0] focus:ring-[#00E5A0]"
                />
                <span>Acepto las políticas de tratamiento de datos personales</span>
              </label>
            </div>
          </div>
        </section>

        <section className="bg-[#0D1B2A] py-16 px-6">
          <div className="mx-auto grid max-w-7xl gap-10 md:grid-cols-2 lg:grid-cols-4">
            <div>
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-full bg-[#00E5A0] text-sm font-black text-black">
                  EP
                </div>
                <div>
                  <p className="text-sm font-black tracking-[0.24em] text-white">EASYPRO NOTARIAL</p>
                  <p className="text-sm text-[#8892A4]">Plataforma notarial digital</p>
                </div>
              </div>
            </div>

            <div>
              <h4 className="text-sm font-bold uppercase tracking-[0.2em] text-white">Producto</h4>
              <ul className="mt-5 space-y-3 text-sm">
                <li>
                  <a href="#funcionamiento" className="text-[#8892A4] transition-colors hover:text-[#00E5A0]">
                    Capacidades
                  </a>
                </li>
                <li>
                  <a href="#funcionamiento" className="text-[#8892A4] transition-colors hover:text-[#00E5A0]">
                    Cómo funciona
                  </a>
                </li>
                <li>
                  <a href="#funcionamiento" className="text-[#8892A4] transition-colors hover:text-[#00E5A0]">
                    Preguntas frecuentes
                  </a>
                </li>
                <li>
                  <Link href="/login" className="text-[#8892A4] transition-colors hover:text-[#00E5A0]">
                    Solicitar acceso
                  </Link>
                </li>
              </ul>
            </div>

            <div>
              <h4 className="text-sm font-bold uppercase tracking-[0.2em] text-white">Empresa</h4>
              <ul className="mt-5 space-y-3 text-sm">
                <li>
                  <a href="#funcionamiento" className="text-[#8892A4] transition-colors hover:text-[#00E5A0]">
                    Sobre EasyPro
                  </a>
                </li>
                <li>
                  <a href="#funcionamiento" className="text-[#8892A4] transition-colors hover:text-[#00E5A0]">
                    Contacto
                  </a>
                </li>
                <li>
                  <a href="#funcionamiento" className="text-[#8892A4] transition-colors hover:text-[#00E5A0]">
                    Términos de uso
                  </a>
                </li>
                <li>
                  <a href="#funcionamiento" className="text-[#8892A4] transition-colors hover:text-[#00E5A0]">
                    Política de privacidad
                  </a>
                </li>
              </ul>
            </div>

            <div>
              <h4 className="text-sm font-bold uppercase tracking-[0.2em] text-white">Medellín, Colombia</h4>
              <div className="mt-5 space-y-2 text-sm leading-relaxed text-[#8892A4]">
                <p>Carrera 43B #1A Sur - 70</p>
                <p>Piso 10, Edificio Buró 4.0</p>
                <p>Medellín, Antioquia</p>
              </div>
            </div>
          </div>
        </section>

        <section className="border-t border-[#1E3A5F] bg-black py-4 px-6">
          <p className="text-center text-sm text-[#8892A4]">
            © 2026 EasyPro Notarial · Todos los derechos reservados · Colombia
          </p>
        </section>
      </footer>
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3">
        <a
          href="https://wa.me/573107932844"
          target="_blank"
          rel="noreferrer"
          className="flex h-14 w-14 items-center justify-center rounded-full bg-[#25D366] shadow-lg transition-transform hover:scale-110"
          aria-label="Contactar por WhatsApp"
        >
          <svg viewBox="0 0 24 24" fill="white" className="h-6 w-6" aria-hidden="true">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z" />
          </svg>
        </a>

        <a
          href="tel:+573107932844"
          className="flex h-14 w-14 items-center justify-center rounded-full bg-[#00E5A0] shadow-lg transition-transform hover:scale-110"
          aria-label="Llamar por teléfono"
        >
          <Phone size={24} color="#0D1B2A" />
        </a>
      </div>
    </main>
  );
}
