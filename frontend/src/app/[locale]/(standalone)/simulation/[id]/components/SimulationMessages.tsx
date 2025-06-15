'use client';

import React, { useEffect, useRef, useState } from 'react';

const mockMessages = [
  {
    id: 1,
    text: "Thanks for meeting with me today. I wanted to discuss the project deadlines you've missed recently.",
    sender: 'assistant',
  },
  {
    id: 2,
    text: "I understand. I know things haven't been on schedule lately.",
    sender: 'user',
  },
  {
    id: 3,
    text: 'Several tasks that were due last week are still unfinished...',
    sender: 'assistant',
  },
  {
    id: 4,
    text: 'Oops...',
    sender: 'user',
  },
  {
    id: 5,
    text: "Can you help me understand what's been causing these delays?",
    sender: 'assistant',
  },
  {
    id: 6,
    text: "I've been struggling with managing multiple tasks simultaneously. Sometimes I feel overwhelmed.",
    sender: 'user',
  },
  {
    id: 7,
    text: 'I appreciate your honesty. Have you considered using any project management tools to help stay organized?',
    sender: 'assistant',
  },
  {
    id: 8,
    text: "No, I haven't really explored those options yet.",
    sender: 'user',
  },
  {
    id: 9,
    text: "I'd be happy to show you some tools that our team uses. They've really helped us stay on track.",
    sender: 'assistant',
  },
  {
    id: 10,
    text: 'That would be really helpful, thank you.',
    sender: 'user',
  },
  {
    id: 11,
    text: "Let's set up a time tomorrow to go through them together. In the meantime, which current task is your highest priority?",
    sender: 'assistant',
  },
  {
    id: 12,
    text: 'The client presentation for the marketing campaign is probably the most urgent right now.',
    sender: 'user',
  },
];

export interface Message {
  id?: number;
  text: string;
  sender: 'user' | 'assistant';
  start_offset_ms?: number;
  end_offset_ms?: number;
  created_at?: string;
}

interface MessageItemProps {
  message: Message;
}

// Component to render each text chunk with a fade-in
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

    // If new text is appended, isolate the delta chunk
    if (curr.startsWith(prev)) {
      const delta = curr.slice(prev.length);
      if (delta) {
        setChunks((prevChunks) => [...prevChunks, delta]);
      }
    } else {
      // If the text was replaced or reset, start fresh
      setChunks([curr]);
    }

    prevTextRef.current = curr;
  }, [message.text]);

  return (
    <div
      className={`text-base text-bw-90 rounded-xl px-4 py-2 max-w-[70%] ${
        message.sender === 'user'
          ? 'self-end bg-marigold-30 rounded-br-none'
          : 'self-start bg-white border border-marigold-30 rounded-bl-none'
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

export default function SimulationMessages({ messages = mockMessages }: { messages?: Message[] }) {
  const messageEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col gap-4 py-2 h-full">
      {messages.map((msg) => (
        <MessageItem key={msg.id} message={msg} />
      ))}
      <div ref={messageEndRef} />
    </div>
  );
}
