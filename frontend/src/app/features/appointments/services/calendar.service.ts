import { Injectable } from '@angular/core';

export interface CalendarDay {
  date: Date | null;
  isCurrentMonth: boolean;
}

export interface Hour {
  hour: number; // 0-23
}

@Injectable({
  providedIn: 'root',
})
export class CalendarService {
  constructor() {}

  generateCalendar(year: number, month: number): CalendarDay[][] {
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    
    const firstWeekday = firstDay.getDay(); // 0 (Sunday) to 6 (Saturday)
    const weeks: CalendarDay[][] = [];

    let currentWeek: CalendarDay[] = [];
    let dayCounter = 1;

    // Fill initial empty slots (previous month)
    for (let i = 0; i < firstWeekday; i++) {
      currentWeek.push({ date: null, isCurrentMonth: false });
    }

    // Fill in the days of the current month
    for (let i = 1; i <= daysInMonth; i++) {
      currentWeek.push({ date: new Date(year, month, i), isCurrentMonth: true });

      if (currentWeek.length === 7) {
        weeks.push(currentWeek);
        currentWeek = [];
      }
    }

    // Fill remaining slots (next month)
    while (currentWeek.length < 7) {
      currentWeek.push({ date: null, isCurrentMonth: false });
    }
    weeks.push(currentWeek);

    return weeks;
  }

  generateHours(): Hour[] {
    return Array.from({ length: 24 }, (_, i) => ({ hour: i }));
  }
}
