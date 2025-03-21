import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatButtonModule } from '@angular/material/button';
import { MatDividerModule } from '@angular/material/divider';
import { SidebarService } from '../../../shared/services/sidebar.service';
import { Observable, Subject, catchError, finalize, takeUntil } from 'rxjs';
import { PageContainerComponent } from '../../../shared/layout/page-container/page-container.component';
import { DashboardService, DashboardStats, Activity } from '../services/dashboard.service';
import { AppointmentResponse, ClientResponse } from '../services/dashboard.service';
import { AuthService } from '../../../_services/auth.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatCardModule,
    MatIconModule,
    MatButtonModule,
    MatDividerModule,
    MatProgressBarModule,
    PageContainerComponent
  ],
  providers: [DatePipe, AuthService],
  viewProviders: [DashboardService],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.sass']
})
export class DashboardComponent implements OnInit, OnDestroy {
  isCollapsed$: Observable<boolean>;
  stats: DashboardStats = {
    todaysAppointmentsCount: 0,
    totalClients: 0,
    upcomingAppointmentsCount: 0,
    appointments: [],
    clients: []
  };
  activities: Activity[] = [];
  todayAppointments: AppointmentResponse[] = [];
  recentClients: ClientResponse[] = [];
  isLoading = true;
  error: string | null = null;
  private destroy$ = new Subject<void>();

  constructor(
    private sidebarService: SidebarService,
    private dashboardService: DashboardService,
    private authService: AuthService
  ) {
    this.isCollapsed$ = this.sidebarService.isCollapsed$;
    console.log('Dashboard Component Initialized'); // Debug log
  }

  ngOnInit(): void {
    this.loadDashboardData();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  retryLoad(): void {
    this.error = null;
    this.isLoading = true;
    this.loadDashboardData();
  }

  private loadDashboardData(): void {
    if (!this.authService.isAuthenticated()) {
      this.error = 'Please login first';
      return;
    }

    console.log('Loading Dashboard Data...');
    this.isLoading = true;
    this.error = null;

    // Initialize data
    this.stats = {
      todaysAppointmentsCount: 0,
      totalClients: 0,
      upcomingAppointmentsCount: 0,
      appointments: [],
      clients: []
    };
    this.todayAppointments = [];
    this.recentClients = [];

    // Fetch dashboard data
    this.dashboardService.getDashboardStats()
      .pipe(
        takeUntil(this.destroy$),
        catchError(error => {
          console.error('Error fetching dashboard data:', error);
          this.error = error.message || 'Failed to load dashboard data';
          throw error;
        }),
        finalize(() => {
          this.isLoading = false;
        })
      )
      .subscribe({
        next: (stats) => {
          console.log('Dashboard Data:', stats);
          this.stats = stats;
          this.todayAppointments = stats.appointments;
          this.recentClients = stats.clients;

          // Create activities from appointments and clients
          this.activities = [
            ...stats.appointments.map(apt => ({
              type: 'appointment' as const,
              text: `New appointment: ${apt.title}`,
              time: apt.startTime
            })),
            ...stats.clients.map(client => ({
              type: 'client' as const,
              text: `New client: ${client.phone}`,
              time: new Date().toISOString()
            }))
          ].sort((a, b) => new Date(b.time).getTime() - new Date(a.time).getTime())
           .slice(0, 5);
        },
        error: (error: Error) => {
          console.error('Error loading dashboard:', error);
          this.error = error.message || 'Failed to load dashboard data';
          this.isLoading = false;
        }
      });
  }
}
