import type { Metadata } from "next";
import "./globals.css";
import "./brand-name.css";
import { BrandProvider } from "@/components/ui/brand-provider";
import { ThemeProvider } from "@/components/ui/theme-provider";

export const metadata: Metadata = {
  title: "Ecosistema Notarial",
  description: "Base multinotaria para operacion notarial premium.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es" suppressHydrationWarning>
      <body>
        <ThemeProvider>
          <BrandProvider>{children}</BrandProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
