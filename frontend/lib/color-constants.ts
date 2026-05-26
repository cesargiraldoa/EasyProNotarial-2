// Colores centralizados para gráficas — sincronizados con el design system
export const CHART_COLORS = {
  primary:   '#1A3560',
  secondary: '#3B6FCF',
  accent:    '#50D690',
  muted:     '#526082',
  soft:      '#707E9E',
  warn:      '#F0C040',
  error:     '#C23B22',
  success:   '#1B7F3A',
} as const;

export const CHART_PALETTE = [
  CHART_COLORS.primary,
  CHART_COLORS.accent,
  CHART_COLORS.secondary,
  CHART_COLORS.warn,
  CHART_COLORS.muted,
  CHART_COLORS.error,
] as const;
