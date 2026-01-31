import React from 'react';
import { type FieldPath, type FieldValues } from 'react-hook-form';

/**
 * Context value for the active form field.
 */
export type FormFieldContextValue<
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>,
> = {
  name: TName;
};

/**
 * Context value for a form item container.
 */
export type FormItemContextValue = {
  id: string;
};

/**
 * Provides the current form field name to descendants.
 */
export const FormFieldContext = React.createContext<FormFieldContextValue>(
  {} as FormFieldContextValue
);

/**
 * Provides the current form item ID to descendants.
 */
export const FormItemContext = React.createContext<FormItemContextValue>(
  {} as FormItemContextValue
);
