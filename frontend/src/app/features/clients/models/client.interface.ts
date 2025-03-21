export interface Client {
  id: string;
  name: string;
  phone: string;
  email: string;
  address: string;
  lastVisit: Date;
  nextAppointment: Date;
  preferredService: string;
  status: 'active' | 'inactive' | 'new';
}

export interface ColumnDefinition {
  key: keyof Client;
  header: string;
  type: 'text' | 'date' | 'status' | 'actions';
  width?: string;
  align?: 'left' | 'center' | 'right';
}

export type SortColumn = keyof Client;
export type SortDirection = 'asc' | 'desc';
