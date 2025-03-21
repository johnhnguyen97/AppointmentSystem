import { Injectable } from '@angular/core';
import { Apollo, gql } from 'apollo-angular';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

const LOGIN_MUTATION = gql`
  mutation Login($input: LoginInput!) {
    login(input: $input) {
      token
      user {
        id
        username
        email
        first_name
        last_name
        enabled
        is_admin
      }
    }
  }
`;

export interface AuthUser {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  enabled: boolean;
  is_admin: boolean;
}

export interface AuthResponse {
  token: string;
  user: AuthUser;
}

interface GraphQLResponse<T> {
  data: T;
  errors?: Array<{ message: string }>;
}

interface LoginResponse {
  login: AuthResponse;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private currentUserSubject: BehaviorSubject<AuthUser | null>;
  public currentUser: Observable<AuthUser | null>;

  constructor(private apollo: Apollo) {
    const user = this.getUserFromStorage();
    this.currentUserSubject = new BehaviorSubject<AuthUser | null>(user);
    this.currentUser = this.currentUserSubject.asObservable();
  }

  public get currentUserValue(): AuthUser | null {
    return this.currentUserSubject.value;
  }

  login(username: string, password: string, rememberMe: boolean = false): Observable<AuthResponse> {
    return this.apollo.mutate<{ login: AuthResponse }>({
      mutation: LOGIN_MUTATION,
      variables: {
        input: { username, password }
      }
    }).pipe(
      map(result => {
        if (!result.data) {
          throw new Error('Login failed - no data received');
        }
        const authResponse = result.data.login;
        this.setSession(authResponse, rememberMe);
        this.currentUserSubject.next(authResponse.user);
        return authResponse;
      }),
      catchError(error => {
        console.error('Login error:', error);
        return throwError(() => new Error('Authentication failed'));
      })
    );
  }

  logout(): void {
    // Clean up local storage
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('remember');

    // Clean up session storage
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('user');
    sessionStorage.removeItem('remember');

    // Reset Apollo store
    this.apollo.client.resetStore()
      .catch(err => console.error('Error resetting Apollo cache:', err));

    // Clear current user
    this.currentUserSubject.next(null);
  }

  isAuthenticated(): boolean {
    const token = this.getToken();
    if (!token) return false;

    try {
      const tokenData = JSON.parse(atob(token.split('.')[1]));
      const expirationDate = tokenData.exp * 1000;
      return Date.now() < expirationDate;
    } catch {
      return false;
    }
  }

  getToken(): string | null {
    return localStorage.getItem('token') || sessionStorage.getItem('token');
  }

  isRememberMe(): boolean {
    return localStorage.getItem('remember') === 'true';
  }

  private setSession(authResult: AuthResponse, rememberMe: boolean = false): void {
    const storage = rememberMe ? localStorage : sessionStorage;
    storage.setItem('token', authResult.token);
    storage.setItem('user', JSON.stringify(authResult.user));
    storage.setItem('remember', String(rememberMe));
  }

  private getUserFromStorage(): AuthUser | null {
    const userStr = localStorage.getItem('user') || sessionStorage.getItem('user');
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch {
        return null;
      }
    }
    return null;
  }
}
