'use client';

import React from 'react';
import { Download, Trash2, Lock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Dialog, DialogContent } from '@/components/ui/Dialog';
import { useTranslations } from 'next-intl';
import { DataProcessingTopic } from '@/interfaces/models/PrivacyDialog';

/**
 * Props for rendering the privacy dialog either inline or as a modal.
 */
type PrivacyDialogProps =
  | {
      variant?: 'dialog';
      open: boolean;
      onOpenChange: (open: boolean) => void;
    }
  | {
      variant: 'content';
      open?: never;
      onOpenChange?: never;
    };

/**
 * Props for a single data processing card entry.
 */
interface DataProcessingCardProps {
  item: DataProcessingTopic;
  purposeLabel: string;
  storageDurationLabel: string;
}

/**
 * Displays a single data processing topic in card form.
 */
const DataProcessingCard = ({
  item,
  purposeLabel,
  storageDurationLabel,
}: DataProcessingCardProps) => (
  <div className="border rounded-lg p-4">
    <div className="text-lg mb-2">{item.title}</div>
    <div className="text-base text-bw-70 mb-3">{item.description}</div>
    <div className="space-y-2">
      <div>
        <div className="text-lg mb-1">{purposeLabel}:</div>
        <div className="text-base space-y-1">
          {item.purposes.map((purpose, idx) => (
            <div key={idx}>• {purpose}</div>
          ))}
        </div>
      </div>
      <div>
        <div className="text-lg mb-1">{storageDurationLabel}:</div>
        <div className="text-base space-y-1">
          {item.storage.map((storage, idx) => (
            <div key={idx}>• {storage}</div>
          ))}
        </div>
      </div>
    </div>
  </div>
);

/**
 * Props for the data processing table layout.
 */
interface DataProcessingTableProps {
  items: DataProcessingTopic[];
  headers: {
    personalData: string;
    purpose: string;
    storageDuration: string;
  };
}

/**
 * Renders data processing topics in a table layout.
 */
const DataProcessingTable = ({ items, headers }: DataProcessingTableProps) => (
  <div className="overflow-x-auto">
    <table className="w-full border-collapse" role="table">
      <thead>
        <tr className="border-b">
          <th className="text-left py-3 pr-4 text-lg" scope="col">
            {headers.personalData}
          </th>
          <th className="text-left py-3 pr-4 text-lg" scope="col">
            {headers.purpose}
          </th>
          <th className="text-left py-3 text-lg" scope="col">
            {headers.storageDuration}
          </th>
        </tr>
      </thead>
      <tbody className="divide-y">
        {items.map((item) => (
          <tr key={item.key}>
            <td className="py-4 pr-4 align-top">
              <div className="text-lg">{item.title}</div>
              <div className="text-base text-bw-70 mt-1">{item.description}</div>
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

/**
 * Props for the data processing section container.
 */
interface DataProcessingSectionProps {
  dataProcessingTopics: DataProcessingTopic[];
  title: string;
  headers: {
    personalData: string;
    purpose: string;
    storageDuration: string;
  };
}

/**
 * Shows the data processing section with responsive card/table layouts.
 */
const DataProcessingSection = ({
  dataProcessingTopics,
  title,
  headers,
}: DataProcessingSectionProps) => (
  <section aria-labelledby="data-processing-title">
    <Card>
      <CardHeader>
        <CardTitle id="data-processing-title">{title}</CardTitle>
      </CardHeader>
      <CardContent className="p-4">
        {/* Mobile: Card view */}
        <div className="block lg:hidden space-y-4">
          {dataProcessingTopics.map((item) => (
            <DataProcessingCard
              key={item.key}
              item={item}
              purposeLabel={headers.purpose}
              storageDurationLabel={headers.storageDuration}
            />
          ))}
        </div>

        {/* Desktop: Table view */}
        <div className="hidden lg:block">
          <DataProcessingTable items={dataProcessingTopics} headers={headers} />
        </div>
      </CardContent>
    </Card>
  </section>
);

/**
 * Props for the external services and encryption section.
 */
interface ExternalServicesAndEncryptionSectionProps {
  externalServices: string[];
  externalServicesTitle: string;
  encryptionTitle: string;
  encryptionDescription: string;
}

/**
 * Presents external services used and encryption information.
 */
const ExternalServicesAndEncryptionSection = ({
  externalServices,
  externalServicesTitle,
  encryptionTitle,
  encryptionDescription,
}: ExternalServicesAndEncryptionSectionProps) => (
  <section aria-labelledby="external-services-title">
    <Card>
      <CardHeader>
        <CardTitle id="external-services-title">
          <span>
            {externalServicesTitle} &amp; {encryptionTitle}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4">
        {/* External Services List */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 border-b pb-6">
          {externalServices.map((service, idx) => (
            <div key={idx} className="flex items-center gap-3 border rounded-lg px-4 py-3">
              <span className="text-base">{service}</span>
            </div>
          ))}
        </div>

        {/* Encryption Info */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6 mt-6">
          <div className="flex items-start gap-3">
            <Lock
              className="h-4 w-4 sm:h-5 sm:w-5 text-forest-50 mt-0.5 flex-shrink-0"
              aria-hidden="true"
            />
            <div>
              <h4 className="text-lg">{encryptionTitle}</h4>
              <p className="text-base text-bw-70 mt-1">{encryptionDescription}</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  </section>
);

/**
 * Props for the user rights section.
 */
interface UserRightsSectionProps {
  title: string;
  accountDeletion: {
    title: string;
    description: string;
  };
  dataExport: {
    title: string;
    description: string;
  };
}

/**
 * Highlights user rights related to account deletion and data export.
 */
const UserRightsSection = ({ title, accountDeletion, dataExport }: UserRightsSectionProps) => (
  <section aria-labelledby="user-rights-title">
    <Card>
      <CardHeader>
        <CardTitle id="user-rights-title">{title}</CardTitle>
      </CardHeader>
      <CardContent className="p-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Account Deletion */}
          <div className="flex items-start gap-3 p-4 border rounded-lg">
            <Trash2
              className="h-4 w-4 sm:h-5 sm:w-5 text-flame-50 mt-0.5 flex-shrink-0"
              aria-hidden="true"
            />
            <div>
              <h4 className="text-lg">{accountDeletion.title}</h4>
              <p className="text-base mt-1">{accountDeletion.description}</p>
            </div>
          </div>

          {/* Data Export */}
          <div className="flex items-start gap-3 p-4 border rounded-lg">
            <Download
              className="h-4 w-4 sm:h-5 sm:w-5 text-blue-600 mt-0.5 flex-shrink-0"
              aria-hidden="true"
            />
            <div>
              <h4 className="text-lg">{dataExport.title}</h4>
              <p className="text-base mt-1">{dataExport.description}</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  </section>
);

/**
 * Renders the privacy dialog content as either inline content or a modal dialog.
 */
export default function PrivacyDialog(props: PrivacyDialogProps) {
  const { variant = 'dialog' } = props as { variant: 'dialog' | 'content' };

  const t = useTranslations('PrivacyPolicy.PrivacyPolicyDialog');

  const dataProcessingTopics = t.raw('dataProcessing.topics') as DataProcessingTopic[];
  const externalServices = t.raw('externalServices.services') as string[];

  const content = (
    <div
      className={`space-y-4 sm:space-y-6 ${variant === 'dialog' ? 'mt-4' : ''}`}
      role={variant === 'dialog' ? 'document' : undefined}
    >
      <DataProcessingSection
        dataProcessingTopics={dataProcessingTopics}
        title={t('dataProcessing.title')}
        headers={{
          personalData: t('dataProcessing.headers.personalData'),
          purpose: t('dataProcessing.headers.purpose'),
          storageDuration: t('dataProcessing.headers.storageDuration'),
        }}
      />

      <ExternalServicesAndEncryptionSection
        externalServices={externalServices}
        externalServicesTitle={t('externalServices.title')}
        encryptionTitle={t('encryption.title')}
        encryptionDescription={t('encryption.description')}
      />

      <UserRightsSection
        title={t('userRights.title')}
        accountDeletion={{
          title: t('userRights.accountDeletion.title'),
          description: t('userRights.accountDeletion.description'),
        }}
        dataExport={{
          title: t('userRights.dataExport.title'),
          description: t('userRights.dataExport.description'),
        }}
      />
    </div>
  );

  if (variant === 'content') {
    return content;
  }

  const { open, onOpenChange } = props as { open: boolean; onOpenChange: (o: boolean) => void };
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className="w-[95vw] max-w-sm sm:max-w-2xl lg:max-w-4xl max-h-[85vh] overflow-y-auto p-4"
        aria-describedby={undefined}
      >
        {content}
      </DialogContent>
    </Dialog>
  );
}
