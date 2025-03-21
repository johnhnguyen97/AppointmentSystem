import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class GridService {
  private readonly HOURS = Array.from({ length: 24 }, (_, i) => {
    // Format as 24-hour time: 00:00 - 23:00
    return `${i.toString().padStart(2, '0')}:00`;
  });

  private readonly DAYS = [
    'MON',
    'TUE',
    'WED',
    'THU',
    'FRI',
    'SAT',
    'SUN'
  ];

  getTimeSlots(): string[] {
    return this.HOURS;
  }

  getWeekDays(): string[] {
    return this.DAYS;
  }

  getFormattedDate(date: Date): string {
    return new Intl.DateTimeFormat('en-US', {
      month: 'long',
      year: 'numeric'
    }).format(date);
  }

  getWeekDates(startDate: Date): Date[] {
    const dates: Date[] = [];
    const currentDate = new Date(startDate);
    const dayOfWeek = currentDate.getDay();
    const diff = dayOfWeek === 0 ? 6 : dayOfWeek - 1;
    
    currentDate.setDate(currentDate.getDate() - diff);
    
    for (let i = 0; i < 7; i++) {
      dates.push(new Date(currentDate));
      currentDate.setDate(currentDate.getDate() + 1);
    }
    
    return dates;
  }

  formatTimeSlot(slot: string): string {
    return slot;
  }
}
