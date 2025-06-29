import { useRef, useState } from 'react';
import { Message, MessageSender } from '@/interfaces/models/Simulation';

export function useMessageReducer() {
  const [messages, setMessages] = useState<Message[]>([]);
  const nextIdRef = useRef(1);

  const addPlaceholderMessage = (sender: MessageSender) => {
    const currentId = nextIdRef.current;
    nextIdRef.current = currentId + 1;
    setMessages((prev) => [
      // Filter out previous empty placeholder for same sender
      ...prev.filter((msg) => !(msg.text === '' && msg.sender === sender)),
      { id: currentId, sender, text: '' },
    ]);
  };

  const appendDeltaToLastMessage = (sender: MessageSender, delta: string) => {
    setMessages((prev) => {
      const idx = prev.findLastIndex((msg) => msg.sender === sender);
      if (idx === -1) return prev;

      const updatedMsg = {
        ...prev[idx],
        text: prev[idx].text + (delta ?? ''),
      };

      return [...prev.slice(0, idx), updatedMsg, ...prev.slice(idx + 1)];
    });
  };

  return {
    messages,
    setMessages,
    addPlaceholderMessage,
    appendDeltaToLastMessage,
  };
}
