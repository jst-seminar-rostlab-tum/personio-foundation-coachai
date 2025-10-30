import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { getTranslations } from 'next-intl/server';
import React from 'react';

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/privacy', false);
}

type Topic = {
  heading?: string;
  content: string | string[];
};

type Section = {
  title?: string;
  content?: string | string[];
  topics?: Topic[];
};

type Sections = Record<string, Section>;

type Segment = { type: 'para'; lines: string[] } | { type: 'list'; items: string[] };

const TEXT_CLASSES = 'text-base leading-loose whitespace-pre-line break-words' as const;
const BULLET_PREFIX = '●\t' as const;

function toArray(value?: string | string[]): string[] {
  if (value == null) return [];
  return Array.isArray(value) ? value : [value];
}

function parseTextSegments(text: string): Segment[] {
  const lines = text.split('\n');
  const segments: Segment[] = [];
  let current: Segment | null = null;

  for (const line of lines) {
    const isBullet = line.startsWith(BULLET_PREFIX);

    if (isBullet) {
      if (current?.type === 'para') {
        segments.push(current);
        current = null;
      }
      if (!current || current.type !== 'list') {
        current = { type: 'list', items: [] };
      }
      current.items.push(line.slice(BULLET_PREFIX.length).trim());
    } else {
      if (current?.type === 'list') {
        segments.push(current);
        current = null;
      }
      if (!current || current.type !== 'para') {
        current = { type: 'para', lines: [] };
      }
      current.lines.push(line);
    }
  }

  if (current) segments.push(current);
  return segments;
}

const Paragraph = React.memo<{ text: string; k: string }>(({ text, k }) => {
  if (!text) return null;

  const segments = parseTextSegments(text);

  return (
    <div className="flex flex-col gap-2">
      {segments.map((seg, i) => {
        if (seg.type === 'para') {
          const block = seg.lines.join('\n').trim();
          if (!block) return null;
          return (
            <p key={`${k}-p-${i}`} className={TEXT_CLASSES}>
              {block}
            </p>
          );
        }
        return (
          <ul key={`${k}-ul-${i}`} className={`list-disc pl-6 space-y-1 ${TEXT_CLASSES}`}>
            {seg.items.map((item, j) => (
              <li key={`${k}-li-${i}-${j}`}>{item}</li>
            ))}
          </ul>
        );
      })}
    </div>
  );
});

Paragraph.displayName = 'Paragraph';

const Topic = React.memo<{ topic: Topic; sectionKey: string; idx: number }>(
  ({ topic, sectionKey, idx }) => {
    const topicParas = toArray(topic.content);
    return (
      <div className="flex flex-col gap-3">
        {topic.heading && <h3 className="text-lg font-semibold">{topic.heading}</h3>}
        {topicParas.map((tp, j) => (
          <Paragraph
            key={`${sectionKey}-topic-${idx}-${j}`}
            k={`${sectionKey}-topic-${idx}-${j}`}
            text={tp}
          />
        ))}
      </div>
    );
  }
);

Topic.displayName = 'Topic';

const SectionContent = React.memo<{ section: Section; sectionKey: string }>(
  ({ section, sectionKey }) => {
    const paragraphs = toArray(section.content);

    return (
      <div className="flex flex-col gap-4">
        {section.title && <h2 className="text-xl font-semibold">{section.title}</h2>}

        {paragraphs.map((p, i) => (
          <Paragraph key={`${sectionKey}-p-${i}`} k={`${sectionKey}-p-${i}`} text={p} />
        ))}

        {section.topics && section.topics.length > 0 && (
          <div className="flex flex-col gap-4">
            {section.topics.map((topic, idx) => (
              <Topic
                key={`${sectionKey}-topic-${idx}`}
                topic={topic}
                sectionKey={sectionKey}
                idx={idx}
              />
            ))}
          </div>
        )}
      </div>
    );
  }
);

SectionContent.displayName = 'SectionContent';

export default async function PrivacyPolicyPage() {
  const t = await getTranslations('PrivacyPolicy');
  const sections = (await t.raw('sections')) as Sections;

  return (
    <div className="flex flex-col justify-between min-h-screen">
      <section className="flex flex-col gap-8">
        <h1 className="text-4xl font-semibold break-words">{t('title')}</h1>
        {Object.entries(sections).map(([key, section]) => (
          <SectionContent key={key} section={section} sectionKey={key} />
        ))}
      </section>
    </div>
  );
}
