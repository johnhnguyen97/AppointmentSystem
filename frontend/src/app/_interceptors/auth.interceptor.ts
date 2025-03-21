import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';
import { AuthService } from '../_services/auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  private isRefreshing = false;

  constructor(private authService: AuthService) {}

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Don't add auth header for login requests
    if (this.isLoginRequest(request)) {
      return next.handle(request);
    }

    const token = this.authService.getToken();
    if (token) {
      request = this.addToken(request, token);
    }

    return next.handle(request).pipe(
      catchError((error) => {
        if (error instanceof HttpErrorResponse && error.status === 401) {
          // Token expired or invalid
          if (!this.isRefreshing) {
            this.isRefreshing = true;
            this.authService.logout();
            // Try to login again using stored credentials
            return this.authService.login('admin', 'admin').pipe(
              switchMap((response) => {
                this.isRefreshing = false;
                // Retry the original request with new token
                const newRequest = this.addToken(request, response.token);
                return next.handle(newRequest);
              }),
              catchError((err) => {
                this.isRefreshing = false;
                this.authService.logout();
                return throwError(() => err);
              })
            );
          }
        }
        return throwError(() => error);
      })
    );
  }

  private addToken(request: HttpRequest<any>, token: string): HttpRequest<any> {
    return request.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }

  private isLoginRequest(request: HttpRequest<any>): boolean {
    return request.body?.query?.includes('mutation Login');
  }
}
