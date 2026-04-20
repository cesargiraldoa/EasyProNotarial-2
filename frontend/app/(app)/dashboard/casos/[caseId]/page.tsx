import { CaseDetailWorkspace } from "@/components/cases/case-detail-workspace";

export default async function CaseDetailPage({
  params,
  searchParams,
}: {
  params: Promise<{ caseId: string }>;
  searchParams?: Promise<{ tab?: string | string[] }>;
}) {
  const { caseId } = await params;
  const resolvedSearchParams = searchParams ? await searchParams : undefined;
  const parsedCaseId = Number(caseId);
  const initialTab = Array.isArray(resolvedSearchParams?.tab) ? resolvedSearchParams?.tab[0] : resolvedSearchParams?.tab;

  if (!Number.isFinite(parsedCaseId) || parsedCaseId <= 0) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">El identificador de la minuta no es v?lido.</div>;
  }

  return <CaseDetailWorkspace caseId={parsedCaseId} initialTab={initialTab} />;
}
