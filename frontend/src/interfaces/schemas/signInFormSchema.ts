import { z } from 'zod/v4';

export const signInFormSchema = z.object({
  email: z.email({ message: 'Please enter a valid email.' }).nonempty().trim(),
  password: z.string().nonempty().trim(),
});

export type SignInFormSchemaProps = z.infer<typeof signInFormSchema>;
