import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CalendarComponent } from '../calendar/calendar.component';

@Component({
  selector: 'app-appointments',
  templateUrl: './appointments.component.html',
  styleUrls: ['./appointments.component.sass'],
  standalone: true,
  imports: [CommonModule, CalendarComponent],
  host: {
    class: 'appointments-wrapper'
  }
})
export class AppointmentsComponent {}
