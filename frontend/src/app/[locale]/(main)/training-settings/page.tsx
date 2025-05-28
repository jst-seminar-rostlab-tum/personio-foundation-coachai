import Link from 'next/link';

import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import type { Props } from '@/interfaces/Props';

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/training-settings', true);
}

export default function TrainingSettingsPage() {
  return (
    <div>
      <div className="flex items-center justify-between">
        <div className="text-xl font-bold text-gray-700">Training Settings</div>
        <Link href="/dashboard">
          <button className="px-3 py-2 bg-gray-200 rounded text-gray-700 text-sm">
            Back to Dashboard
          </button>
        </Link>
      </div>

      {/* Accordion Sections */}
      <div className="mt-6 space-y-4">
        <div className="">
          <button className="w-full px-4 py-3 flex items-center justify-between bg-gray-50 hover:bg-gray-100 rounded-t-lg">
            <span className="font-medium text-gray-700">Data Storage Preferences</span>
            <svg
              className="w-5 h-5 text-gray-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>
          <div className="p-4 bg-white rounded-b-lg">
            <div className="space-y-4">
              <div className="h-4 bg-gray-200 rounded w-3/4 animate-pulse"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2 animate-pulse"></div>
            </div>
          </div>
        </div>

        <div className="">
          <button className="w-full px-4 py-3 flex items-center justify-between bg-gray-50 hover:bg-gray-100 rounded-t-lg">
            <span className="font-medium text-gray-700">Privacy Controls</span>
            <svg
              className="w-5 h-5 text-gray-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>
          <div className="p-4 bg-white rounded-b-lg">
            <div className="space-y-4">
              <div className="h-4 bg-gray-200 rounded w-3/4 animate-pulse"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2 animate-pulse"></div>
            </div>
          </div>
        </div>

        <div className="">
          <button className="w-full px-4 py-3 flex items-center justify-between bg-gray-50 hover:bg-gray-100 rounded-t-lg">
            <span className="font-medium text-gray-700">Personalization Settings</span>
            <svg
              className="w-5 h-5 text-gray-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>
          <div className="p-4 bg-white rounded-b-lg">
            <div className="space-y-4">
              <div className="h-24 bg-gray-200 rounded w-5/6 animate-pulse"></div>
              <div className="h-4 bg-gray-200 rounded w-3/4 animate-pulse"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2 animate-pulse"></div>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 w-full sm:w-auto sm:flex sm:justify-end">
        <button className="w-full sm:w-auto px-6 py-2 bg-gray-200 rounded animate-pulse text-gray-700">
          Save Settings
        </button>
      </div>
    </div>
  );
}
