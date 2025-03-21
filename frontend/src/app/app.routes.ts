import { Routes } from '@angular/router';
import { authGuard } from './_guards/auth.guard';
import { LoginComponent } from './features/auth/login/login.component';

export const routes: Routes = [
  {
    path: 'login',
    component: LoginComponent,
    title: 'Login'
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./features/dashboard/dashboard/dashboard.component')
      .then(m => m.DashboardComponent),
    title: 'Dashboard',
    canActivate: [() => authGuard()]
  },
  {
    path: 'calendar',
    loadChildren: () => import('./features/appointments/appointments.module')
      .then(m => m.AppointmentsModule),
    canActivate: [() => authGuard()]
  },
  {
    path: 'clients',
    loadChildren: () => import('./features/clients/clients.module')
      .then(m => m.ClientsModule),
    canActivate: [() => authGuard()]
  },
  {
    path: 'settings',
    loadChildren: () => import('./features/settings/settings.module')
      .then(m => m.SettingsModule),
    canActivate: [() => authGuard()]
  },
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full'
  }
];
