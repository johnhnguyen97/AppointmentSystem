export interface TimeSlot {
  hour: number;
  minute: number;
  formatted: string;
}

export interface CalendarDay {
  date: Date;
  isCurrentMonth: boolean;
  isToday: boolean;
  dayOfWeek: number;
}

export interface CalendarWeek {
  days: CalendarDay[];
}

export interface CalendarCell {
  timeSlot: TimeSlot;
  day: CalendarDay;
  hasAppointment: boolean;
  appointments: Appointment[];
}

export interface Appointment {
  id: string;
  startTime: Date;
  endTime: Date;
  title: string;
  clientName: string;
  type: AppointmentType;
}

export enum AppointmentType {
  Regular = 'regular',
  Urgent = 'urgent',
  Blocked = 'blocked'
}

export interface CalendarViewState {
  currentDate: Date;
  selectedDate: Date | null;
  viewMode: CalendarViewMode;
  timeRange: TimeRange;
}

export enum CalendarViewMode {
  Day = 'day',
  Week = 'week',
  Month = 'month'
}

export interface TimeRange {
  start: number; // Hour (0-23)
  end: number;   // Hour (0-23)
}

export interface CalendarGrid {
  timeSlots: TimeSlot[];
  days: CalendarDay[];
  cells: CalendarCell[][];
  viewState: CalendarViewState;
}
