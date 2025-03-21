import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { DashboardComponent } from './dashboard.component';
import { DashboardService } from '../services/dashboard.service';
import { SidebarService } from '../../../shared/services/sidebar.service';
import { PageContainerComponent } from '../../../shared/layout/page-container/page-container.component';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { of, throwError } from 'rxjs';

describe('DashboardComponent', () => {
  let component: DashboardComponent;
  let fixture: ComponentFixture<DashboardComponent>;
  let dashboardService: jasmine.SpyObj<DashboardService>;

  beforeEach(async () => {
    const dashboardSpy = jasmine.createSpyObj('DashboardService', ['getDashboardStats', 'getRecentActivity']);
    dashboardSpy.getDashboardStats.and.returnValue(of({
      todayAppointments: 0,
      totalClients: 0,
      upcomingAppointments: 0,
      appointments: [],
      clients: []
    }));
    dashboardSpy.getRecentActivity.and.returnValue(of([]));

    await TestBed.configureTestingModule({
      imports: [
        HttpClientTestingModule,
        MatCardModule,
        MatIconModule,
        MatProgressBarModule,
        PageContainerComponent,
        DashboardComponent
      ],
      providers: [
        { provide: DashboardService, useValue: dashboardSpy },
        SidebarService
      ]
    }).compileComponents();

    dashboardService = TestBed.inject(DashboardService) as jasmine.SpyObj<DashboardService>;
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load dashboard data on init', () => {
    component.ngOnInit();
    expect(dashboardService.getDashboardStats).toHaveBeenCalled();
    expect(dashboardService.getRecentActivity).toHaveBeenCalled();
  });

  it('should show loading state initially', () => {
    expect(component.isLoading).toBeTruthy();
  });

  it('should handle error state', () => {
    dashboardService.getDashboardStats.and.returnValue(throwError(() => new Error('Test error')));
    component.ngOnInit();
    expect(component.error).toBeDefined();
  });
});
