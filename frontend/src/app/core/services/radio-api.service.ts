import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';

import { API_URL } from '../tokens/api-url.token';
import { RadioMode, RadioStatus } from '../models/radio-status.model';

@Injectable({
  providedIn: 'root',
})
export class RadioApiService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = inject(API_URL);

  getStatus() {
    return this.http.get<RadioStatus>(`${this.apiUrl}/radio/status`);
  }

  setFrequency(frequencyHz: number) {
    return this.http.post<RadioStatus>(`${this.apiUrl}/radio/frequency`, {
      frequency_hz: frequencyHz,
    });
  }

  setMode(mode: RadioMode) {
    return this.http.post<RadioStatus>(`${this.apiUrl}/radio/mode`, {
      mode,
    });
  }

  setPtt(enabled: boolean) {
    return this.http.post<RadioStatus>(`${this.apiUrl}/radio/ptt`, {
      enabled,
    });
  }
}
