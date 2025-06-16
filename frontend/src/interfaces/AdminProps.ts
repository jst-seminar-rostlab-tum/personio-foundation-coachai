import { Review, ReviewsPaginated } from './Review';

export interface RatingStatistics {
  average: number;
  numFiveStar: number;
  numFourStar: number;
  numThreeStar: number;
  numTwoStar: number;
  numOneStar: number;
}

export interface Pagination {
  currentPage: number;
  totalPages: number;
  totalCount: number;
}

export interface ReviewsData {
  reviews: Review[];
  pagination: Pagination;
  ratingStatistics: RatingStatistics;
}

export interface AdminProps {
  stats: {
    totalUsers: number;
    totalTrainings: number;
    totalReviews: number;
    averageScore: number;
    dailyTokenLimit: number;
  };
  reviews: ReviewsPaginated;
}
