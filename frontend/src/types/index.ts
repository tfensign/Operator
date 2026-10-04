export interface Message {
  id: number;
  platform: string;
  from_address: string;
  subject?: string;
  body: string;
  priority: number;
  created_at: string;
  read_at?: string;
  deleted_at?: string;
}

export interface ChecklistItem {
  id: number;
  checklist_id: number;
  text: string;
  completed_at?: string;
  source_message_id?: number;
}

export interface Checklist {
  id: number;
  title: string;
  description?: string;
  created_at: string;
  due_date?: string;
  completed_at?: string;
  items: ChecklistItem[];
}

export interface PendingSend {
  id: number;
  platform: string;
  to_address: string;
  subject?: string;
  body: string;
  created_at: string;
  approved_at?: string;
}

export interface Integration {
  id: number;
  platform: string;
  webhook_url: string;
  status: string;
  created_at: string;
}
