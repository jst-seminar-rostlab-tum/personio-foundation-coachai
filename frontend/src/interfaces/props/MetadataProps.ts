export interface MetadataProps {
  params: Promise<{ locale: string }>;
  searchParams?: Promise<{ step?: string }>;
}
