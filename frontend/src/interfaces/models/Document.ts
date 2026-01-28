/**
 * Document metadata used in resources and quotes.
 */
export interface Document {
  id: string;
  title: string;
  quote: string;
  author?: string;
  page?: number;
  chapter?: string;
  sourceUrl?: string;
  documentName?: string;
}

/**
 * Response wrapper for a list of documents.
 */
export interface DocumentsResponse {
  documents: Document[];
}
