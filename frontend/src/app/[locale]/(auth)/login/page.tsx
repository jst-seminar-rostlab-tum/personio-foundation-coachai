'use client';

import { SignInForm, SignUpForm } from '@/interfaces/forms';
import { useState } from 'react';

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);

  return (
    <div className="max-w-md mx-auto mt-10 p-6 bg-white rounded shadow">
      <div className="flex justify-center mb-6">
        <button
          className={`px-4 py-2 rounded-l ${isLogin ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
          onClick={() => setIsLogin(true)}
        >
          Login
        </button>
        <button
          className={`px-4 py-2 rounded-r ${!isLogin ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
          onClick={() => setIsLogin(false)}
        >
          Sign Up
        </button>
      </div>
      {isLogin ? <SignInForm /> : <SignUpForm />}
    </div>
  );
}
