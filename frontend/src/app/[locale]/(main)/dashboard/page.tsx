import Link from 'next/link';

import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import type { Props } from '@/interfaces/LayoutProps';

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/dashboard', true);
}

export default function DashboardPage() {
  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="text-xl font-bold text-gray-700">Dashboard</div>
        <Link href="/new-training">
          <button className="px-3 py-2 bg-gray-200 rounded text-gray-700 text-sm">
            New Training
          </button>
        </Link>
      </div>

      {/* Simple Stats: 2x2 on small, 1x4 on large screens */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
        <div className="bg-gray-100 p-4 rounded-lg shadow-md animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-2/3 mb-2"></div>
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
        </div>
        <div className="bg-gray-100 p-4 rounded-lg shadow-md animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-2/3 mb-2"></div>
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
        </div>
        <div className="bg-gray-100 p-4 rounded-lg shadow-md animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-2/3 mb-2"></div>
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
        </div>
        <div className="bg-gray-100 p-4 rounded-lg shadow-md animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-2/3 mb-2"></div>
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
        </div>
      </div>

      {/* Current Training Section */}
      <div className="mt-6 w-full bg-gray-50 p-4 rounded-lg shadow-md">
        <div className="text-lg text-gray-400 font-semibold mb-2">Current Training</div>
        <div className="flex items-center justify-end bg-gray-100 p-4 rounded-lg shadow-md w-full">
          <Link href="/simulation/1">
            <button className="px-4 py-2 bg-gray-200 rounded text-gray-700 text-sm">
              Continue
            </button>
          </Link>
        </div>
      </div>

      {/* Recent Training Section */}
      <div className="mt-6 w-full bg-gray-50 p-4 rounded-lg shadow-md">
        <div className="text-lg text-gray-400 font-semibold mb-2">Recent Training History</div>
        <div className="space-y-4">
          {[1, 2].map((_, i) => (
            <div
              key={i}
              className="flex items-center justify-between bg-gray-100 p-4 rounded-lg shadow animate-pulse"
            >
              <div>
                <div className="h-4 bg-gray-200 rounded w-32 mb-2"></div>
                <div className="h-6 bg-gray-200 rounded w-48"></div>
              </div>
              <div className="h-8 w-8 bg-gray-200 rounded-full ml-4"></div>
            </div>
          ))}
        </div>
        <div className="mt-4 w-full">
          <Link href="/history" className="w-full block">
            <button className="px-4 py-2 w-full bg-gray-200 rounded text-gray-700 text-sm">
              View All Training History
            </button>
          </Link>
        </div>
      </div>

      {/* Placeholder Section 1 */}
      <div className="mt-6 w-full bg-gray-50 p-4 rounded-lg shadow-md">
        <div className="bg-gray-100 h-24 rounded animate-pulse" />
      </div>

      {/* Placeholder Section 2 */}
      <div className="mt-6 w-full bg-gray-50 p-4 rounded-lg shadow-md">
        <div className="bg-gray-100 h-16 rounded animate-pulse" />
      </div>
    </div>
  );
}
