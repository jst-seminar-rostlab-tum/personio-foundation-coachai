'use client';

import React, { useEffect, useRef, useState } from 'react';

const mockMessages = [
  {
    id: 1,
    text: "Thanks for meeting with me today. I wanted to discuss the project deadlines you've missed recently.",
    sender: 'other',
  },
  {
    id: 2,
    text: "I understand. I know things haven't been on schedule lately.",
    sender: 'user',
  },
  {
    id: 3,
    text: 'Several tasks that were due last week are still unfinished...',
    sender: 'other',
  },
  {
    id: 4,
    text: 'Oops...',
    sender: 'user',
  },
  {
    id: 5,
    text: "Can you help me understand what's been causing these delays?",
    sender: 'other',
  },
  {
    id: 6,
    text: "I've been struggling with managing multiple tasks simultaneously. Sometimes I feel overwhelmed.",
    sender: 'user',
  },
  {
    id: 7,
    text: 'I appreciate your honesty. Have you considered using any project management tools to help stay organized?',
    sender: 'other',
  },
  {
    id: 8,
    text: "No, I haven't really explored those options yet.",
    sender: 'user',
  },
  {
    id: 9,
    text: "I'd be happy to show you some tools that our team uses. They've really helped us stay on track.",
    sender: 'other',
  },
  {
    id: 10,
    text: 'That would be really helpful, thank you.',
    sender: 'user',
  },
  {
    id: 11,
    text: "Let's set up a time tomorrow to go through them together. In the meantime, which current task is your highest priority?",
    sender: 'other',
  },
  {
    id: 12,
    text: 'The client presentation for the marketing campaign is probably the most urgent right now.',
    sender: 'user',
  },
];

export default function SimulationMessages() {
  const [messages] = useState(mockMessages);
  const messageEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col gap-4 py-2 h-full">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`text-base text-bw-90 rounded-xl px-4 py-2 max-w-[70%] ${
            msg.sender === 'other'
              ? 'self-end bg-marigold-30 rounded-br-none'
              : 'self-start bg-white border border-marigold-30 rounded-bl-none'
          }`}
        >
          {msg.text}
        </div>
      ))}
      <div ref={messageEndRef} />
    </div>
  );
}
