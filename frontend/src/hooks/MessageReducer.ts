import { Message, MessageSender } from '@/interfaces/models/Session';
import { useRef, useState } from 'react';

export function useMessageReducer() {
  const [messages, setMessages] = useState<Message[]>([]);
  const nextIdRef = useRef(1);
  const messagesRef = useRef(messages);

  messagesRef.current = messages;

  const addPlaceholderMessage = (sender: MessageSender, startOffsetMs: number) => {
    const currentId = nextIdRef.current;
    setMessages((prev: Message[]) => {
      const filtered = prev.filter((msg) => !(msg.text === '' && msg.sender === sender));
      return [...filtered, { id: currentId, text: '', sender, startOffsetMs }];
    });
    nextIdRef.current += 1;
  };

  const appendDeltaToLastMessage = (sender: MessageSender, delta: string) => {
    setMessages((prev: Message[]) => {
      const idx = prev.findLastIndex((msg) => msg.sender === sender);
      if (idx === -1) return prev;
      const updatedMsg = { ...prev[idx], text: prev[idx].text + (delta ?? '') };
      return [...prev.slice(0, idx), updatedMsg, ...prev.slice(idx + 1)];
    });
  };

  const getLastMessageStartOffsetMsBySender = (sender: MessageSender): number | undefined => {
    return [...messagesRef.current].reverse().find((msg) => msg.sender === sender)?.startOffsetMs;
  };

  return {
    messages,
    setMessages,
    addPlaceholderMessage,
    appendDeltaToLastMessage,
    getLastMessageStartOffsetMsBySender,
  };
}
