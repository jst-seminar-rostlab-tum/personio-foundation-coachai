export interface ReviewCreate {
  rating: number;
  comment: string;
  sessionId: string;
  allowAdminAccess: boolean;
}
export interface Review {
  id: string;
  userId: string;
  userEmail: string;
  sessionId: string | null;
  rating: number;
  comment: string;
  date: string;
}

export interface RatingStatistics {
  average: number;
  numFiveStar: number;
  numFourStar: number;
  numThreeStar: number;
  numTwoStar: number;
  numOneStar: number;
}

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
