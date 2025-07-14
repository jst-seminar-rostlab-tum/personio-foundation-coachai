import Link from 'next/link';

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center py-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-lg shadow-md border border-bw-20">
          {/* Card Header */}
          <div className="p-6 border-b border-bw-20">
            <div className="h-6 w-32 bg-bw-10 rounded mb-2 animate-pulse" />
            <div className="h-4 w-48 bg-bw-10 rounded animate-pulse" />
          </div>

          {/* Card Content */}
          <div className="p-6">
            {/* Tabs */}
            <div className="flex mb-6">
              <div className="flex-1 h-10 bg-bw-20 rounded-l animate-pulse" />
              <div className="flex-1 h-10 bg-bw-10 rounded-r animate-pulse" />
            </div>

            {/* Tab Content */}
            <div className="space-y-4">
              <div className="h-4 w-24 bg-bw-10 rounded animate-pulse" />
              <div className="h-10 w-full bg-bw-10 rounded animate-pulse" />
              <div className="h-4 w-20 bg-bw-10 rounded animate-pulse" />
              <div className="h-10 w-full bg-bw-10 rounded animate-pulse" />
              <div className="h-10 w-full bg-bw-20 rounded animate-pulse" />
              <div className="h-10 w-full bg-bw-10 rounded animate-pulse" />
            </div>
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
