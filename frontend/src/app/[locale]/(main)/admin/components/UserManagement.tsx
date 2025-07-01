'use client';

import { useTranslations } from 'next-intl';
import React from 'react';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/Accordion';
import UsersList from './UsersList';

interface User {
  userId: string;
  fullName: string;
  email: string;
  professionalRole: string;
  accountRole: string;
}
interface UsersProp {
  users: {
    users: User[];
    totalCount: number;
  };
}

export default function UserManagement({ users }: UsersProp) {
  const t = useTranslations('Admin');

  return (
    <Accordion type="multiple">
      <AccordionItem value="item-1">
        <AccordionTrigger>{t('userManagement')}</AccordionTrigger>
        <AccordionContent>
          <UsersList
            initialUsers={users.users.map((u) => ({
              ...u,
              id: u.userId,
            }))}
            totalCount={users.totalCount}
            initialPage={1}
            pageSize={10}
          />
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
