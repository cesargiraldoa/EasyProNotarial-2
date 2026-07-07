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
  commercialName: "Ecosistema Notarial",
  legalName: "Plataforma notarial digital",
  primaryColor: "13 46 93",
  secondaryColor: "77 91 124",
  accentColor: "80 214 144",
  logoInitials: "EN",
  officeLabel: "Sede principal",
  city: "Colombia",
};

export const resolveBranding = (): NotaryBranding => defaultBranding;
