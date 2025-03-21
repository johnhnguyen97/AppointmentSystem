import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-page-container',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="page-container">
      <ng-content></ng-content>
    </div>
  `,
  styleUrls: ['./page-container.component.sass']
})
export class PageContainerComponent {}
