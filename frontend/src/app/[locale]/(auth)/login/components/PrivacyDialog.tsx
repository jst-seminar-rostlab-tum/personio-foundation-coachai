'use client';

import React from 'react';
import { Download, Trash2, Lock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Dialog, DialogContent, DialogTitle } from '@/components/ui/Dialog';
import { useTranslations } from 'next-intl';
import { DataProcessingTopic } from '@/interfaces/models/PrivacyDialog';

interface PrivacyDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function PrivacyDialog({ open, onOpenChange }: PrivacyDialogProps) {
  const t = useTranslations('PrivacyPolicy.PrivacyPolicyDialog');
  const tCommon = useTranslations('Common');
  const dataProcessingTopics = t.raw('dataProcessing.topics') as DataProcessingTopic[];

  const externalServices = t.raw('externalServices.services') as string[];

  const DataProcessingCard = ({ item }: { item: DataProcessingTopic }) => (
    <div className="border rounded-lg p-4" key={item.key}>
      <div className="text-lg mb-2">{item.title}</div>
      <div className="text-base text-bw-60 mb-3">{item.description}</div>
      <div className="space-y-2">
        <div>
          <div className="text-lg mb-1">{t('dataProcessing.headers.purpose')}:</div>
          <div className="text-base space-y-1">
            {item.purposes.map((purpose, idx) => (
              <div key={idx}>• {purpose}</div>
            ))}
          </div>
        </div>
        <div>
          <div className="text-lg mb-1">{t('dataProcessing.headers.storageDuration')}:</div>
          <div className="text-base space-y-1">
            {item.storage.map((storage, idx) => (
              <div key={idx}>• {storage}</div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const DataProcessingTable = ({ items }: { items: DataProcessingTopic[] }) => (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse" role="table">
        <thead>
          <tr className="border-b">
            <th className="text-left py-3 pr-4 text-lg" scope="col">
              {t('dataProcessing.headers.personalData')}
            </th>
            <th className="text-left py-3 pr-4 text-lg" scope="col">
              {t('dataProcessing.headers.purpose')}
            </th>
            <th className="text-left py-3 text-lg" scope="col">
              {t('dataProcessing.headers.storageDuration')}
            </th>
          </tr>
        </thead>
        <tbody className="divide-y">
          {items.map((item) => (
            <tr key={item.key}>
              <td className="py-4 pr-4 align-top">
                <div className="text-lg">{item.title}</div>
                <div className="text-base text-bw-60 mt-1">{item.description}</div>
              </td>
              <td className="py-4 pr-4 align-top">
                <ul className="text-base space-y-1" role="list">
                  {item.purposes.map((purpose, idx) => (
                    <li key={idx}>• {purpose}</li>
                  ))}
                </ul>
              </td>
              <td className="py-4 align-top">
                <ul className="text-base space-y-1" role="list">
                  {item.storage.map((storage, idx) => (
                    <li key={idx}>• {storage}</li>
                  ))}
                </ul>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className="w-[95vw] max-w-sm sm:max-w-2xl lg:max-w-4xl max-h-[85vh] overflow-y-auto p-4"
        aria-describedby={undefined}
      >
        <DialogTitle>{tCommon('privacyPolicy')}</DialogTitle>

        <div className="space-y-4 sm:space-y-6 mt-4" role="document">
          <section aria-labelledby="data-processing-title">
            <Card>
              <CardHeader>
                <CardTitle id="data-processing-title">{t('dataProcessing.title')}</CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                <div className="block lg:hidden space-y-4">
                  {dataProcessingTopics.map((item) => (
                    <DataProcessingCard key={item.key} item={item} />
                  ))}
                </div>

                <div className="hidden lg:block">
                  <DataProcessingTable items={dataProcessingTopics} />
                </div>
              </CardContent>
            </Card>
          </section>

          <section aria-labelledby="external-services-title">
            <Card>
              <CardHeader>
                <CardTitle id="external-services-title">
                  <span>
                    {t('externalServices.title')} & {t('encryption.title')}
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 border-b pb-6">
                  {externalServices.map((service, idx) => (
                    <div key={idx} className="flex items-center gap-3 border rounded-lg px-4 py-3">
                      <span className="text-base">{service}</span>
                    </div>
                  ))}
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6 mt-6">
                  <div className="flex items-start gap-3">
                    <Lock
                      className="h-4 w-4 sm:h-5 sm:w-5 text-forest-50 mt-0.5 flex-shrink-0"
                      aria-hidden="true"
                    />
                    <div>
                      <h4 className="text-lg">{t('encryption.title')}</h4>
                      <p className="text-base text-bw-60 mt-1">{t('encryption.description')}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </section>

          <section aria-labelledby="user-rights-title">
            <Card>
              <CardHeader>
                <CardTitle id="user-rights-title">{t('userRights.title')}</CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="flex items-start gap-3 p-4 border rounded-lg">
                    <Trash2
                      className="h-4 w-4 sm:h-5 sm:w-5 text-flame-50 mt-0.5 flex-shrink-0"
                      aria-hidden="true"
                    />
                    <div>
                      <h4 className="text-lg">{t('userRights.accountDeletion.title')}</h4>
                      <p className="text-base mt-1">
                        {t('userRights.accountDeletion.description')}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 p-4 border rounded-lg">
                    <Download
                      className="h-4 w-4 sm:h-5 sm:w-5 text-blue-600 mt-0.5 flex-shrink-0"
                      aria-hidden="true"
                    />
                    <div>
                      <h4 className="text-lg">{t('userRights.dataExport.title')}</h4>
                      <p className="text-base mt-1">{t('userRights.dataExport.description')}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </section>
        </div>
      </DialogContent>
    </Dialog>
  );
}
