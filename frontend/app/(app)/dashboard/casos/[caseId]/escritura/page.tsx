import { EscrituraWorkspace } from "@/components/escritura/escritura-workspace";

export default async function EscrituraPage({
  params,
}: {
  params: Promise<{ caseId: string }>;
}) {
  const { caseId } = await params;
  const parsedCaseId = Number(caseId);

  if (!Number.isFinite(parsedCaseId) || parsedCaseId <= 0) {
    return <div className="ep-card rounded-[2rem] p-6 text-secondary">El identificador de la minuta no es valido.</div>;
  }

  return <EscrituraWorkspace caseId={parsedCaseId} />;
}
