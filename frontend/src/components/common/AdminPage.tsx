'use client';

import { ArrowRightIcon, ChevronDown, Search, Star, Trash2 } from 'lucide-react';
import { useTranslations } from 'next-intl';
import React from 'react';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '../ui/Accordion';
import { Button } from '../ui/Button';
import Progress from '../ui/Progress';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/Avatar';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/Select';
import StatCard from './StatCard';
import Input from '../ui/Input';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '../ui/AlertDialog';

export default function Admin() {
  const t = useTranslations('Admin');
  const tr = useTranslations('TrainingSettings');
  const stats = [
    { value: '11.200', label: t('statActiveUsers') },
    { value: '34.533', label: t('statTotalTrainings') },
    { value: '1.062', label: t('statReviews') },
    { value: '82%', label: t('statAverageScore') },
  ];
  const [visibleUsers, setVisibleUsers] = React.useState(5);
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
  const handleLoadMore = () => setVisibleUsers((v) => Math.min(v + 5, allUsers.length));
  return (
    <div className="px-2 sm:px-4 max-w-full">
      <div className="text-2xl font-bold text-bw-70 text-center mb-2">{t('dashboardTitle')}</div>
      <div className="text-sm text-bw-40 text-center mb-8">{t('dashboardSubtitle')}</div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((stat, i) => (
          <StatCard key={i} value={stat.value} label={stat.label} />
        ))}
      </div>
      <div className="w-full max-w-md mb-8 text-left">
        <label className="block text-bw-70 font-semibold text-sm mb-1">
          {t('tokensPerUserLabel')}
        </label>
        <Select defaultValue="100">
          <SelectTrigger className="w-full border border-bw-20 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bw-70 text-left">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="100">100</SelectItem>
            <SelectItem value="200">200</SelectItem>
            <SelectItem value="500">500</SelectItem>
            <SelectItem value="1000">1000</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="w-full max-w-md mb-8 text-left">
        <div className="text-lg font-semibold text-bw-70 mb-4">{t('userFeedback')}</div>
        <div className="flex flex-col sm:flex-row items-start gap-4">
          <div className="flex flex-col items-start justify-center min-w-0">
            <Star className="w-14 h-14 fill-marigold-30 mb-2" strokeWidth={0} />
            <div className="flex items-end whitespace-nowrap">
              <span className="text-2xl font-semibold text-bw-70 leading-none">4.7</span>
              <span className="text-2xl font-normal text-bw-40 leading-none ml-1">/ 5</span>
            </div>
          </div>
          <div className="flex flex-col space-y-2 w-full max-w-full">
            {[5, 4, 3, 2, 1].map((num, idx) => (
              <div key={num} className="flex items-center justify-end w-full">
                <Progress className="h-3 [&>div]:!bg-marigold-30" value={[80, 40, 15, 8, 2][idx]} />
                <span className="ml-3 text-sm text-bw-70 font-semibold w-6 text-right">{num}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
      <div className="w-full max-w-5xl mb-8 text-left">
        <div className="text-lg font-semibold text-bw-70 mb-4">{t('userFeedback')}</div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="border border-bw-20 rounded-lg bg-transparent p-4 flex flex-col items-start">
            <div className="flex items-center mb-2">
              <Avatar className="w-8 h-8 mr-3">
                <AvatarImage alt="Sara P." />
                <AvatarFallback>SP</AvatarFallback>
              </Avatar>
              <span className="text-sm font-semibold text-bw-70">Sara P.</span>
            </div>
            <div className="flex items-center mb-2">
              {[...Array(5)].map((_, i) => (
                <Star key={i} className="w-5 h-5 fill-marigold-30 mr-1" strokeWidth={0} />
              ))}
            </div>
            <div className="text-sm text-bw-70 mb-2">
              Great app! It helped me so much with mastering difficult conversations!
            </div>
            <div className="text-sm text-bw-40">18 Jul 2019</div>
          </div>
          <div className="border border-bw-20 rounded-lg bg-transparent p-4 flex flex-col items-start">
            <div className="flex items-center mb-2">
              <Avatar className="w-8 h-8 mr-3">
                <AvatarImage alt="TheLegend27" />
                <AvatarFallback>TL</AvatarFallback>
              </Avatar>
              <span className="text-sm font-semibold text-bw-70">TheLegend27</span>
            </div>
            <div className="flex items-center mb-2">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`w-5 h-5 mr-1 ${i < 4 ? 'fill-marigold-30' : 'fill-bw-20'}`}
                  strokeWidth={0}
                />
              ))}
            </div>
            <div className="text-sm text-bw-70 mb-2"></div>
            <div className="text-sm text-bw-40">20 Jan 2025</div>
          </div>
          <div className="border border-bw-20 rounded-lg bg-transparent p-4 flex flex-col items-start">
            <div className="flex items-center mb-2">
              <Avatar className="w-8 h-8 mr-3">
                <AvatarImage alt="Jackson Lopez" />
                <AvatarFallback>JL</AvatarFallback>
              </Avatar>
              <span className="text-sm font-semibold text-bw-70">Jackson Lopez</span>
            </div>
            <div className="flex items-center mb-2">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`w-5 h-5 mr-1 ${i === 0 ? 'fill-marigold-30' : 'fill-bw-20'}`}
                  strokeWidth={0}
                />
              ))}
            </div>
            <div className="text-sm text-bw-70 mb-2">I got brain damage.</div>
            <div className="text-sm text-bw-40">6 Dez 2023</div>
          </div>
        </div>
      </div>
      <Button size="full">
        {t('showAllReviews')}
        <ArrowRightIcon className="inline w-4 h-4 ml-2" />
      </Button>
      <Accordion type="multiple" className="w-full mt-8">
        <AccordionItem value="item-1" className="text-dark">
          <AccordionTrigger className="font-bw-70 cursor-pointer">
            {t('userManagement')}
          </AccordionTrigger>
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
                        <AlertDialog>
                          <AlertDialogTrigger asChild>
                            <Button
                              variant="ghost"
                              size="icon"
                              aria-label={t('deleteUser')}
                              className="hover:bg-flame-50"
                            >
                              <Trash2 className="w-4 h-4 text-bw-40" />
                            </Button>
                          </AlertDialogTrigger>
                          <AlertDialogContent>
                            <AlertDialogHeader>
                              <AlertDialogTitle>{tr('deleteAccountConfirmTitle')}</AlertDialogTitle>
                              <AlertDialogDescription>
                                {tr('deleteAccountConfirmDesc', { user })}
                              </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                              <AlertDialogCancel>{tr('cancel')}</AlertDialogCancel>
                              <AlertDialogAction>{tr('confirm')}</AlertDialogAction>
                            </AlertDialogFooter>
                          </AlertDialogContent>
                        </AlertDialog>
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
        <AccordionItem value="item-2" className="text-dark">
          <AccordionTrigger className="font-bw-70 cursor-pointer">
            {t('trainingCategories')}
          </AccordionTrigger>
          <AccordionContent></AccordionContent>
        </AccordionItem>
        <AccordionItem value="item-3" className="text-dark">
          <AccordionTrigger className="font-bw-70 cursor-pointer">
            {t('trainingScenarios')}
          </AccordionTrigger>
          <AccordionContent></AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}
