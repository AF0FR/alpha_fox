import { HttpClient } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';

import { AppStatus } from '../models/app-status.model';
import { API_URL } from '../tokens/api-url.token';

@Injectable({
  providedIn: 'root',
})
export class AppStatusService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = inject(API_URL);

  readonly status = signal<AppStatus | null>(null);

  refresh(): void {
    this.http.get<AppStatus>(`${this.apiUrl}/app/status`).subscribe({
      next: (status) => {
        this.status.set(status);
      },
      error: () => {
        this.status.set({
          app: 'alpha_fox',
          backend: 'disconnected',
          active_radio_backend: 'mock',
          available_radio_backends: [],
          radio_connected: false,
        });
      },
    });
  }
}
