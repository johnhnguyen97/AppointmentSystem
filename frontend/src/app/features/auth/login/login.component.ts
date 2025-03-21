import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { AuthService } from '../../../_services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatInputModule,
    MatButtonModule,
    MatFormFieldModule,
    MatProgressBarModule,
    MatCheckboxModule
  ],
  template: `
    <div class="login-container">
      <mat-card class="login-card">
        <mat-card-header>
          <mat-card-title>Login</mat-card-title>
        </mat-card-header>

        <mat-progress-bar *ngIf="isLoading" mode="indeterminate"></mat-progress-bar>

        <mat-card-content>
          <form #loginForm="ngForm" (ngSubmit)="onSubmit()">
            <mat-form-field appearance="outline">
              <mat-label>Username</mat-label>
              <input matInput [(ngModel)]="username" name="username" required>
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>Password</mat-label>
              <input matInput type="password" [(ngModel)]="password" name="password" required>
            </mat-form-field>

            <mat-checkbox [(ngModel)]="rememberMe" name="rememberMe" color="primary">
              Remember me
            </mat-checkbox>

            <div *ngIf="error" class="error-message">
              {{ error }}
            </div>

            <button mat-raised-button color="primary" type="submit" [disabled]="isLoading">
              Login
            </button>
          </form>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`

.login-container
  display: flex
  justify-content: center
  align-items: center
  height: 100vh
  background-color: var(--surface-container)
  color: var(--on-surface)

.login-card
  width: 100%
  max-width: 400px
  margin: 2rem
  background-color: var(--surface)
  color: var(--on-surface)

mat-card-header
  margin-bottom: 1rem

mat-form-field
  width: 100%
  margin-bottom: 1rem

mat-checkbox
  margin-bottom: 1rem

.error-message
  color: var(--error)
  margin-bottom: 1rem
  font-size: 0.875rem

::ng-deep
  .mdc-text-field
    background-color: var(--surface-container-high) !important

  .mat-mdc-form-field-focus-overlay
    background-color: var(--surface-container-highest)

button
  width: 100%

form
  display: flex
  flex-direction: column
  padding: 1rem
  `]
})
export class LoginComponent {
  username = '';
  password = '';
  rememberMe = false;
  isLoading = false;
  error: string | null = null;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  onSubmit(): void {
    if (!this.username || !this.password) {
      this.error = 'Please enter both username and password';
      return;
    }

    this.isLoading = true;
    this.error = null;

    this.authService.login(this.username, this.password, this.rememberMe)
      .subscribe({
        next: () => {
          this.router.navigate(['/dashboard']);
        },
        error: (error) => {
          this.error = error.message || 'Login failed';
          this.isLoading = false;
        }
      });
  }
}
