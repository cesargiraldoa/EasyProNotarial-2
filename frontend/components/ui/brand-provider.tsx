"use client";

import type { CSSProperties, PropsWithChildren } from "react";
import { resolveBranding } from "@/lib/branding";

export function BrandProvider({ children }: PropsWithChildren) {
  const branding = resolveBranding();

  return (
    <div
      style={
        {
          "--primary": branding.primaryColor,
          "--secondary": branding.secondaryColor,
          "--accent": branding.accentColor
        } as CSSProperties
      }
    >
      {children}
    </div>
  );
}
