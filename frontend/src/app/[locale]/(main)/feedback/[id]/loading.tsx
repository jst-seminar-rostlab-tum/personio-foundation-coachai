import Link from 'next/link';
import { useTranslations } from 'next-intl';

export default function FeedbackDetailLoadingPage() {
  const tCommon = useTranslations('Common');

  return (
    <div>
      {/* Header */}
      <div className="flex items-center gap-8">
        <Link href="/dashboard">
          <button className="w-8 h-8 bg-gray-200 rounded-lg flex items-center justify-center text-gray-700 font-bold text-lg hover:bg-gray-300 transition-colors">
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        </Link>
        <div className="text-xl font-bold text-gray-700">Feedback & Analysis</div>
      </div>

      {/* Performance Summary Section */}
      <div className="mb-8 flex flex-row items-stretch gap-4">
        <div className="flex-1">
          <div className="text-lg font-bold text-gray-400 mb-4">Performance Summary</div>
          {[1, 2, 3].map((_, i) => (
            <div key={i} className="mb-4">
              <div className="flex items-center justify-between mb-1">
                <div className="h-4 w-24 bg-gray-200 rounded animate-pulse" />
                <div className="h-4 w-10 bg-gray-200 rounded animate-pulse" />
              </div>
              <div className="w-full h-2 bg-gray-100 rounded">
                <div
                  className="h-2 bg-gray-300 rounded animate-pulse"
                  style={{ width: `${70 + i * 7}%` }}
                />
              </div>
            </div>
          ))}
        </div>
        <div className="flex items-center">
          <div className="w-20 h-20 bg-gray-200 rounded-full flex items-center justify-center animate-pulse">
            <div className="w-8 h-8 bg-gray-300 rounded-full" />
          </div>
        </div>
      </div>

      {/* Separator */}
      <div className="w-full h-px bg-gray-200 mb-6" />

      {/* 2x2 Small Stat Grid */}
      <div className="grid grid-cols-2 md:flex md:flex-row gap-4 w-full mb-8">
        {[1, 2, 3, 4].map((_, i) => (
          <div
            key={i}
            className="bg-gray-100 rounded-lg p-3 flex flex-col items-center animate-pulse w-full"
          >
            <div className="h-4 w-10 bg-gray-200 rounded mb-1" />
            <div className="h-3 w-16 bg-gray-200 rounded" />
          </div>
        ))}
      </div>

      {/* Separator */}
      <div className="w-full h-px bg-gray-200 mb-6" />

      {/* Full width section with round button, heading, subheading */}
      <div className="w-full flex items-center gap-4 bg-gray-50 p-4 rounded-lg shadow-md mb-8">
        <button className="w-14 h-14 bg-gray-200 rounded-full flex-shrink-0 flex items-center justify-center animate-pulse">
          <svg
            className="w-12 h-12 text-gray-400"
            fill="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <polygon points="9.5,7.5 16.5,12 9.5,16.5" />
          </svg>
        </button>
        <div className="flex flex-col flex-1">
          <div className="h-5 w-1/3 bg-gray-200 rounded mb-2 animate-pulse" />
          <div className="h-4 w-2/3 bg-gray-100 rounded animate-pulse" />
        </div>
      </div>

      {/* 1x2 Small Stat Grid */}
      <div className="grid grid-cols-2 gap-4 w-full mb-8">
        {[1, 2].map((_, i) => (
          <div
            key={i}
            className="bg-gray-100 rounded-lg p-3 flex flex-col items-center animate-pulse w-full"
          >
            <div className="h-4 w-10 bg-gray-200 rounded mb-1" />
            <div className="h-3 w-16 bg-gray-200 rounded" />
          </div>
        ))}
      </div>

      {/* Skeleton Accordions */}
      <div className="space-y-4 w-full mb-8">
        {[1, 2, 3].map((_, i) => (
          <div key={i} className="bg-gray-100 rounded-lg shadow-md animate-pulse">
            {/* Accordion Header */}
            <div className="flex items-center justify-between p-4 cursor-pointer">
              <div className="h-5 w-32 bg-gray-200 rounded" />
              <div className="h-5 w-5 bg-gray-200 rounded-full" />
            </div>
          </div>
        ))}
      </div>

      {/* Return to dashboard button */}
      <div className="w-full flex justify-center pb-8">
        <Link href="/dashboard" className="text-gray-400 hover:text-gray-500 text-sm underline">
          {tCommon('backToDashboard')}
        </Link>
      </div>
    </div>
  );
}
