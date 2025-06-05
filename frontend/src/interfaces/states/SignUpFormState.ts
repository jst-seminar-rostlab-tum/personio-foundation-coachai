import z from 'zod/v4';
import { $ZodErrorTree } from 'zod/v4/core';
import { signUpFormSchema } from '../schemas';

export interface SignUpFormState {
  formData?: FormData;
  validationErrors?: $ZodErrorTree<z.infer<typeof signUpFormSchema>>;
  error?: string;
}
