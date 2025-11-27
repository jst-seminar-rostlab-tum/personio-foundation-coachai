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

import { Search, ChevronDown, ArrowUp, ArrowDown } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { Button } from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import EmptyListComponent from '@/components/common/EmptyListComponent';
import { UserProfileService as ClientUserProfileService } from '@/services/UserProfileService';
import { api } from '@/services/ApiClient';
import { DeleteUserHandler } from '@/components/common/DeleteUserHandler';
import {
  UserProfile as User,
  UserPaginationResponse,
  SortOption,
  SessionLimitType,
} from '@/interfaces/models/UserProfile';
import { showErrorToast } from '@/lib/utils/toast';
import { adminService } from '@/services/AdminService';
import { useAdminStatsStore } from '@/store/AdminStatsStore';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/Select';
import { USER_LIST_PAGE, USER_LIST_LIMIT } from '../constants/UsersList';
import UserDialog from './UserDialog';

export default function UsersList({
  users,
  totalUsers: initialTotalUsers,
}: UserPaginationResponse) {
  const [userList, setUserList] = useState<User[]>(users);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [totalUsers, setTotalUsers] = useState(initialTotalUsers);
  const [limit, setLimit] = useState(USER_LIST_LIMIT);
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [sessionLimitFilter, setSessionLimitFilter] = useState<SessionLimitType[] | null>(null);
  const [emailSorting, setEmailSorting] = useState<SortOption | null>(null);
  const [sessionLimitSorting, setSessionLimitSorting] = useState<SortOption | null>(null);
  const { setStats } = useAdminStatsStore();
  const t = useTranslations('Admin');
  const tCommon = useTranslations('Common');

  const getSessionLimitFilterValue = (
    sessionLimitFilterValue: SessionLimitType[] | null
  ): SessionLimitType => {
    if (sessionLimitFilterValue === null) return SessionLimitType.ALL;
    return sessionLimitFilterValue[0] === SessionLimitType.DEFAULT
      ? SessionLimitType.DEFAULT
      : SessionLimitType.INDIVIDUAL;
  };

  const fetchUsers = async (
    newLimit: number,
    searchStr: string,
    sessionLimitTypeFilter?: SessionLimitType[] | null,
    emailSort?: SortOption | null,
    sessionLimitSort?: SortOption | null
  ) => {
    setLoading(true);
    try {
      const sessionLimitTypeArray =
        sessionLimitTypeFilter && sessionLimitTypeFilter.length > 0
          ? sessionLimitTypeFilter
          : undefined;

      const data = await ClientUserProfileService.getPaginatedUsers(
        api,
        USER_LIST_PAGE,
        newLimit,
        searchStr || undefined,
        sessionLimitTypeArray,
        emailSort || undefined,
        sessionLimitSort || undefined
      );
      setTotalUsers(data.totalUsers);
      setUserList(data.users);
    } catch (e) {
      showErrorToast(e, 'Error loading users');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = e.target;
    setSearch(value);
    setLimit(USER_LIST_LIMIT);
    fetchUsers(USER_LIST_LIMIT, value, sessionLimitFilter, emailSorting, sessionLimitSorting);
  };

  const handleSessionLimitFilterChange = (value: string) => {
    let newFilter: SessionLimitType[] | null = null;
    if (value === SessionLimitType.DEFAULT) {
      newFilter = [SessionLimitType.DEFAULT];
    } else if (value === SessionLimitType.INDIVIDUAL) {
      newFilter = [SessionLimitType.INDIVIDUAL];
    } else if (value === SessionLimitType.ALL) {
      newFilter = null;
    }
    setSessionLimitFilter(newFilter);
    setLimit(USER_LIST_LIMIT);
    fetchUsers(USER_LIST_LIMIT, search, newFilter, emailSorting, sessionLimitSorting);
  };

  const handleEmailSortingChange = (value: string) => {
    let newSort: SortOption | null = null;
    if (value === SortOption.ASC) {
      newSort = SortOption.ASC;
    } else if (value === SortOption.DESC) {
      newSort = SortOption.DESC;
    } else if (value === SortOption.NONE) {
      newSort = null;
    }
    setEmailSorting(newSort);
    if (newSort) {
      setSessionLimitSorting(null);
    }
    setLimit(USER_LIST_LIMIT);
    fetchUsers(USER_LIST_LIMIT, search, sessionLimitFilter, newSort, null);
  };

  const handleSessionLimitSortingChange = (value: string) => {
    let newSort: SortOption | null = null;
    if (value === SortOption.ASC) {
      newSort = SortOption.ASC;
    } else if (value === SortOption.DESC) {
      newSort = SortOption.DESC;
    } else if (value === SortOption.NONE) {
      newSort = null;
    }
    setSessionLimitSorting(newSort);
    if (newSort) {
      setEmailSorting(null);
    }
    setLimit(USER_LIST_LIMIT);
    fetchUsers(USER_LIST_LIMIT, search, sessionLimitFilter, null, newSort);
  };

  const handleLoadMore = async () => {
    const nextLimit = limit + USER_LIST_LIMIT;
    setLimit(nextLimit);
    fetchUsers(nextLimit, search, sessionLimitFilter, emailSorting, sessionLimitSorting);
  };

  const showLoadMoreUsersButton = () => userList.length < totalUsers;

  const onDeleteSuccess = async () => {
    try {
      fetchUsers(limit, search, sessionLimitFilter, emailSorting, sessionLimitSorting);
      const data = await adminService.getAdminStats(api);
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleUserClick = (userId: string) => {
    setSelectedUserId(userId);
    setIsDialogOpen(true);
  };

  const handleDialogClose = () => {
    setIsDialogOpen(false);
    setSelectedUserId(null);
  };

  const renderSortIndicator = (sortOption: SortOption | null) => {
    if (sortOption === SortOption.ASC) {
      return <ArrowUp className="w-4 h-4 text-bw-70" />;
    }
    if (sortOption === SortOption.DESC) {
      return <ArrowDown className="w-4 h-4 text-bw-70" />;
    }
    return null;
  };

  return (
    <>
      <div className="mt-4 mb-4 flex flex-col gap-4">
        <div className="relative w-full sm:max-w-sm">
          <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-bw-70">
            <Search className="w-4 h-4" />
          </span>
          <Input
            type="text"
            placeholder={t('search')}
            value={search}
            onChange={handleSearch}
            className="w-full pl-10 pr-3 py-2 border border-bw-40 rounded text-sm text-bw-70 placeholder-bw-50 focus:border-bw-40 focus-visible:outline-none focus-visible:ring-0"
          />
        </div>
        <div className="flex flex-col sm:flex-row gap-4 items-end">
          <div className="w-full sm:w-auto flex flex-col gap-1">
            <label className="text-sm font-medium text-bw-70">{t('filterBySessionLimit')}</label>
            <Select
              value={getSessionLimitFilterValue(sessionLimitFilter)}
              onValueChange={handleSessionLimitFilterChange}
            >
              <SelectTrigger className="w-full sm:w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={SessionLimitType.ALL}>{t('all')}</SelectItem>
                <SelectItem value={SessionLimitType.DEFAULT}>{t('default')}</SelectItem>
                <SelectItem value={SessionLimitType.INDIVIDUAL}>{t('individual')}</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="w-full sm:w-auto flex flex-col gap-1">
            <label className="text-sm font-medium text-bw-70">{t('sortByEmail')}</label>
            <Select
              value={emailSorting === null ? SortOption.NONE : emailSorting}
              onValueChange={handleEmailSortingChange}
            >
              <SelectTrigger className="w-full sm:w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={SortOption.NONE}>{t('noSort')}</SelectItem>
                <SelectItem value={SortOption.ASC}>{t('ascending')}</SelectItem>
                <SelectItem value={SortOption.DESC}>{t('descending')}</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="w-full sm:w-auto flex flex-col gap-1">
            <label className="text-sm font-medium text-bw-70">{t('sortBySessionLimit')}</label>
            <Select
              value={sessionLimitSorting === null ? SortOption.NONE : sessionLimitSorting}
              onValueChange={handleSessionLimitSortingChange}
            >
              <SelectTrigger className="w-full sm:w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={SortOption.NONE}>{t('noSort')}</SelectItem>
                <SelectItem value={SortOption.ASC}>{t('ascending')}</SelectItem>
                <SelectItem value={SortOption.DESC}>{t('descending')}</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>
      {userList.length === 0 && !loading ? (
        <EmptyListComponent itemType={t('users')} />
      ) : (
        <>
          <div className="overflow-x-auto rounded-lg border border-bw-40 mb-4 w-full">
            <Table className="min-w-[320px] text-sm table-fixed">
              <TableHeader>
                <TableRow>
                  <TableHead className="text-left font-semibold text-bw-70 px-6 py-4 w-[280px]">
                    <div className="flex items-center gap-2">
                      {t('email')}
                      {renderSortIndicator(emailSorting)}
                    </div>
                  </TableHead>
                  <TableHead className="text-left font-semibold text-bw-70 px-6 py-4">
                    <div className="flex items-center gap-2">
                      {t('dailySessionLimit')}
                      {renderSortIndicator(sessionLimitSorting)}
                    </div>
                  </TableHead>
                  <TableHead className="text-right font-semibold text-bw-70 pl-0 pr-6 py-4"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {userList.map((user) => (
                  <TableRow
                    key={user.email}
                    className="border-t border-bw-50 hover:bg-bw-5 cursor-pointer"
                    onClick={() => handleUserClick(user.userId)}
                  >
                    <TableCell className="px-6 py-4 text-bw-70 w-[280px]">{user.email}</TableCell>
                    <TableCell className="px-6 py-4 text-bw-70">
                      {user.dailySessionLimit ?? '-'}
                    </TableCell>
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
      <UserDialog
        userId={selectedUserId}
        isOpen={isDialogOpen}
        onClose={handleDialogClose}
        onUpdate={() => {
          // Refresh the user list when session limit is updated
          fetchUsers(limit, search, sessionLimitFilter, emailSorting, sessionLimitSorting);
        }}
      />
    </>
  );
}
