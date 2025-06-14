import { RatingContextValue } from '@/interfaces/Rating';
import React from 'react';

export const RatingContext = React.createContext<RatingContextValue | null>(null);
