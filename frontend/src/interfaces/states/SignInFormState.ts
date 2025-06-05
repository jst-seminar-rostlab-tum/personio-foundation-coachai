import z from 'zod/v4';
import { $ZodErrorTree } from 'zod/v4/core';
import { signInFormSchema } from '../schemas';

export interface SignInFormState {
  formData?: FormData;
  validationErrors?: $ZodErrorTree<z.infer<typeof signInFormSchema>>;
  error?: string;
}
