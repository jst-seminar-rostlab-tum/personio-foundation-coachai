/**
 * Payload for creating a review.
 */
export interface ReviewCreate {
  rating: number;
  comment: string;
  sessionId: string;
  allowAdminAccess: boolean;
}
/**
 * Review entity returned from the API.
 */
export interface Review {
  id: string;
  userId: string;
  userEmail: string;
  sessionId: string | null;
  rating: number;
  comment: string;
  date: string;
  allowAdminAccess: boolean;
}

/**
 * Aggregated rating statistics for reviews.
 */
export interface RatingStatistics {
  average: number;
  numFiveStar: number;
  numFourStar: number;
  numThreeStar: number;
  numTwoStar: number;
  numOneStar: number;
}

/**
 * Paginated review response with statistics.
 */
export interface ReviewsPaginated {
  reviews: Review[];
  pagination: {
    currentPage: number;
    totalPages: number;
    totalCount: number;
    pageSize: number;
  };
  ratingStatistics: RatingStatistics;
}
