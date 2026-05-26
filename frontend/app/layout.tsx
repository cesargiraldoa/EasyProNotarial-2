import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "@/app/globals.css";
import { BrandProvider } from "@/components/ui/brand-provider";
import { ThemeProvider } from "@/components/ui/theme-provider";

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600"],
  variable: "--font-jakarta",
  display: "swap",
});

export const metadata: Metadata = {
  title: "EasyPro 2",
  description: "Base multinotaría para operación notarial premium.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es" suppressHydrationWarning>
      <body className={jakarta.variable}>
        <ThemeProvider>
          <BrandProvider>{children}</BrandProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
