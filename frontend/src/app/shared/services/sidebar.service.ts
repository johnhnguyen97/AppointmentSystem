import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SidebarService {
  private isCollapsedSubject = new BehaviorSubject<boolean>(false);
  private isMobileCollapsedSubject = new BehaviorSubject<boolean>(false);
  
  isCollapsed$ = this.isCollapsedSubject.asObservable();
  isMobileCollapsed$ = this.isMobileCollapsedSubject.asObservable();

  toggleSidebar(isMobile = false) {
    if (isMobile) {
      this.isMobileCollapsedSubject.next(!this.isMobileCollapsedSubject.value);
    } else {
      this.isCollapsedSubject.next(!this.isCollapsedSubject.value);
    }
  }

  resetMobileCollapsed() {
    this.isMobileCollapsedSubject.next(false);
  }

  getIsCollapsed(isMobile = false) {
    return isMobile ? this.isMobileCollapsedSubject.value : this.isCollapsedSubject.value;
  }
}
