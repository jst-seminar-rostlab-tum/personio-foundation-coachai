/**
 * Metadata generation props with locale params.
 */
export interface MetadataProps {
  params: Promise<{ locale: string }>;
}
