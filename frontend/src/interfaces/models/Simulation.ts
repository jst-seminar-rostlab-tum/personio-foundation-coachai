export interface Message {
  id?: number;
  text: string;
  sender: 'user' | 'assistant';
  start_offset_ms?: number;
  end_offset_ms?: number;
  created_at?: string;
}

export enum MessageSender {
  USER = 'user',
  ASSISTANT = 'assistant',
}
