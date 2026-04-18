import { NotaryCrmWorkspace } from "@/components/notaries/notary-crm-workspace";

export default async function CommercialNotaryDetailPage({ params }: { params: Promise<{ notaryId: string }> }) {
  const { notaryId } = await params;
  return <NotaryCrmWorkspace notaryId={Number(notaryId)} />;
}
