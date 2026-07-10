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
  primaryColor: "16 20 24",
  secondaryColor: "96 106 118",
  accentColor: "216 155 69",
  logoInitials: "EN",
  officeLabel: "Sede principal",
  city: "Colombia",
};

export const resolveBranding = (): NotaryBranding => defaultBranding;
