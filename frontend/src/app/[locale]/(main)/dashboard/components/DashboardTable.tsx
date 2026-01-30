'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ChevronDown } from 'lucide-react';
import { ClickableTable, ClickableTableColumn } from '@/components/common/ClickableTable';
import { DeleteConfirmButton } from '@/components/common/DeleteConfirmButton';
import { ConversationScenario } from '@/interfaces/models/ConversationScenario';
import { useLocale, useTranslations } from 'next-intl';
import { conversationScenarioService } from '@/services/ConversationScenarioService';
import { api } from '@/services/ApiClient';
import { showErrorToast, showSuccessToast } from '@/lib/utils/toast';
import { Button } from '@/components/ui/Button';
import { formatDateFlexible } from '@/lib/utils/formatDateAndTime';
import { Categories } from '@/lib/constants/categories';
import Image from 'next/image';
import EmptyListComponent from '@/components/common/EmptyListComponent';
import { Badge } from '@/components/ui/Badge';

/**
 * Props for the dashboard scenarios table.
 */
type DashboardTableProps = {
  scenarios: ConversationScenario[];
  totalScenarios: number;
  limit: number;
};

/**
 * Renders a paginated table of recent conversation scenarios.
 */
export default function DashboardTable({ scenarios, totalScenarios, limit }: DashboardTableProps) {
  const router = useRouter();
  const locale = useLocale();
  const tCommon = useTranslations('Common');
  const tDashboard = useTranslations('Dashboard');
  const tConversationScenario = useTranslations('ConversationScenario');
  const tCategories = useTranslations('ConversationScenario.categories');
  const [pageNumber, setPageNumber] = useState(1);
  const [visibleCount, setVisibleCount] = useState(limit);
  const [isLoading, setIsLoading] = useState(false);
  const [rows, setRows] = useState(scenarios);
  const canLoadMore = visibleCount < totalScenarios;
  const categories = Categories(tCategories);

  /**
   * Advances to the next page of scenarios.
   */
  const handleLoadMore = (newPage: number) => {
    setPageNumber(newPage);
  };

  /**
   * Navigates to the selected scenario's history.
   */
  const handleRowClick = (row: ConversationScenario) => router.push(`/history/${row.scenarioId}`);

  /**
   * Loads additional scenarios and appends new rows.
   */
  const getScenarios = async () => {
    try {
      setIsLoading(true);
      const response = await conversationScenarioService.getConversationScenarios(
        api,
        pageNumber,
        limit
      );
      setRows((prev) => {
        const existingIds = new Set(prev.map((row) => row.scenarioId));
        const filtered = response.data.scenarios.filter(
          (s: ConversationScenario) => !existingIds.has(s.scenarioId)
        );
        return [...prev, ...filtered];
      });
      setVisibleCount((prev) => prev + limit);
    } catch (e) {
      showErrorToast(e, tCommon('error'));
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Deletes a scenario and refreshes the list.
   */
  const handleDelete = async (id: string) => {
    try {
      await conversationScenarioService.deleteConversationScenario(api, id);
      setRows((prev) => prev.filter((row) => row.scenarioId !== id));
      await getScenarios();
      showSuccessToast(tDashboard('deleteConversationScenarioSuccess'));
    } catch (error) {
      showErrorToast(error, tDashboard('deleteConversationScenarioError'));
    }
  };

  useEffect(() => {
    if (canLoadMore && pageNumber > 1) {
      getScenarios();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pageNumber, canLoadMore, limit, tCommon]);

  const columns: ClickableTableColumn<(typeof rows)[number]>[] = [
    {
      header: 'Situation',
      accessor: 'categoryId',
      cell: (row) => categories[row.categoryId].name,
    },
    {
      header: 'Persona',
      accessor: 'personaName',
      cell: (row) => (
        <div className="flex items-center gap-2">
          <Image
            src={tConversationScenario(`customize.persona.personas.${row.personaName}.imageUri`)}
            alt={tConversationScenario(`customize.persona.personas.${row.personaName}.name`)}
            width={28}
            height={28}
            className="rounded-full bg-custom-beige"
          />
          <span className="text-sm">
            {tConversationScenario(`customize.persona.personas.${row.personaName}.name`)}
          </span>
        </div>
      ),
    },
    {
      header: tConversationScenario('difficultyTitle'),
      accessor: 'difficultyLevel',
      cell: (row) => (
        <Badge variant={row.difficultyLevel}>
          {tConversationScenario(`${row.difficultyLevel}`)}
        </Badge>
      ),
    },
    {
      header: tDashboard('lastSession'),
      accessor: 'lastSessionAt',
      cell: (row) => formatDateFlexible(row.lastSessionAt, locale, true),
    },
    {
      header: '',
      accessor: () => '',
      className: 'text-right',
      cell: (row) => (
        <DeleteConfirmButton onConfirm={() => handleDelete(row.scenarioId as string)} />
      ),
    },
  ];

  if (!rows.length) {
    return <EmptyListComponent itemType={tConversationScenario('emptyListItemType')} />;
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-bw-40 mb-4 max-w-full">
      <ClickableTable
        columns={columns}
        data={rows}
        onRowClick={handleRowClick}
        rowKey={(row) => row.scenarioId as string}
      />
      {canLoadMore && (
        <div className="flex justify-center mt-4 mb-4">
          <Button variant="ghost" onClick={() => handleLoadMore(pageNumber + 1)}>
            {isLoading ? tCommon('loading') : tCommon('loadMore')} <ChevronDown />
          </Button>
        </div>
      )}
    </div>
  );
}
