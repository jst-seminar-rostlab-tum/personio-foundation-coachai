'use client';

import { useEffect, useState } from 'react';
import { Search, ChevronDown, Trash2 } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { Button } from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import EmptyListComponent from '@/components/common/EmptyListComponent';
import { UserProfileService as ClientUserProfileService } from '@/services/UserProfileService';
import { api } from '@/services/ApiClient';
import { DeleteUserHandler } from '@/components/common/DeleteUserHandler';
import type { UserProfile as User, UserPaginationResponse } from '@/interfaces/models/UserProfile';
import { showErrorToast } from '@/lib/utils/toast';

export default function UsersList({
  users,
  totalUsers: initialTotalUsers,
  page,
  limit,
}: UserPaginationResponse) {
  const [userList, setUserList] = useState<User[]>(users);
  const [currentPage, setCurrentPage] = useState(page);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [totalUsers, setTotalUsers] = useState(initialTotalUsers);
  const [hasMore, setHasMore] = useState(users.length < initialTotalUsers);
  const t = useTranslations('Admin');
  const tCommon = useTranslations('Common');

  const fetchUsers = async (pageNum: number, searchStr: string) => {
    setLoading(true);
    try {
      const data = await ClientUserProfileService.getPaginatedUsers(
        api,
        pageNum,
        limit,
        searchStr || undefined
      );
      setUserList(data.users);
      setTotalUsers(data.totalUsers);
      setHasMore((pageNum - 1) * limit + data.users.length < data.totalUsers);
    } catch (e) {
      showErrorToast(e, 'Error loading users');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = e.target;
    setSearch(value);
    setCurrentPage(1);
    fetchUsers(1, value);
  };

  const handleLoadMore = () => {
    const nextPage = currentPage + 1;
    setCurrentPage(nextPage);
    fetchUsers(nextPage, search);
  };

  useEffect(() => {
    setHasMore((currentPage - 1) * limit + userList.length < totalUsers);
  }, [userList, totalUsers, currentPage, limit]);

  return (
    <>
      <div className="mb-4">
        <div className="relative">
          <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-bw-40">
            <Search className="w-4 h-4" />
          </span>
          <Input
            type="text"
            placeholder={t('search')}
            value={search}
            onChange={handleSearch}
            className="w-full pl-10 pr-3 py-2 border border-bw-20 rounded text-sm text-bw-70 placeholder-bw-40 focus:border-bw-20 focus-visible:outline-none focus-visible:ring-0"
          />
          {loading && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              <div className="h-5 w-16 bg-bw-10 rounded animate-pulse" />
            </div>
          )}
        </div>
      </div>
      {userList.length === 0 && !loading ? (
        <EmptyListComponent itemType={t('users')} />
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm table-fixed">
              <colgroup>
                <col style={{ width: '70%' }} />
                <col style={{ width: '30%' }} />
              </colgroup>
              <thead>
                <tr>
                  <th className="text-left font-semibold text-bw-70 py-2 px-2">{t('email')}</th>
                  <th className="text-left font-semibold text-bw-70 py-2 px-2">{t('actions')}</th>
                </tr>
              </thead>
              <tbody>
                {userList.map((user) => (
                  <tr key={user.email} className="border-t border-bw-10">
                    <td className="py-2 px-2 truncate">{user.email}</td>
                    <td className="py-2 px-2">
                      <DeleteUserHandler
                        id={user.userId}
                        onDeleteSuccess={() => {
                          setCurrentPage(1);
                          fetchUsers(1, search);
                        }}
                      >
                        <Button
                          variant="ghost"
                          size="icon"
                          aria-label={t('deleteUser')}
                          className="group"
                        >
                          <Trash2 className="w-4 h-4 text-bw-40 group-hover:text-flame-50" />
                        </Button>
                      </DeleteUserHandler>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {hasMore && (
            <div className="flex justify-center mt-4">
              <Button onClick={handleLoadMore} disabled={loading} variant="ghost">
                {loading ? tCommon('loading') : tCommon('loadMore')}
                <ChevronDown className="ml-2 w-4 h-4" />
              </Button>
            </div>
          )}
        </>
      )}
    </>
  );
}
