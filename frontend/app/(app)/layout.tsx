import { AppShell } from "@/components/app-shell/app-shell";
import { UserProvider } from "@/lib/user-context";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <UserProvider>
      <AppShell>{children}</AppShell>
    </UserProvider>
  );
}
