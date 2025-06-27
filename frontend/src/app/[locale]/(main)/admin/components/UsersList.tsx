'use client';

import { useEffect, useState } from 'react';
import { Search, ChevronDown, Trash2 } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { Button } from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { UserProfileService as ClientUserProfileService } from '@/services/client/UserProfileService';
import { showErrorToast } from '@/lib/toast';
import { DeleteUserHandler } from '@/components/common/DeleteUserHandler';

interface User {
  userId: string;
  fullName: string;
  email: string;
  professionalRole: string;
  accountRole: string;
}

interface UsersListProps {
  initialUsers: User[];
  totalCount: number;
  initialPage: number;
  pageSize: number;
}

export default function UsersList({
  initialUsers,
  totalCount,
  initialPage,
  pageSize,
}: UsersListProps) {
  const [users, setUsers] = useState<User[]>(initialUsers);
  const [page, setPage] = useState(initialPage);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [hasMore, setHasMore] = useState(users.length < totalCount);
  const t = useTranslations('Common');

  const fetchUsers = async (pageNum: number, searchStr: string) => {
    setLoading(true);
    try {
      const data = await ClientUserProfileService.getPaginatedUsers({
        page: pageNum,
        pageSize,
        emailSubstring: searchStr || undefined,
      });
      setUsers(data.users);
      setHasMore(data.users.length < data.totalCount);
    } catch (e) {
      showErrorToast(e, 'Error loading users');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
    setPage(1);
    fetchUsers(1, e.target.value);
  };

  const handleLoadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    fetchUsers(nextPage, search);
  };

  useEffect(() => {
    setHasMore(users.length < totalCount);
  }, [users, totalCount]);

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
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm table-fixed">
          <colgroup>
            <col style={{ width: '40%' }} />
            <col style={{ width: '30%' }} />
            <col style={{ width: '20%' }} />
            <col style={{ width: '10%' }} />
          </colgroup>
          <thead>
            <tr>
              <th className="text-left font-semibold text-bw-70 py-2 px-2">{t('name')}</th>
              <th className="text-left font-semibold text-bw-70 py-2 px-2">{t('email')}</th>
              <th className="text-left font-semibold text-bw-70 py-2 px-2">{t('role')}</th>
              <th className="text-left font-semibold text-bw-70 py-2 px-2">{t('actions')}</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.email} className="border-t border-bw-10">
                <td className="py-2 px-2 truncate">{user.fullName}</td>
                <td className="py-2 px-2 truncate">{user.email}</td>
                <td className="py-2 px-2 truncate">{user.accountRole}</td>
                <td className="py-2 px-2">
                  <DeleteUserHandler
                    id={user.userId}
                    onSuccess={() =>
                      setUsers((prev) => prev.filter((u) => u.userId !== user.userId))
                    }
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
            {loading ? t('loading') : t('loadMore')}
            <ChevronDown className="ml-2 w-4 h-4" />
          </Button>
        </div>
      )}
    </>
  );
}
