import { z } from 'zod/v4';

export const signUpFormSchema = z.object({
  email: z.email({ message: 'Please enter a valid email.' }).trim(),
  password: z
    .string()
    .min(8, { message: 'Password must be at least 8 characters long' })
    .max(64, { message: 'Password must be at most 64 characters long' })
    .regex(/[A-Z]/, { message: 'Password must contain at least one uppercase letter' })
    .regex(/[a-z]/, { message: 'Password must contain at least one lowercase letter' })
    .regex(/[0-9]/, { message: 'Password must containt at least one number' })
    .regex(/[\W_]/, { message: 'Password must contain at least one special character' })
    .trim(),
  phone: z.string().trim(),
});

export type SignUpFormSchemaProps = z.infer<typeof signUpFormSchema>;
