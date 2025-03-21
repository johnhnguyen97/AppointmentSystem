import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { Client, ColumnDefinition } from '../models/client.interface';

@Injectable({
  providedIn: 'root'
})
export class ClientsService {
  private columnsSubject = new BehaviorSubject<ColumnDefinition[]>([
    { key: 'name', header: 'Name', type: 'text', width: '14.28%', align: 'left' },
    { key: 'email', header: 'Email', type: 'text', width: '14.28%', align: 'left' },
    { key: 'phone', header: 'Phone', type: 'text', width: '14.28%', align: 'left' },
    { key: 'nextAppointment', header: 'Next Appt.', type: 'date', width: '14.28%', align: 'left' },
    { key: 'preferredService', header: 'Service', type: 'text', width: '14.28%', align: 'left' },
    { key: 'status', header: 'Status', type: 'status', width: '14.28%', align: 'center' },
    { key: 'id', header: 'Actions', type: 'actions', width: '14.28%', align: 'center' }
  ]);

  // Mock data for demonstration
  private clientsSubject = new BehaviorSubject<Client[]>([
    {
      id: '1',
      name: 'John Doe',
      phone: '(555) 123-4567',
      email: 'john@example.com',
      address: '123 Main St, City, State 12345',
      lastVisit: new Date('2024-01-15'),
      nextAppointment: new Date('2024-02-20'),
      preferredService: 'Haircut',
      status: 'active'
    },
    {
      id: '2',
      name: 'Jane Smith',
      phone: '(555) 987-6543',
      email: 'jane@example.com',
      address: '456 Oak St, City, State 12345',
      lastVisit: new Date('2024-02-01'),
      nextAppointment: new Date('2024-02-25'),
      preferredService: 'Color',
      status: 'new'
    }
  ]);

  getColumns(): Observable<ColumnDefinition[]> {
    return this.columnsSubject.asObservable();
  }

  getClients(): Observable<Client[]> {
    return this.clientsSubject.asObservable();
  }

  getBaseColumns(): ColumnDefinition[] {
    return this.columnsSubject.value;
  }

  getMobileColumns(): ColumnDefinition[] {
    return [
      { key: 'name', header: 'Name', type: 'text', width: '33.33%', align: 'left' },
      { key: 'status', header: 'Status', type: 'status', width: '33.33%', align: 'center' },
      { key: 'id', header: '', type: 'actions', width: '33.33%', align: 'center' }
    ];
  }

  getTabletColumns(): ColumnDefinition[] {
    return [
      { key: 'name', header: 'Name', type: 'text', width: '25%', align: 'left' },
      { key: 'email', header: 'Email', type: 'text', width: '25%', align: 'left' },
      { key: 'status', header: 'Status', type: 'status', width: '25%', align: 'center' },
      { key: 'id', header: 'Actions', type: 'actions', width: '25%', align: 'center' }
    ];
  }
}
