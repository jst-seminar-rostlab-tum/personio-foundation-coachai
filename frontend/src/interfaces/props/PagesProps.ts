/**
 * Params for locale-aware routes with an ID.
 */
type Params = Promise<{ locale: string; id: string }>;

/**
 * Page props containing params.
 */
export type PagesProps = { params: Params };
