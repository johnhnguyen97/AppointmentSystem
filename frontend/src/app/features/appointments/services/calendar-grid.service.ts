import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import {
  CalendarGrid,
  CalendarViewMode,
  CalendarDay,
  TimeSlot,
  CalendarCell,
  TimeRange,
  CalendarViewState
} from '../calendar/calendar.types';

@Injectable({
  providedIn: 'root'
})
export class CalendarGridService {
  private readonly DAYS_OF_WEEK = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];
  private gridState = new BehaviorSubject<CalendarGrid>(this.createInitialState());

  constructor() {}

  private createInitialState(): CalendarGrid {
    const now = new Date();
    const initialViewState: CalendarViewState = {
      currentDate: now,
      selectedDate: null,
      viewMode: CalendarViewMode.Week,
      timeRange: { start: 0, end: 23 }
    };

    return {
      timeSlots: this.generateTimeSlots(initialViewState.timeRange),
      days: this.generateDays(now),
      cells: [],
      viewState: initialViewState
    };
  }

  private generateTimeSlots(range: TimeRange): TimeSlot[] {
    return Array.from(
      { length: range.end - range.start + 1 },
      (_, i) => {
        const hour = i + range.start;
        return {
          hour,
          minute: 0,
          formatted: `${hour.toString().padStart(2, '0')}:00`
        };
      }
    );
  }

  private generateDays(date: Date): CalendarDay[] {
    const today = new Date();
    const currentDay = date.getDay();
    const diff = currentDay === 0 ? 6 : currentDay - 1; // Adjust to start from Monday
    const startDate = new Date(date);
    startDate.setDate(date.getDate() - diff);

    return Array.from({ length: 7 }, (_, i) => {
      const dayDate = new Date(startDate);
      dayDate.setDate(startDate.getDate() + i);

      return {
        date: dayDate,
        isCurrentMonth: dayDate.getMonth() === date.getMonth(),
        isToday: this.isSameDay(dayDate, today),
        dayOfWeek: i
      };
    });
  }

  private isSameDay(date1: Date, date2: Date): boolean {
    return date1.getFullYear() === date2.getFullYear() &&
           date1.getMonth() === date2.getMonth() &&
           date1.getDate() === date2.getDate();
  }

  private generateGrid(timeSlots: TimeSlot[], days: CalendarDay[]): CalendarCell[][] {
    return timeSlots.map(timeSlot =>
      days.map(day => ({
        timeSlot,
        day,
        hasAppointment: false,
        appointments: []
      }))
    );
  }

  // Public methods
  updateViewState(update: Partial<CalendarViewState>): void {
    const currentState = this.gridState.value;
    const newViewState = { ...currentState.viewState, ...update };
    
    const newState: CalendarGrid = {
      timeSlots: update.timeRange 
        ? this.generateTimeSlots(update.timeRange)
        : currentState.timeSlots,
      days: update.currentDate 
        ? this.generateDays(update.currentDate)
        : currentState.days,
      cells: currentState.cells,
      viewState: newViewState
    };

    newState.cells = this.generateGrid(newState.timeSlots, newState.days);
    this.gridState.next(newState);
  }

  getGridState(): Observable<CalendarGrid> {
    return this.gridState.asObservable();
  }

  getDaysOfWeek(): string[] {
    return this.DAYS_OF_WEEK;
  }

  navigateToDate(date: Date): void {
    this.updateViewState({ currentDate: date });
  }

  setViewMode(mode: CalendarViewMode): void {
    this.updateViewState({ viewMode: mode });
  }

  setTimeRange(range: TimeRange): void {
    this.updateViewState({ timeRange: range });
  }

  selectDate(date: Date | null): void {
    this.updateViewState({ selectedDate: date });
  }

  getTimeSlots(): Observable<TimeSlot[]> {
    return this.gridState.pipe(map(state => state.timeSlots));
  }

  getDays(): Observable<CalendarDay[]> {
    return this.gridState.pipe(map(state => state.days));
  }

  getCells(): Observable<CalendarCell[][]> {
    return this.gridState.pipe(map(state => state.cells));
  }

  getCurrentViewState(): Observable<CalendarViewState> {
    return this.gridState.pipe(map(state => state.viewState));
  }
}
