'use server';

import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';

import { createClient } from '@/utils/supabase/server';
import {
  SignInWithPasswordCredentials,
  SignUpWithPasswordCredentials,
} from '@supabase/supabase-js';
import { SignInFormState, SignUpFormState } from '@/interfaces/states';
import { signInFormSchema, signUpFormSchema } from '@/interfaces/schemas';
import z from 'zod/v4';

// eslint-disable-next-line consistent-return
export async function signInAction(
  prevState: SignInFormState,
  formData: FormData
): Promise<SignInFormState> {
  const validatedFormData = signInFormSchema.safeParse(Object.fromEntries(formData));
  if (!validatedFormData.success) {
    return {
      ...prevState,
      formData,
      validationErrors: z.treeifyError(validatedFormData.error),
    };
  }

  const supabase = await createClient();

  const credentials: SignInWithPasswordCredentials = {
    email: validatedFormData.data.email,
    password: validatedFormData.data.password,
  };
  const { error } = await supabase.auth.signInWithPassword(credentials);
  if (error) {
    return {
      ...prevState,
      formData,
      error: error.message,
    };
  }

  revalidatePath('/', 'layout');
  redirect('/');
}

// eslint-disable-next-line consistent-return
export async function signUpAction(
  prevState: SignUpFormState,
  formData: FormData
): Promise<SignUpFormState> {
  const validatedFormData = signUpFormSchema.safeParse(Object.fromEntries(formData));
  if (!validatedFormData.success) {
    return {
      ...prevState,
      formData,
      validationErrors: z.treeifyError(validatedFormData.error),
    };
  }

  // TODO: handle phone number verification before creating the user

  const supabase = await createClient();

  const credentials: SignUpWithPasswordCredentials = {
    email: validatedFormData.data.email,
    password: validatedFormData.data.password,
    phone: validatedFormData.data.phone,
  };
  const { error } = await supabase.auth.signUp(credentials);
  if (error) {
    return {
      ...prevState,
      formData,
      error: error.message,
    };
  }

  revalidatePath('/', 'layout');
  redirect('/');
}
