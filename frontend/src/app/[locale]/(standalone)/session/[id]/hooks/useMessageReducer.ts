import { Message, MessageSender } from '@/interfaces/models/Session';
import { useRef, useState, useCallback } from 'react';

/**
 * Manages message state for streaming chat updates.
 */
export function useMessageReducer() {
  const [messages, setMessages] = useState<Message[]>([]);
  const nextIdRef = useRef(1);
  const messagesRef = useRef(messages);

  messagesRef.current = messages;

  /**
   * Adds an empty placeholder message for a sender.
   */
  const addPlaceholderMessage = useCallback((sender: MessageSender) => {
    const currentId = nextIdRef.current;
    setMessages((prev: Message[]) => {
      const filtered = prev.filter((msg) => !(msg.text === '' && msg.sender === sender));
      return [...filtered, { id: currentId, text: '', sender }];
    });
    nextIdRef.current += 1;
  }, []);

  /**
   * Appends a text delta to the latest message for a sender.
   */
  const appendDeltaToLastMessage = useCallback((sender: MessageSender, delta: string) => {
    setMessages((prev: Message[]) => {
      const idx = prev.findLastIndex((msg) => msg.sender === sender);
      if (idx === -1) return prev;
      const updatedMsg = { ...prev[idx], text: prev[idx].text + (delta ?? '') };
      return [...prev.slice(0, idx), updatedMsg, ...prev.slice(idx + 1)];
    });
  }, []);

  return {
    messages,
    addPlaceholderMessage,
    appendDeltaToLastMessage,
  };
}
