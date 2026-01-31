/**
 * Layout props with locale params and children.
 */
export interface LayoutProps {
  params: Promise<{ locale: string }>;
  children: React.ReactNode;
}
