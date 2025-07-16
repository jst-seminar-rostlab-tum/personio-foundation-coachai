'use client';

import { ChevronDown, Star } from 'lucide-react';
import { useLocale, useTranslations } from 'next-intl';
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/Button';
import Progress from '@/components/ui/Progress';
import { Review, ReviewsPaginated } from '@/interfaces/models/Review';
import { reviewService } from '@/services/ReviewService';
import { showErrorToast } from '@/lib/utils/toast';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/Select';
import { useRouter } from 'next/navigation';
import EmptyListComponent from '@/components/common/EmptyListComponent';
import { formatDateFlexible } from '@/lib/utils/formatDateAndTime';
import { api } from '@/services/ApiClient';

export default function Reviews({ ratingStatistics, reviews, pagination }: ReviewsPaginated) {
  const limit = pagination?.pageSize;
  const router = useRouter();
  const locale = useLocale();
  const tCommon = useTranslations('Common');
  const tAdmin = useTranslations('Admin');
  const [visibleCount, setVisibleCount] = useState(limit);
  const [pageNumber, setPageNumber] = useState(pagination?.currentPage);
  const [isLoading, setIsLoading] = useState(false);
  const [sortBy, setSortBy] = useState('newest');
  const canLoadMore = visibleCount < pagination?.totalCount;
  const [reviewsStorage, setReviewsStorage] = useState<Review[]>(reviews);

  const handleReviewClick = (sessionId: string | null) => {
    if (sessionId) {
      router.push(`/feedback/${sessionId}`);
    }
  };

  const handleLoadMore = (newPage: number) => {
    setPageNumber(newPage);
  };

  const handleSortChange = async (value: string) => {
    setSortBy(value);
    setPageNumber(1);
    setVisibleCount(limit);
    try {
      setIsLoading(true);
      const response = await reviewService.getPaginatedReviews(api, 1, limit, value);
      setReviewsStorage(response.reviews);
    } catch (e) {
      showErrorToast(e, tCommon('error'));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const getSessions = async () => {
      try {
        setIsLoading(true);
        const response = await reviewService.getPaginatedReviews(api, pageNumber, limit, sortBy);
        setReviewsStorage((prev) => [...prev, ...response.reviews]);
        setVisibleCount((prev) => prev + limit);
      } catch (e) {
        showErrorToast(e, tCommon('error'));
      } finally {
        setIsLoading(false);
      }
    };
    if (canLoadMore && pageNumber > 1) {
      getSessions();
    }
  }, [pageNumber, canLoadMore, limit, tCommon, sortBy]);

  return (
    <div>
      <div className="w-full max-w-5xl mx-auto my-16 px-4 md:px-16">
        <div className="flex flex-col md:flex-row items-center gap-9 md:gap-20">
          <div className="flex flex-col items-center justify-center w-max mx-auto gap-1">
            <div className="flex items-end text-7xl whitespace-nowrap mb-2 font-medium text-bw-70 leading-none">
              {ratingStatistics?.average?.toFixed(1) ?? 'N/A'}
              <span className="text-5xl font-normal text-bw-40 leading-none ml-2">/</span>
              <span className="text-5xl font-normal text-bw-40 leading-none ml-2">5</span>
            </div>
            <div className="flex gap-1 mb-2">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`w-8 h-8 ${i < Math.round(ratingStatistics?.average ?? 0) ? 'fill-marigold-40' : 'fill-bw-20'}`}
                  strokeWidth={0}
                />
              ))}
            </div>
            <div className="text-md font-normal text-bw-40 text-center w-full">
              {pagination?.totalCount ?? 'N/A'} Bewertungen
            </div>
          </div>
          <div className="flex flex-col space-y-6 w-full max-w-full min-w-0">
            {[5, 4, 3, 2, 1].map((num, idx) => {
              const count = [
                ratingStatistics?.numFiveStar,
                ratingStatistics?.numFourStar,
                ratingStatistics?.numThreeStar,
                ratingStatistics?.numTwoStar,
                ratingStatistics?.numOneStar,
              ][idx];
              const percentage = (count / (pagination?.totalCount ?? 0)) * 100;
              return (
                <div key={num} className="flex items-center w-full justify-end">
                  <span className="mr-4 flex items-center justify-end gap-x-1 text-sm text-bw-70 font-semibold text-right items-center w-10">
                    {num}
                    <Star className="w-6 h-6 fill-marigold-40" strokeWidth={0} />
                  </span>
                  <Progress className="h-2.5 flex-1 min-w-0" value={percentage} />
                  <span className="text-sm text-bw-40 w-6 text-right">{count ?? 'N/A'}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
      {!reviewsStorage || reviewsStorage.length === 0 ? (
        <EmptyListComponent itemType={tCommon('reviews')} />
      ) : (
        <div className="w-full mb-8 text-left">
          <div className="flex items-center justify-between mb-4">
            <div className="text-lg font-semibold text-bw-70">{tCommon('reviews')}</div>
            <Select value={sortBy} onValueChange={handleSortChange}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder={tAdmin('sortBy')} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="newest">{tAdmin('sortNewest')}</SelectItem>
                <SelectItem value="oldest">{tAdmin('sortOldest')}</SelectItem>
                <SelectItem value="highest">{tAdmin('sortHighest')}</SelectItem>
                <SelectItem value="lowest">{tAdmin('sortLowest')}</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {reviewsStorage?.slice(0, visibleCount).map((review) => (
              <div
                onClick={() => review.allowAdminAccess && handleReviewClick(review.sessionId)}
                key={review.id}
                className={`border border-bw-20 rounded-lg bg-transparent p-4 flex flex-col items-start ${
                  review.sessionId && review.allowAdminAccess
                    ? 'cursor-pointer'
                    : 'cursor-not-allowed'
                } transition-all duration-300 hover:shadow-md`}
              >
                <div className="flex items-center mb-2">
                  <span className="text-sm font-semibold text-bw-70">{review.userEmail}</span>
                </div>
                <div className="flex items-center mb-2">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className={`w-5 h-5 mr-1 ${i < review.rating ? 'fill-marigold-30' : 'fill-bw-20'}`}
                      strokeWidth={0}
                    />
                  ))}
                </div>
                <div className="text-sm text-bw-70 mb-2">{review.comment}</div>
                <div className="text-sm text-bw-40">{formatDateFlexible(review.date, locale)}</div>
              </div>
            ))}
          </div>
        </div>
      )}
      {canLoadMore && (
        <div className="flex justify-center mt-4">
          <Button variant="ghost" onClick={() => handleLoadMore(pageNumber + 1)}>
            {isLoading ? tCommon('loading') : tCommon('loadMore')} <ChevronDown />
          </Button>
        </div>
      )}
    </div>
  );
}
