export interface ConversationCategory {
  id: string;
  name: string;
  iconUri: string;
  defaultContext?: string;
  defaultGoal?: string;
  defaultOtherParty?: string;
  isCustom?: boolean;
}
