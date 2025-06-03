import { ArrowRightIcon, Star } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '../ui/Accordion';
import { Button } from '../ui/Button';
import Progress from '../ui/Progress';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/Avatar';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/Select';
import StatCard from './StatCard';

export default function Admin() {
  const t = useTranslations('Admin');
  const stats = [
    { value: '11.200', label: t('statActiveUsers') },
    { value: '34.533', label: t('statTotalTrainings') },
    { value: '1.062', label: t('statReviews') },
    { value: '82%', label: t('statAverageScore') },
  ];
  return (
    <div className="px-2 sm:px-4 max-w-full">
      <div className="text-2xl font-bold text-bw-70 text-center mb-2">{t('dashboardTitle')}</div>
      <div className="text-sm text-bw-40 text-center mb-8">{t('dashboardSubtitle')}</div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((stat, i) => (
          <StatCard key={i} value={stat.value} label={stat.label} />
        ))}
      </div>
      <div className="w-full max-w-md mb-8 mx-auto">
        <label className="block text-left text-bw-70 font-semibold text-sm mb-1">
          {t('tokensPerUserLabel')}
        </label>
        <Select defaultValue="100">
          <SelectTrigger className="w-full border border-bw-20 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-bw-70">
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
      <div className="w-full max-w-md mb-8 mx-auto">
        <div className="text-lg font-semibold text-bw-70 mb-4 text-left" style={{ paddingLeft: 0 }}>
          {t('userFeedback')}
        </div>
        <div className="flex flex-row items-center">
          <div className="flex flex-col items-center justify-center min-w-28">
            <Star className="w-14 h-14 fill-marigold-30 mb-2" strokeWidth={0} />
            <div className="flex items-end">
              <span className="text-2xl font-semibold text-bw-70 leading-none">4.7</span>
              <span className="text-2xl font-normal text-bw-40 leading-none ml-1">/ 5</span>
            </div>
          </div>
          <div className="flex flex-col space-y-2 w-full sm:ml-8 sm:items-end sm:w-56 max-w-xs mx-auto">
            {[5, 4, 3, 2, 1].map((num, idx) => (
              <div key={num} className="flex items-center justify-end w-full">
                <Progress className="h-3 [&>div]:!bg-marigold-30" value={[80, 40, 15, 8, 2][idx]} />
                <span className="ml-3 text-sm text-bw-70 font-semibold w-6 text-right">{num}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
      <div className="w-full max-w-md mb-8 space-y-4 mx-auto">
        <div className="border border-bw-20 rounded-lg bg-transparent p-4 flex flex-col">
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
        <div className="border border-bw-20 rounded-lg bg-transparent p-4 flex flex-col">
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
          <div className="text-sm text-bw-40">20 Jan 2025</div>
        </div>
        <div className="border border-bw-20 rounded-lg bg-transparent p-4 flex flex-col">
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
      <Button size="full">
        {t('showAllReviews')}
        <ArrowRightIcon className="inline w-4 h-4 ml-2" />
      </Button>
      <Accordion type="multiple" className="w-full">
        <AccordionItem value="item-1" className="text-dark">
          <AccordionTrigger className="font-bw-70 cursor-pointer">
            {t('userManagement')}
          </AccordionTrigger>
          <AccordionContent></AccordionContent>
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
