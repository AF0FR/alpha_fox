import { Component, inject, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';

import { AppStatusService } from '../../core/services/app-status.service';
import { RadioApiService, RadioConnectionTestResult } from '../../core/services/radio-api.service';
import { RadioBackend } from '../../core/models/radio-status.model';
import { formatFrequencyMHz } from '../../core/utils/frequency.util';

@Component({
  selector: 'app-settings-page',
  standalone: true,
  imports: [FormsModule, RouterLink],
  templateUrl: './settings-page.html',
})
export class SettingsPage implements OnInit {
  readonly appStatus = inject(AppStatusService);
  private readonly radioApi = inject(RadioApiService);

  activeBackend: RadioBackend = 'mock';
  availableBackends: RadioBackend[] = [];

  backendError: string | null = null;
  backendMessage: string | null = null;

  connectionTestRunning = false;
  connectionTestResult: RadioConnectionTestResult | null = null;
  connectionTestError: string | null = null;

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {
    this.appStatus.refresh();

    this.radioApi.getBackend().subscribe({
      next: (info) => {
        this.activeBackend = info.active_backend;
        this.availableBackends = info.available_backends;
      },
      error: (error) => {
        this.backendError = error.error?.detail ?? 'Failed to load radio backend settings.';
      },
    });
  }

  setBackend(backend: RadioBackend): void {
    if (backend === this.activeBackend) {
      return;
    }

    this.backendError = null;
    this.backendMessage = null;
    this.connectionTestResult = null;
    this.connectionTestError = null;

    this.radioApi.setBackend(backend).subscribe({
      next: (info) => {
        this.activeBackend = info.active_backend;
        this.availableBackends = info.available_backends;
        this.backendMessage = `Radio backend switched to ${info.active_backend}.`;
        this.appStatus.refresh();
      },
      error: (error) => {
        this.backendError = error.error?.detail ?? 'Failed to switch radio backend.';
      },
    });
  }

  testRadioConnection(): void {
    this.connectionTestRunning = true;
    this.connectionTestResult = null;
    this.connectionTestError = null;
    this.backendError = null;
    this.backendMessage = null;

    this.radioApi.testConnection().subscribe({
      next: (result) => {
        this.connectionTestResult = result;
        this.connectionTestRunning = false;
        this.appStatus.refresh();
      },
      error: (error) => {
        this.connectionTestRunning = false;
        this.connectionTestError = error.error?.detail ?? 'Radio connection test failed.';
      },
    });
  }

  formatFrequency(frequencyHz: number | null | undefined): string {
    return formatFrequencyMHz(frequencyHz);
  }

  formatLevel(value: unknown): string {
    if (value === null || value === undefined) {
      return '-';
    }

    if (typeof value === 'number') {
      return Number.isInteger(value) ? value.toString() : value.toFixed(2);
    }

    return String(value);
  }
}
