import { generateMetadata as generateDynamicMetadata } from '@/lib/utils/metadata';
import type { Metadata } from 'next';
import { getTranslations } from 'next-intl/server';
import React from 'react';

export async function generateMetadata({
  params,
}: {
  params: { locale: string };
}): Promise<Metadata> {
  const { locale } = params;
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

function toArray(value?: string | string[]): string[] {
  if (value == null) return [];
  if (Array.isArray(value)) return value;
  return [value];
}

function Paragraph({ text, k }: { text: string; k: string }) {
  if (!text) return null;

  const lines = text.split('\n');
  const textClasses = 'text-base leading-loose whitespace-pre-line break-words';

  type Seg = { type: 'para'; lines: string[] } | { type: 'list'; items: string[] };

  const segments: Seg[] = [];
  let current: Seg | null = null;

  for (const raw of lines) {
    const isBullet = raw.startsWith('●\t');

    if (isBullet) {
      // close a paragraph if we were in one
      if (current && current.type === 'para') {
        segments.push(current);
        current = null;
      }
      // start / continue a list
      if (!current || current.type !== 'list') {
        current = { type: 'list', items: [] };
      }
      current.items.push(raw.replace(/^●\t/, '').trim());
    } else {
      // close a list if we were in one
      if (current && current.type === 'list') {
        segments.push(current);
        current = null;
      }
      // start / continue a paragraph
      if (!current || current.type !== 'para') {
        current = { type: 'para', lines: [] };
      }
      current.lines.push(raw);
    }
  }
  if (current) segments.push(current);

  return (
    <div key={k} className="flex flex-col gap-2">
      {segments.map((seg, i) => {
        if (seg.type === 'para') {
          const block = seg.lines.join('\n').trim();
          if (!block) return null; // avoid empty <p> from blank separators
          return (
            <p key={`${k}-p-${i}`} className={textClasses}>
              {block}
            </p>
          );
        }
        return (
          <ul key={`${k}-ul-${i}`} className={`list-disc pl-6 space-y-1 ${textClasses}`}>
            {seg.items.map((item, j) => (
              <li key={`${k}-li-${i}-${j}`}>{item}</li>
            ))}
          </ul>
        );
      })}
    </div>
  );
}

export default async function PrivacyPolicyPage() {
  const t = await getTranslations('PrivacyPolicyCombined');
  const tCommon = await getTranslations('Common');

  const sections = (await t.raw('sections')) as Sections;
  const sectionKeys = Object.keys(sections);

  return (
    <div className="flex flex-col justify-between min-h-screen">
      <section className="flex flex-col gap-8">
        <h1 className="text-4xl font-semibold break-words">{tCommon('privacyPolicyCombined')}</h1>

        {sectionKeys.map((key) => {
          const sec = sections[key];
          if (!sec) return null;

          const paragraphs = toArray(sec.content);

          return (
            <div key={key} className="flex flex-col gap-4">
              {sec.title && <h2 className="text-xl font-semibold">{sec.title}</h2>}

              {paragraphs.map((p, i) => (
                <Paragraph key={`${key}-p-${i}`} k={`${key}-p-${i}`} text={p} />
              ))}

              {Array.isArray(sec.topics) && sec.topics.length > 0 && (
                <div className="flex flex-col gap-4">
                  {sec.topics.map((topic, idx) => {
                    const topicParas = toArray(topic.content);
                    return (
                      <div key={`${key}-topic-${idx}`} className="flex flex-col gap-3">
                        {topic.heading && (
                          <h3 className="text-lg font-semibold">{topic.heading}</h3>
                        )}
                        {topicParas.map((tp, j) => (
                          <Paragraph
                            key={`${key}-topic-${idx}-${j}`}
                            k={`${key}-topic-${idx}-${j}`}
                            text={tp}
                          />
                        ))}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </section>
    </div>
  );
}
