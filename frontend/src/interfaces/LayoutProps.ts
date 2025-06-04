export interface LayoutProps {
  params: Promise<{ locale: string }>;
  children: React.ReactNode;
}
