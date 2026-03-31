"use client";

import { useEffect, useState } from "react";
import { formatDateTime } from "@/lib/datetime";

type LiveClockProps = {
  className?: string;
};

export function LiveClock({ className }: LiveClockProps) {
  const [now, setNow] = useState<Date | null>(null);

  useEffect(() => {
    const updateClock = () => setNow(new Date());
    updateClock();
    const timer = window.setInterval(updateClock, 1000);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <span className={className} suppressHydrationWarning>
      {now ? formatDateTime(now) : "--/--/----, --:--:--"}
    </span>
  );
}
