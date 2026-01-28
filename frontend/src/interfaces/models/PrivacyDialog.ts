/**
 * Data processing topic displayed in privacy dialogs.
 */
export interface DataProcessingTopic {
  key: string;
  title: string;
  description: string;
  purposes: string[];
  storage: string[];
}
