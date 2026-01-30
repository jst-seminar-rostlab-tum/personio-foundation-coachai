import React, { useContext, MouseEvent, KeyboardEvent } from 'react';

/**
 * Context value for the rating components.
 */
export type RatingContextValue = {
  value: number;
  readOnly: boolean;
  hoverValue: number | null;
  focusedStar: number | null;
  handleValueChange: (
    event: MouseEvent<HTMLButtonElement> | KeyboardEvent<HTMLButtonElement>,
    value: number
  ) => void;
  handleKeyDown: (event: KeyboardEvent<HTMLButtonElement>) => void;
  setHoverValue: (value: number | null) => void;
  setFocusedStar: (value: number | null) => void;
};

/**
 * Provides rating state to child components.
 */
export const RatingContext = React.createContext<RatingContextValue | null>(null);

/**
 * Hook to access the current rating context.
 */
export const useRating = () => {
  const context = useContext(RatingContext);
  if (!context) {
    throw new Error('useRating must be used within a Rating component');
  }
  return context;
};
