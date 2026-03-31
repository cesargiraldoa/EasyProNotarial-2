const EASYPRO_LOCALE = "es-CO";
const EASYPRO_TIME_ZONE = "America/Bogota";

type DateParseStrategy = "utc" | "bogota";

type FormatDateTimeOptions = {
  includeSeconds?: boolean;
  strategy?: DateParseStrategy;
};

type DateTimeLocalOptions = {
  strategy?: DateParseStrategy;
};

const ISO_WITH_ZONE = /(Z|[+-]\d{2}:?\d{2})$/i;
const ISO_DATE_ONLY = /^\d{4}-\d{2}-\d{2}$/;
const ISO_NAIVE = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(?:\.\d+)?)?$/;

function buildUtcDateFromNaive(value: string): Date | null {
  const match = value.match(
    /^(\d{4})-(\d{2})-(\d{2})(?:T(\d{2}):(\d{2})(?::(\d{2})(?:\.(\d{1,6}))?)?)?$/
  );
  if (!match) return null;

  const [, year, month, day, hour = "00", minute = "00", second = "00", fraction = "0"] = match;
  const milliseconds = Number(fraction.padEnd(3, "0").slice(0, 3));
  const date = new Date(Date.UTC(Number(year), Number(month) - 1, Number(day), Number(hour), Number(minute), Number(second), milliseconds));
  return Number.isNaN(date.getTime()) ? null : date;
}

function parseDateValue(value: string | number | Date | null | undefined, strategy: DateParseStrategy = "utc"): Date | null {
  if (value == null || value === "") return null;
  if (value instanceof Date) return Number.isNaN(value.getTime()) ? null : new Date(value.getTime());
  if (typeof value === "number") {
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? null : date;
  }

  const raw = String(value).trim();
  if (!raw) return null;

  if (ISO_WITH_ZONE.test(raw)) {
    const zonedDate = new Date(raw);
    return Number.isNaN(zonedDate.getTime()) ? null : zonedDate;
  }

  if (ISO_DATE_ONLY.test(raw) || ISO_NAIVE.test(raw)) {
    return buildUtcDateFromNaive(raw);
  }

  const fallback = new Date(raw);
  return Number.isNaN(fallback.getTime()) ? null : fallback;
}

function getFormatter(includeSeconds: boolean, timeZone: string) {
  return new Intl.DateTimeFormat(EASYPRO_LOCALE, {
    timeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    ...(includeSeconds ? { second: "2-digit" } : {}),
  });
}

function getDateParts(date: Date, timeZone: string) {
  const formatter = new Intl.DateTimeFormat("en-CA", {
    timeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });

  const partMap = Object.fromEntries(
    formatter
      .formatToParts(date)
      .filter((part) => part.type !== "literal")
      .map((part) => [part.type, part.value])
  ) as Record<string, string>;

  return {
    year: partMap.year,
    month: partMap.month,
    day: partMap.day,
    hour: partMap.hour,
    minute: partMap.minute,
  };
}

export function formatDateTime(value: string | number | Date | null | undefined, options: FormatDateTimeOptions = {}) {
  const { includeSeconds = true, strategy = "utc" } = options;
  const date = parseDateValue(value, strategy);
  if (!date) return value == null ? "" : String(value);
  const timeZone = strategy == "utc" ? EASYPRO_TIME_ZONE : "UTC";
  return getFormatter(includeSeconds, timeZone).format(date);
}

export function toDateTimeLocalValue(value: string | number | Date | null | undefined, options: DateTimeLocalOptions = {}) {
  const { strategy = "utc" } = options;
  const date = parseDateValue(value, strategy);
  if (!date) return "";
  const timeZone = strategy == "utc" ? EASYPRO_TIME_ZONE : "UTC";
  const parts = getDateParts(date, timeZone);
  return `${parts.year}-${parts.month}-${parts.day}T${parts.hour}:${parts.minute}`;
}

export function getCurrentBogotaDateTimeLocalValue() {
  return toDateTimeLocalValue(new Date(), { strategy: "utc" });
}

export { EASYPRO_LOCALE, EASYPRO_TIME_ZONE };
