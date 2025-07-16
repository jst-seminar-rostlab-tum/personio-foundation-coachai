'use client';

import { useEffect, useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/Table';

import { Search, ChevronDown } from 'lucide-react';
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
      <div className="mt-4 mb-4 flex items-end justify-between">
        <div className="text-xl mb-4 font-medium text-bw-70">{t('users')}</div>
        <div className="relative min-w-[200px] max-w-md w-full">
          <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-bw-40">
            <Search className="w-4 h-4" />
          </span>
          <Input
            type="text"
            placeholder={t('search')}
            value={search}
            onChange={handleSearch}
            className="w-full max-w-md pl-10 pr-3 py-2 border border-bw-20 rounded text-sm text-bw-70 placeholder-bw-40 focus:border-bw-20 focus-visible:outline-none focus-visible:ring-0"
          />
        </div>
      </div>
      {userList.length === 0 && !loading ? (
        <EmptyListComponent itemType={t('users')} />
      ) : (
        <>
          <div className="overflow-x-auto rounded-lg border border-bw-20 mb-4 max-w-full">
            <Table className="min-w-full text-sm table-fixed">
              <TableHeader>
                <TableRow>
                  <TableHead className="text-left font-semibold text-bw-70 px-6 py-4">
                    {t('email')}
                  </TableHead>
                  <TableHead className="text-right font-semibold text-bw-70 px-6 py-4"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {userList.map((user) => (
                  <TableRow key={user.email} className="border-t border-bw-10">
                    <TableCell className="px-6 py-4 truncate text-bw-70">{user.email}</TableCell>
                    <TableCell className="px-6 py-4 text-right">
                      <DeleteUserHandler
                        id={user.userId}
                        onDeleteSuccess={() => {
                          setCurrentPage(1);
                          fetchUsers(1, search);
                        }}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
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
