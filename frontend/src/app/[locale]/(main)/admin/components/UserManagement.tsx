'use client';

import { ChevronDown, Search, Trash2 } from 'lucide-react';
import { useTranslations } from 'next-intl';
import React, { useState } from 'react';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/Accordion';
import { Button } from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { DeleteUserHandler } from '@/components/common/DeleteUserHandler';

export default function UserManagement() {
  const t = useTranslations('Admin');
  const [visibleUsers, setVisibleUsers] = useState(5);

  const handleLoadMore = () => setVisibleUsers((v) => Math.min(v + 5, allUsers.length));

  const allUsers = [
    'Sara P.',
    'TheLegend27',
    'Jackson Lopez',
    'Maria Surname',
    'Alex Kim',
    'John Doe',
    'Jane Roe',
    'Chris Evans',
    'Sam Lee',
    'Patricia Surname',
  ];

  const canLoadMore = visibleUsers < allUsers.length;

  return (
    <Accordion type="multiple">
      <AccordionItem value="item-1">
        <AccordionTrigger>{t('userManagement')}</AccordionTrigger>
        <AccordionContent>
          <div className="mb-4">
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-bw-40">
                <Search className="w-4 h-4" />
              </span>
              <Input
                type="text"
                placeholder={t('search')}
                className="w-full pl-10 pr-3 py-2 border border-bw-20 rounded text-sm text-bw-70 placeholder-bw-40 focus:border-bw-20 focus-visible:outline-none focus-visible:ring-0"
              />
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm table-fixed">
              <colgroup>
                <col style={{ width: '70%' }} />
                <col style={{ width: '30%' }} />
              </colgroup>
              <thead>
                <tr>
                  <th className="text-left font-semibold text-bw-70 py-2 px-2">{t('users')}</th>
                  <th className="text-left font-semibold text-bw-70 py-2 px-2">{t('actions')}</th>
                </tr>
              </thead>
              <tbody>
                {allUsers.slice(0, visibleUsers).map((user) => (
                  <tr key={user} className="border-t border-bw-10">
                    <td className="py-2 px-2 truncate">{user}</td>
                    <td className="py-2 px-2">
                      <DeleteUserHandler id={user}>
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
          {canLoadMore && (
            <div className="flex justify-center mt-4">
              <Button variant="ghost" onClick={handleLoadMore}>
                {t('loadMore')} <ChevronDown className="ml-2 w-4 h-4" />
              </Button>
            </div>
          )}
        </AccordionContent>
      </AccordionItem>
      <AccordionItem value="item-2">
        <AccordionTrigger>{t('trainingCategories')}</AccordionTrigger>
        <AccordionContent></AccordionContent>
      </AccordionItem>
      <AccordionItem value="item-3">
        <AccordionTrigger>{t('trainingScenarios')}</AccordionTrigger>
        <AccordionContent></AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
