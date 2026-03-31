import { cn } from "@/components/ui/utils";

type LogoBadgeProps = {
  initials: string;
  compact?: boolean;
};

export function LogoBadge({ initials, compact = false }: LogoBadgeProps) {
  return (
    <div
      className={cn(
        "flex items-center justify-center rounded-2xl bg-primary text-white shadow-soft",
        compact ? "h-10 w-10 text-sm" : "h-14 w-14 text-lg",
      )}
    >
      <span className="font-semibold tracking-[0.18em]">{initials}</span>
    </div>
  );
}
