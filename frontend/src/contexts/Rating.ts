import { RatingContextValue } from '@/interfaces/Rating';
import React, { useContext } from 'react';

export const RatingContext = React.createContext<RatingContextValue | null>(null);

export const useRating = () => {
  const context = useContext(RatingContext);
  if (!context) {
    throw new Error('useRating must be used within a Rating component');
  }
  return context;
};
