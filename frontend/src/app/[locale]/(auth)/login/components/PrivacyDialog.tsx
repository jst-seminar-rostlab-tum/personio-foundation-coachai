'use client';

import React from 'react';
import { Download, Trash2, Server, Lock } from 'lucide-react';
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

  const externalServices = t.raw('security.externalServices.services') as string[];

  const DataProcessingCard = ({ item }: { item: DataProcessingTopic }) => (
    <div className="border rounded-lg p-4" key={item.key}>
      <div className="font-semibold text-base sm:text-base mb-2">{item.title}</div>
      <div className="text-base sm:text-base text-gray-600 mb-3">{item.description}</div>
      <div className="space-y-2">
        <div>
          <div className="font-medium text-base mb-1">{t('dataProcessing.headers.purpose')}:</div>
          <div className="text-base space-y-1">
            {item.purposes.map((purpose, idx) => (
              <div key={idx}>• {purpose}</div>
            ))}
          </div>
        </div>
        <div>
          <div className="font-medium text-base mb-1">
            {t('dataProcessing.headers.storageDuration')}:
          </div>
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
            <th className="text-left py-3 pr-4 font-semibold text-base sm:text-base" scope="col">
              {t('dataProcessing.headers.personalData')}
            </th>
            <th className="text-left py-3 pr-4 font-semibold text-base sm:text-base" scope="col">
              {t('dataProcessing.headers.purpose')}
            </th>
            <th className="text-left py-3 font-semibold text-base sm:text-base" scope="col">
              {t('dataProcessing.headers.storageDuration')}
            </th>
          </tr>
        </thead>
        <tbody className="divide-y">
          {items.map((item) => (
            <tr key={item.key}>
              <td className="py-4 pr-4 align-top">
                <div className="font-medium text-base sm:text-base">{item.title}</div>
                <div className="text-base sm:text-base text-gray-600 mt-1">{item.description}</div>
              </td>
              <td className="py-4 pr-4 align-top">
                <ul className="text-base sm:text-base space-y-1" role="list">
                  {item.purposes.map((purpose, idx) => (
                    <li key={idx}>• {purpose}</li>
                  ))}
                </ul>
              </td>
              <td className="py-4 align-top">
                <ul className="text-base sm:text-base space-y-1" role="list">
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

          <section aria-labelledby="security-title">
            <Card>
              <CardHeader>
                <CardTitle id="security-title">
                  <div className="flex items-center justify-center gap-2">
                    {t('security.title')}
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
                  <div className="flex items-start gap-3">
                    <Server
                      className="h-4 w-4 sm:h-5 sm:w-5 text-blue-600 mt-0.5 flex-shrink-0"
                      aria-hidden="true"
                    />
                    <div>
                      <h4 className="font-semibold text-base sm:text-base">
                        {t('security.euServers.title')}
                      </h4>
                      <p className="text-base sm:text-base text-gray-600 mt-1">
                        {t('security.euServers.description')}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <Lock
                      className="h-4 w-4 sm:h-5 sm:w-5 text-green-600 mt-0.5 flex-shrink-0"
                      aria-hidden="true"
                    />
                    <div>
                      <h4 className="font-semibold text-base sm:text-base">
                        {t('security.encryption.title')}
                      </h4>
                      <p className="text-base sm:text-base text-gray-600 mt-1">
                        {t('security.encryption.description')}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t">
                  <h4 className="font-semibold mb-3 text-base sm:text-base">
                    {t('security.externalServices.title')}
                  </h4>
                  <div className="text-base sm:text-base text-gray-600 space-y-2">
                    {externalServices.map((service, idx) => (
                      <p key={idx}>
                        • <strong>{service}</strong>
                      </p>
                    ))}
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
                  <div className="flex items-start gap-3 p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                    <Trash2
                      className="h-4 w-4 sm:h-5 sm:w-5 text-red-600 mt-0.5 flex-shrink-0"
                      aria-hidden="true"
                    />
                    <div>
                      <h4 className="font-semibold text-base sm:text-base">
                        {t('userRights.accountDeletion.title')}
                      </h4>
                      <p className="text-base sm:text-base text-gray-600 mt-1">
                        {t('userRights.accountDeletion.description')}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                    <Download
                      className="h-4 w-4 sm:h-5 sm:w-5 text-blue-600 mt-0.5 flex-shrink-0"
                      aria-hidden="true"
                    />
                    <div>
                      <h4 className="font-semibold text-base sm:text-base">
                        {t('userRights.dataExport.title')}
                      </h4>
                      <p className="text-base sm:text-base text-gray-600 mt-1">
                        {t('userRights.dataExport.description')}
                      </p>
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
