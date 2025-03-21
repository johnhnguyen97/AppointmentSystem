import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { SidebarService } from '../../services/sidebar.service';

@Component({
  selector: 'app-mobile-nav',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatIconModule
  ],
  templateUrl: './mobile-nav.component.html',
  styleUrls: ['./mobile-nav.component.sass']
})
export class MobileNavComponent {
  private sidebarService = inject(SidebarService);
  isCollapsed$ = this.sidebarService.isMobileCollapsed$;

  toggleNav() {
    this.sidebarService.toggleSidebar(true);
  }
}
