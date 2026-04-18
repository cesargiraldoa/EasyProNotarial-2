import { CaseDetailWorkspace } from "@/components/cases/case-detail-workspace";

export default async function CaseDetailPage({ params }: { params: Promise<{ caseId: string }> }) {
  const { caseId } = await params;
  const parsedCaseId = Number(caseId);

  if (!Number.isFinite(parsedCaseId) || parsedCaseId <= 0) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">El identificador de la minuta no es válido.</div>;
  }

  return <CaseDetailWorkspace caseId={parsedCaseId} />;
}

