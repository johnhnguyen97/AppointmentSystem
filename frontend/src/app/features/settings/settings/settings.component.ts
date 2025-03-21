import { Component, ViewChild, ElementRef, AfterViewInit, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PageContainerComponent } from '../../../shared/layout/page-container/page-container.component';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatSelectModule } from '@angular/material/select';
import { MatDividerModule } from '@angular/material/divider';
import { FormsModule } from '@angular/forms';

interface SettingsSection {
  id: string;
  title: string;
  icon: string;
  subsections: {
    id: string;
    title: string;
    icon: string;
  }[];
}

@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.sass'],
  standalone: true,
  imports: [
    CommonModule,
    PageContainerComponent,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatListModule,
    MatSlideToggleModule,
    MatButtonToggleModule,
    MatExpansionModule,
    MatSelectModule,
    MatDividerModule,
    FormsModule
  ]
})
export class SettingsComponent implements AfterViewInit {
  @ViewChild('settingsContent') settingsContent?: ElementRef;
  
  selectedSection = '';
  expandedSection = '';
  isMobileView = window.innerWidth < 768;
  
  sections: SettingsSection[] = [
    {
      id: 'profile',
      title: 'Profile Settings',
      icon: 'account_circle',
      subsections: [
        { 
          id: 'personal',
          title: 'Personal Information',
          icon: 'person'
        },
        { 
          id: 'security',
          title: 'Security',
          icon: 'lock'
        },
        {
          id: 'preferences',
          title: 'Preferences',
          icon: 'settings'
        }
      ]
    },
    {
      id: 'appearance',
      title: 'Appearance',
      icon: 'palette',
      subsections: [
        {
          id: 'theme',
          title: 'Theme',
          icon: 'dark_mode'
        },
        {
          id: 'font',
          title: 'Font Settings',
          icon: 'format_size'
        },
        {
          id: 'layout',
          title: 'Layout Options',
          icon: 'view_quilt'
        }
      ]
    },
    {
      id: 'notifications',
      title: 'Notifications',
      icon: 'notifications',
      subsections: [
        {
          id: 'email',
          title: 'Email Notifications',
          icon: 'email'
        },
        {
          id: 'sms',
          title: 'SMS Notifications',
          icon: 'sms'
        },
        {
          id: 'push',
          title: 'Push Notifications',
          icon: 'notifications_active'
        }
      ]
    },
    {
      id: 'calendar',
      title: 'Calendar Settings',
      icon: 'calendar_today',
      subsections: [
        {
          id: 'workHours',
          title: 'Work Hours',
          icon: 'schedule'
        },
        {
          id: 'availability',
          title: 'Availability',
          icon: 'event_available'
        },
        {
          id: 'scheduling',
          title: 'Scheduling Rules',
          icon: 'rule'
        }
      ]
    },
    {
      id: 'integrations',
      title: 'Integrations',
      icon: 'integration_instructions',
      subsections: [
        {
          id: 'calendar-sync',
          title: 'Calendar Sync',
          icon: 'sync'
        },
        {
          id: 'payment',
          title: 'Payment Services',
          icon: 'payments'
        },
        {
          id: 'messaging',
          title: 'Messaging Services',
          icon: 'chat'
        }
      ]
    }
  ];

  timeZones = [
    'America/Chicago',
    'America/New_York',
    'America/Los_Angeles',
    'America/Phoenix',
    'Europe/London',
    'Europe/Paris',
    'Asia/Tokyo',
    'Australia/Sydney'
  ];

  languages = [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Spanish' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'it', name: 'Italian' },
    { code: 'pt', name: 'Portuguese' },
    { code: 'ja', name: 'Japanese' },
    { code: 'ko', name: 'Korean' }
  ];

  dateFormats = [
    { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY' },
    { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY' },
    { value: 'YYYY-MM-DD', label: 'YYYY-MM-DD' }
  ];

  timeFormats = [
    { value: '12', label: '12-hour' },
    { value: '24', label: '24-hour' }
  ];

  constructor() {
    window.addEventListener('resize', this.handleResize.bind(this));
  }

  ngAfterViewInit() {
    // Select first section by default
    if (!this.selectedSection && this.sections.length > 0) {
      this.selectSection(this.sections[0].id);
    }
  }

  selectSection(sectionId: string): void {
    const section = this.sections.find(s => s.id === sectionId);
    const subsection = this.sections.find(s => 
      s.subsections.some(sub => sub.id === sectionId)
    );

    if (section) {
      // Clicking on a main section
      if (this.expandedSection === sectionId) {
        // If already expanded, collapse it
        this.expandedSection = '';
        this.selectedSection = '';
      } else {
        // Expand the section and select its first subsection
        this.expandedSection = sectionId;
        this.selectedSection = section.subsections[0].id;
        this.scrollToSection(section.subsections[0].id);
      }
    } else if (subsection) {
      // Clicking on a subsection
      this.expandedSection = subsection.id;
      this.selectedSection = sectionId;
      this.scrollToSection(sectionId);
    }
  }

  private scrollToSection(sectionId: string): void {
    if (sectionId) {
      const element = document.getElementById(`section-${sectionId}`);
      if (element) {
        const headerOffset = this.isMobileView ? 100 : 20;
        const elementPosition = element.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });

        if (this.settingsContent) {
          this.settingsContent.nativeElement.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
          });
        }
      }
    }
  }

  @HostListener('window:resize')
  private handleResize(): void {
    this.isMobileView = window.innerWidth < 768;
  }

  isSelected(sectionId: string): boolean {
    return this.expandedSection === sectionId;
  }

  isSubsectionSelected(subsectionId: string): boolean {
    return this.selectedSection === subsectionId;
  }

  getParentSection(subsectionId: string): SettingsSection | undefined {
    return this.sections.find(section => 
      section.subsections.some(sub => sub.id === subsectionId)
    );
  }
}
