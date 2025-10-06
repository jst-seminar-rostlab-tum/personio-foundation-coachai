'use client';

import { useState } from 'react';
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
import { adminService } from '@/services/AdminService';
import { useAdminStatsStore } from '@/store/AdminStatsStore';
import { USER_LIST_INITIAL_PAGE, USER_LIST_LIMIT } from '../constants/UsersList';

export default function UsersList({
  users,
  totalUsers: initialTotalUsers,
}: UserPaginationResponse) {
  const [userList, setUserList] = useState<User[]>(users);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [totalUsers, setTotalUsers] = useState(initialTotalUsers);
  const [page, setPage] = useState(USER_LIST_INITIAL_PAGE);
  const { setStats } = useAdminStatsStore();
  const t = useTranslations('Admin');
  const tCommon = useTranslations('Common');

  const fetchUsers = async (nextPage: number, searchStr: string) => {
    setLoading(true);
    try {
      const data = await ClientUserProfileService.getPaginatedUsers(
        api,
        nextPage,
        USER_LIST_LIMIT,
        searchStr || undefined
      );
      setTotalUsers(data.totalUsers);
      return data.users;
    } catch (e) {
      showErrorToast(e, 'Error loading users');
      return [];
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = e.target;
    setSearch(value);
    setPage(USER_LIST_INITIAL_PAGE);
    setUserList(await fetchUsers(USER_LIST_INITIAL_PAGE, value));
  };

  const handleLoadMore = async () => {
    const nextPage = page + 1;
    setPage(nextPage);
    const moreUsers = await fetchUsers(nextPage, search);
    setUserList((prev) => [...prev, ...moreUsers]);
  };

  const showLoadMoreUsersButton = () => userList.length < totalUsers;

  const onDeleteSuccess = async () => {
    try {
      fetchUsers(page, search);
      const data = await adminService.getAdminStats(api);
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  return (
    <>
      <div className="mt-4 mb-4 flex flex-row gap-4 items-end">
        <div className="relative w-full sm:max-w-sm">
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
        </div>
      </div>
      {userList.length === 0 && !loading ? (
        <EmptyListComponent itemType={t('users')} />
      ) : (
        <>
          <div className="overflow-x-auto rounded-lg border border-bw-20 mb-4 w-full">
            <Table className="min-w-[320px] text-sm table-fixed">
              <TableHeader>
                <TableRow>
                  <TableHead className="text-left font-semibold text-bw-70 px-6 py-4 w-[280px]">
                    {t('email')}
                  </TableHead>
                  <TableHead className="text-right font-semibold text-bw-70 pl-0 pr-6 py-4"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {userList.map((user) => (
                  <TableRow key={user.email} className="border-t border-bw-10">
                    <TableCell className="px-6 py-4 text-bw-70 w-[280px]">{user.email}</TableCell>
                    <TableCell className="pl-0 pr-6 py-4 text-right">
                      <DeleteUserHandler id={user.userId} onDeleteSuccess={onDeleteSuccess} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          {showLoadMoreUsersButton() && (
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
