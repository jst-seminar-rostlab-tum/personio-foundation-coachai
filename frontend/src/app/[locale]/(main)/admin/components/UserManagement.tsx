import { useTranslations } from 'next-intl';
import React from 'react';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/Accordion';
import type { UserPaginationResponse } from '@/interfaces/models/UserProfile';
import UsersList from './UsersList';

interface UsersProp {
  usersPaginationData: UserPaginationResponse;
}

export default function UserManagement({ usersPaginationData }: UsersProp) {
  const t = useTranslations('Admin');

  return (
    <Accordion type="multiple">
      <AccordionItem value="item-1">
        <AccordionTrigger>{t('userManagement')}</AccordionTrigger>
        <AccordionContent>
          <UsersList {...usersPaginationData} />
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
