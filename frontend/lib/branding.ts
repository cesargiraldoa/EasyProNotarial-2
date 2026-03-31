export type NotaryBranding = {
  commercialName: string;
  legalName: string;
  primaryColor: string;
  secondaryColor: string;
  accentColor: string;
  logoInitials: string;
  officeLabel: string;
  city: string;
};

export const defaultBranding: NotaryBranding = {
  commercialName: "EasyPro Notarial",
  legalName: "Notaría 75 del Círculo de Bogotá",
  primaryColor: "13 46 93",
  secondaryColor: "77 91 124",
  accentColor: "80 214 144",
  logoInitials: "EP",
  officeLabel: "Sede principal",
  city: "Bogotá D.C.",
};

export const resolveBranding = (): NotaryBranding => defaultBranding;
