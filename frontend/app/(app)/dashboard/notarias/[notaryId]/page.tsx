import { NotaryDetailWorkspace } from "@/components/notaries/notary-detail-workspace";

export default async function NotaryDetailPage({ params }: { params: Promise<{ notaryId: string }> }) {
  const { notaryId } = await params;
  return <NotaryDetailWorkspace notaryId={Number(notaryId)} />;
}
