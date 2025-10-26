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

export interface DocumentsResponse {
  documents: Document[];
}
