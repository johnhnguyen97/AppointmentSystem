import { Injectable } from '@angular/core';
import { Apollo, gql } from 'apollo-angular';
import { map, Observable, catchError } from 'rxjs';
import { AuthService } from '../../../_services/auth.service';

const GET_DASHBOARD_DATA = gql`
  query GetDashboardData {
    dashboardSummary {
      totalClients
      todaysAppointmentsCount
      upcomingAppointmentsCount
    }
    todaysAppointments {
      id
      title
      description
      startTime
      durationMinutes
      status
      serviceType
      estimatedCost
    }
    recentClients {
      id
      phone
      service
      status
      notes
      loyaltyPoints
      totalSpent
      visitCount
      lastVisit
      category
    }
  }
`;

export enum AppointmentStatus {
  SCHEDULED = 'SCHEDULED',
  CONFIRMED = 'CONFIRMED',
  CANCELLED = 'CANCELLED',
  COMPLETED = 'COMPLETED',
  DECLINED = 'DECLINED'
}

export interface DashboardStats {
  todaysAppointmentsCount: number;
  totalClients: number;
  upcomingAppointmentsCount: number;
  appointments: AppointmentResponse[];
  clients: ClientResponse[];
}

export interface Activity {
  type: 'appointment' | 'client' | 'completion';
  text: string;
  time: string;
}

export interface AppointmentResponse {
  id: string;
  title: string;
  description?: string;
  startTime: string;
  durationMinutes: number;
  status: AppointmentStatus;
  serviceType: string;
  estimatedCost: number;
}

export interface ClientResponse {
  id: string;
  phone: string;
  service: string;
  status: string;
  notes?: string;
  loyaltyPoints: number;
  totalSpent: number;
  visitCount: number;
  lastVisit?: string;
  category: string;
}

interface DashboardQueryResponse {
  dashboardSummary: {
    totalClients: number;
    todaysAppointmentsCount: number;
    upcomingAppointmentsCount: number;
  };
  todaysAppointments: AppointmentResponse[];
  recentClients: ClientResponse[];
}

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  constructor(
    private apollo: Apollo,
    private authService: AuthService
  ) {}

  getDashboardStats(): Observable<DashboardStats> {
    if (!this.authService.isAuthenticated()) {
      console.error('Not authenticated, please log in first');
      throw new Error('Authentication required');
    }

    const token = this.authService.getToken();
    if (!token) {
      console.error('No auth token available');
      throw new Error('Authentication required');
    }

    return this.apollo.watchQuery<DashboardQueryResponse>({
      query: GET_DASHBOARD_DATA,
      context: {
        headers: {
          Authorization: `Bearer ${token}`
        }
      },
      fetchPolicy: 'network-only',
      errorPolicy: 'all'
    }).valueChanges.pipe(
      map(result => {
        console.log('Full GraphQL Response:', result);

        if (result.errors) {
          console.error('GraphQL Errors:', result.errors);
          if (result.errors[0]?.message.includes('Not authenticated')) {
            this.authService.logout();
          }
          throw new Error(result.errors[0]?.message || 'GraphQL Error');
        }

        const { dashboardSummary, todaysAppointments, recentClients } = result.data;

        return {
          todaysAppointmentsCount: dashboardSummary.todaysAppointmentsCount,
          totalClients: dashboardSummary.totalClients,
          upcomingAppointmentsCount: dashboardSummary.upcomingAppointmentsCount,
          appointments: todaysAppointments,
          clients: recentClients
        };
      }),
      catchError(error => {
        console.error('GraphQL Error:', error);
        if (error.message?.includes('Not authenticated')) {
          this.authService.logout();
        }
        throw error;
      })
    );
  }
}
