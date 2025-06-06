export interface DataProcessingTopic {
  key: string;
  title: string;
  description: string;
  purposes: string[];
  storage: string[];
}

export interface ExternalService {
  name: string;
}

export interface PrivacyDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export interface DataProcessingCardProps {
  item: DataProcessingTopic;
}

export interface DataProcessingTableProps {
  items: DataProcessingTopic[];
}
