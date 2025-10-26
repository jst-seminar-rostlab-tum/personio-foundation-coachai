'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Message } from '@/interfaces/models/Session';

interface MessageItemProps {
  message: Message;
}

interface SessionMessagesProps {
  messages: Message[];
}

const Chunk: React.FC<{ text: string }> = ({ text }) => {
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const frame = requestAnimationFrame(() => setVisible(true));
    return () => cancelAnimationFrame(frame);
  }, []);

  return (
    <span className={`transition-opacity duration-300 ${visible ? 'opacity-100' : 'opacity-0'}`}>
      {text}
    </span>
  );
};

const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  const [chunks, setChunks] = useState<string[]>([message.text]);
  const prevTextRef = useRef(message.text);

  useEffect(() => {
    const prev = prevTextRef.current;
    const curr = message.text;

    if (curr.startsWith(prev)) {
      const delta = curr.slice(prev.length);
      if (delta) {
        setChunks((prevChunks) => [...prevChunks, delta]);
      }
    } else {
      setChunks([curr]);
    }

    prevTextRef.current = curr;
  }, [message.text]);

  return (
    <div
      className={`text-base text-bw-90 rounded-xl px-4 py-2 max-w-[70%] ${
        message.sender === 'user'
          ? 'self-end bg-custom-beige rounded-br-none'
          : 'self-start border border-custom-beige rounded-bl-none'
      }`}
    >
      <span className="inline">
        {chunks.map((chunk, index) => (
          <Chunk key={index} text={chunk} />
        ))}
      </span>
    </div>
  );
};

export default function SessionMessages({ messages }: SessionMessagesProps) {
  const messageEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="w-full max-w-7xl mx-auto px-[clamp(1.25rem,4vw,4rem)] flex flex-col gap-4 py-2 h-full">
      {messages.map((msg) => (
        <MessageItem key={msg.id} message={msg} />
      ))}
      <div ref={messageEndRef} />
    </div>
  );
}
