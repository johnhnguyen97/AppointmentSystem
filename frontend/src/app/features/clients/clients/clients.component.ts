import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PageContainerComponent } from '../../../shared/layout/page-container/page-container.component';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTableModule } from '@angular/material/table';
import { MatMenuModule } from '@angular/material/menu';
import { MatPaginatorModule } from '@angular/material/paginator';
import { ClientsService } from '../services/clients.service';
import { Client, ColumnDefinition } from '../models/client.interface';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-clients',
  templateUrl: './clients.component.html',
  styleUrls: ['./clients.component.sass'],
  standalone: true,
  imports: [
    CommonModule,
    PageContainerComponent,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatIconModule,
    MatButtonModule,
    MatTableModule,
    MatMenuModule,
    MatPaginatorModule
  ]
})
export class ClientsComponent implements OnInit, OnDestroy {
  displayedColumns: string[] = [];
  dataSource: Client[] = [];
  columns: ColumnDefinition[] = [];
  private baseColumns: ColumnDefinition[] = [];
  private destroy$ = new Subject<void>();
  private resizeTimeout: any;
  private isMobile = window.innerWidth < 768;

  constructor(private clientsService: ClientsService) {}

  ngOnInit(): void {
    // Get base columns and set initial columns
    this.baseColumns = this.clientsService.getBaseColumns();
    this.columns = [...this.baseColumns];
    this.displayedColumns = this.columns.map(col => col.key.toString());
    
    // Subscribe to clients data
    this.clientsService.getClients()
      .pipe(takeUntil(this.destroy$))
      .subscribe(clients => {
        this.dataSource = clients;
      });

    // Initial resize check
    this.handleResize();

    // Setup resize handling with debounce
    window.addEventListener('resize', () => {
      if (this.resizeTimeout) {
        clearTimeout(this.resizeTimeout);
      }
      this.resizeTimeout = setTimeout(() => {
        this.handleResize();
        // Force change detection if needed
        this.columns = [...this.columns];
      }, 150);
    });
  }

  ngOnDestroy(): void {
    if (this.resizeTimeout) {
      clearTimeout(this.resizeTimeout);
    }
    this.destroy$.next();
    this.destroy$.complete();
  }

  private handleResize(): void {
    const width = window.innerWidth;
    this.isMobile = width < 768;

    if (this.isMobile) {
      // Mobile view
      this.columns = this.clientsService.getMobileColumns();
    } else if (width < 1024) {
      // Tablet view
      this.columns = this.clientsService.getTabletColumns();
    } else {
      // Desktop view - use base columns
      this.columns = [...this.baseColumns];
    }

    // Update displayed columns
    this.displayedColumns = this.columns.map(col => col.key.toString());
  }

  formatColumnValue(client: Client, column: ColumnDefinition): string {
    const value = client[column.key];
    
    if (column.type === 'date' && value instanceof Date) {
      return value.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: this.isMobile ? undefined : 'numeric'
      });
    }
    
    return value?.toString() || '';
  }
}
