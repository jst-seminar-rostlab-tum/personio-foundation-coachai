export interface ConversationCategory {
  id: string;
  name: string;
  iconUri: string;
  description?: string;
  defaultContext?: string;
  defaultGoal?: string;
  defaultOtherParty?: string;
  isCustom?: boolean;
}
