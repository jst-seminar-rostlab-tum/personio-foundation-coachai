'use client';

import { useActionState, useRef } from 'react';
import { signUpAction } from '../../app/[locale]/(auth)/login/actions';

export function SignUpForm() {
  const formRef = useRef<HTMLFormElement>(null);
  const [state, formAction, isPending] = useActionState(signUpAction, {});

  return (
    <form ref={formRef} action={formAction} className="flex flex-col gap-4">
      <label htmlFor="">E-mail</label>
      <input
        type="email"
        name="email"
        placeholder="Enter your email"
        required
        defaultValue={state.formData?.get('email')?.toString() || ''}
        className="border rounded px-3 py-2"
      />
      {state.validationErrors?.properties?.email && (
        <span className="text-red-500 text-sm ml-2">
          {state.validationErrors.properties?.email.errors.map((error: string, idx: number) => (
            <div key={idx}>{error}</div>
          ))}
        </span>
      )}

      <label htmlFor="">Password</label>
      <input
        type="password"
        name="password"
        placeholder="Enter your password"
        required
        defaultValue={state.formData?.get('password')?.toString() || ''}
        className="border rounded px-3 py-2"
      />
      {state.validationErrors?.properties?.password && (
        <span className="text-red-500 text-sm ml-2">
          {state.validationErrors.properties?.password.errors.map((error: string, idx: number) => (
            <div key={idx}>{error}</div>
          ))}
        </span>
      )}

      <label htmlFor="">Phone number</label>
      <input
        type="tel"
        name="phone"
        placeholder="Enter your phone number"
        required
        defaultValue={state.formData?.get('phone')?.toString() || ''}
        className="border rounded px-3 py-2"
      />
      {state.validationErrors?.properties?.phone && (
        <span className="text-red-500 text-sm ml-2">
          {state.validationErrors.properties?.phone.errors.map((error: string, idx: number) => (
            <div key={idx}>{error}</div>
          ))}
        </span>
      )}

      <button
        type="submit"
        disabled={isPending}
        className="bg-blue-500 text-white px-4 py-2 rounded"
      >
        Sign Up
      </button>
      {state.error && <span className="text-red-500 text-sm ml-2">{state.error}</span>}
    </form>
  );
}
