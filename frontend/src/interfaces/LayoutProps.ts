export interface Props {
  params: Promise<{ locale: string }>;
  children: React.ReactNode;
}
