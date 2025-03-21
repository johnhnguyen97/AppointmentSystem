import { Component, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { SidebarService } from '../../services/sidebar.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatListModule,
    MatIconModule,
    MatButtonModule
  ],
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.sass']
})
export class SidebarComponent {
  userEmail = 'admin&#64;nailsalonpro.com';
  isCollapsed$;
  isMobileCollapsed$;
  isMobile = false;

  constructor(private sidebarService: SidebarService) {
    this.isCollapsed$ = this.sidebarService.isCollapsed$;
    this.isMobileCollapsed$ = this.sidebarService.isMobileCollapsed$;
    this.checkScreenSize();
  }

  @HostListener('window:resize')
  onResize() {
    this.checkScreenSize();
  }

  private checkScreenSize() {
    const wasMobile = this.isMobile;
    this.isMobile = window.innerWidth <= 576;
    
    // Reset mobile collapsed state when transitioning from mobile to desktop
    if (wasMobile && !this.isMobile) {
      this.sidebarService.resetMobileCollapsed();
    }
  }

  toggleSidebar() {
    this.sidebarService.toggleSidebar(this.isMobile);
  }
}
