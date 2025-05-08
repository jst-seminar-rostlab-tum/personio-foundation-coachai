export interface Message {
    id: number;
    content: string;
    created_at: string;
}

export interface ApiResponse<T> {
    data?: T;
    error?: string;
}

export interface PaginationParams {
    page?: number;
    limit?: number;
}
  