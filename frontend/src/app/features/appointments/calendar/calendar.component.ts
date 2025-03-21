import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { PageContainerComponent } from '../../../shared/layout/page-container/page-container.component';

@Component({
  selector: 'app-calendar',
  templateUrl: './calendar.component.html',
  styleUrls: ['./calendar.component.sass'],
  standalone: true,
  imports: [CommonModule, MatIconModule, MatCardModule, PageContainerComponent]
})
export class CalendarComponent {
  currentMonth = new Date().getMonth();
  currentYear = new Date().getFullYear();
  
  // Update to Monday-Sunday format
  daysOfWeek = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  hours = Array.from({ length: 24 }, (_, i) => ({ hour: i }));

  prevMonth() {
    if (this.currentMonth === 0) {
      this.currentMonth = 11;
      this.currentYear--;
    } else {
      this.currentMonth--;
    }
  }

  nextMonth() {
    if (this.currentMonth === 11) {
      this.currentMonth = 0;
      this.currentYear++;
    } else {
      this.currentMonth++;
    }
  }

  formatHour(hour: number): string {
    // Use 24-hour format
    return hour.toString().padStart(2, '0') + ':00';
  }

  getMonthName(month: number): string {
    return new Date(2024, month).toLocaleString('default', { month: 'long' });
  }
}
