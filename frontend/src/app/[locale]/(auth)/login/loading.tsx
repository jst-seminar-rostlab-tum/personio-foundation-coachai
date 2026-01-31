/**
 * Shows a skeleton UI while the login page loads.
 */
export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center py-4 bg-bw-5">
      <div className="w-full max-w-md rounded-2xl shadow-lg p-10 flex flex-col items-center gap-4">
        {/* Title */}
        <div className="h-8 w-80 bg-bw-40 rounded-lg mb-1 animate-pulse" />
        {/* Subtitle */}
        <div className="h-5 w-64 bg-bw-40 rounded-lg mb-4 animate-pulse" />
        {/* Tabs */}
        <div className="flex w-full gap-2 mb-6">
          <div className="flex-1 h-10 bg-bw-40 rounded-lg animate-pulse" />
          <div className="flex-1 h-10 bg-bw-40 rounded-lg animate-pulse" />
        </div>
        {/* Email Label */}
        <div className="h-5 w-32 bg-bw-40 rounded mb-2 animate-pulse self-start" />
        {/* Email Input */}
        <div className="h-12 w-full bg-bw-40 rounded-lg mb-4 animate-pulse" />
        {/* Password Label */}
        <div className="h-5 w-24 bg-bw-40 rounded mb-2 animate-pulse self-start" />
        {/* Password Input */}
        <div className="h-12 w-full bg-bw-40 rounded-lg mb-6 animate-pulse" />
        {/* Sign In Button */}
        <div className="h-12 w-full bg-bw-40 rounded-lg mb-4 animate-pulse" />
        {/* Forgot Password Link */}
        <div className="h-5 w-40 bg-bw-40 rounded mx-auto animate-pulse" />
      </div>
    </div>
  );
}
