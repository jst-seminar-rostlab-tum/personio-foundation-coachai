import Link from 'next/link';
import { generateMetadata as generateDynamicMetadata } from '@/lib/metadata';
import type { Metadata } from 'next';
import type { Props } from '@/interfaces/Props';

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  return generateDynamicMetadata(locale, '/login', true);
}

export default function LoginPage() {
  return (
    <div className="  flex flex-col lg:flex-row">
      {/* Left Side (Desktop only) */}
      <div className="hidden lg:flex flex-col justify-between flex-1 bg-gray-200 p-8 h-[calc(100vh-4rem)]">
        {/* Large X for image placeholder */}
        <div className="relative flex-1 flex items-center justify-center">
          <div className="absolute top-8 left-8 text-2xl font-bold text-gray-400">
            Leadership Coach
          </div>
        </div>
        <div className="mt-8">
          <div className="text-2xl font-bold text-gray-400 mb-2">
            Develop exceptional leadership skills with AI coaching
          </div>
          <div className="text-gray-400">
            Join thousands of HR professionals and team leaders who are improving their soft skills
            with our AI training platform.
          </div>
        </div>
      </div>
      {/* Right Side (Auth Skeleton) */}
      <div className="flex flex-col items-center justify-center flex-1 px-4 py-8 bg-gray-50 lg:bg-white lg:rounded-lg lg:shadow-md lg:max-w-xl lg:mx-auto">
        {/* Logo */}
        <div className="w-12 h-12 bg-gray-200 rounded-full mb-4 animate-pulse" />
        {/* Title */}
        <div className="w-2/3 h-6 bg-gray-200 rounded mb-2 animate-pulse" />
        {/* Subtitle */}
        <div className="w-1/2 h-4 bg-gray-100 rounded mb-4 animate-pulse" />
        {/* Demo Banner */}
        <div className="w-full h-8 bg-gray-100 rounded mb-4 animate-pulse" />
        {/* Continue Button */}
        <Link href="/onboarding" className="w-2/3 mb-6">
          <button className="w-full h-10 bg-gray-200 rounded font-semibold text-gray-700 hover:bg-gray-300 transition-colors flex items-center justify-center gap-2">
            Continue to Demo
            <svg
              className="w-4 h-4 ml-1"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </Link>
        {/* Tabs */}
        <div className="flex w-full mb-4">
          <div className="w-1/2 h-8 bg-gray-200 rounded-l animate-pulse" />
          <div className="w-1/2 h-8 bg-gray-100 rounded-r animate-pulse" />
        </div>
        {/* Form Fields */}
        <div className="w-full space-y-4">
          <div className="w-full h-4 bg-gray-200 rounded animate-pulse" />
          <div className="w-full h-10 bg-gray-100 rounded animate-pulse" />
          <div className="w-full h-4 bg-gray-200 rounded animate-pulse" />
          <div className="w-full h-10 bg-gray-100 rounded animate-pulse" />
        </div>
        {/* Sign In Button */}
        <div className="w-full h-10 bg-gray-200 rounded mt-6 animate-pulse" />
        {/* Google Button */}
        <div className="w-full h-10 bg-gray-200 rounded mt-4 animate-pulse" />
      </div>
    </div>
  );
}
