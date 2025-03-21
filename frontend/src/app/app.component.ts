import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { SidebarComponent } from './shared/layout/sidebar/sidebar.component';
import { MobileNavComponent } from './shared/layout/mobile-nav/mobile-nav.component';
import { HeaderComponent } from './shared/layout/header/header.component';
import { SidebarService } from './shared/services/sidebar.service';
import { ThemeService } from './shared/services/theme.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    SidebarComponent,
    MobileNavComponent,
    HeaderComponent
  ],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.sass']
})
export class AppComponent implements OnInit {
  title = 'NailBook Pro';
  isCollapsed$;
  isMobileCollapsed$;
  isLoginPage = false;

  constructor(
    private sidebarService: SidebarService,
    private themeService: ThemeService,
    private router: Router
  ) {
    this.isCollapsed$ = this.sidebarService.isCollapsed$;
    this.isMobileCollapsed$ = this.sidebarService.isMobileCollapsed$;

    // Subscribe to router events to detect login page
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe(() => {
      this.isLoginPage = this.router.url === '/login';
    });
  }

  ngOnInit() {
    this.themeService.isDarkTheme$.subscribe(isDark => {
      document.body.classList.toggle('dark-theme', isDark);
    });
  }
}
