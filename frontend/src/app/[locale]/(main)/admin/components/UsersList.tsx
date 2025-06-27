'use client';

import { useEffect, useState } from 'react';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/Accordion';
import { Button } from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { UserProfileService as ClientUserProfileService } from '@/services/client/UserProfileService';
import { showErrorToast } from '@/lib/toast';

interface User {
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
    <Accordion type="multiple" className="mt-8">
      <AccordionItem value="users">
        <AccordionTrigger>Users</AccordionTrigger>
        <AccordionContent>
          <div className="mb-4">
            <Input
              type="text"
              placeholder="Search by email..."
              value={search}
              onChange={handleSearch}
              className="w-full mb-2"
            />
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm table-fixed">
              <thead>
                <tr>
                  <th className="text-left font-semibold py-2 px-2">Name</th>
                  <th className="text-left font-semibold py-2 px-2">Email</th>
                  <th className="text-left font-semibold py-2 px-2">Role</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.email} className="border-t">
                    <td className="py-2 px-2 truncate">{user.fullName}</td>
                    <td className="py-2 px-2 truncate">{user.email}</td>
                    <td className="py-2 px-2 truncate">{user.accountRole}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {hasMore && (
            <div className="flex justify-center mt-4">
              <Button onClick={handleLoadMore} disabled={loading} variant="ghost">
                {loading ? 'Loading...' : 'Load More'}
              </Button>
            </div>
          )}
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
