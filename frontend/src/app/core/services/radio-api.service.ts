import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';

import { API_URL } from '../tokens/api-url.token';
import {
  RadioBackend,
  RadioBackendInfo,
  RadioMode,
  RadioStatus,
  TxSafetyStatus,
} from '../models/radio-status.model';
import { BandCheckResult } from '../models/band-check.model';


export interface RadioConnectionTestResult {
  connected: boolean;
  backend: RadioBackend;
  radio_name?: string | null;
  frequency_hz?: number | null;
  mode?: RadioMode | null;
  ptt?: boolean | null;
  levels: Record<string, unknown>;
  errors: string[];
}


@Injectable({
  providedIn: 'root',
})
export class RadioApiService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = inject(API_URL);

  getStatus() {
    return this.http.get<RadioStatus>(`${this.apiUrl}/radio/status`);
  }

  getTxArmStatus() {
    return this.http.get<TxSafetyStatus>(`${this.apiUrl}/radio/tx-arm`);
  }

  armTx() {
    return this.http.post<TxSafetyStatus>(`${this.apiUrl}/radio/tx-arm`, {});
  }

  disarmTxBackend() {
    return this.http.post<TxSafetyStatus>(`${this.apiUrl}/radio/tx-disarm`, {});
  }

  setFrequency(frequencyHz: number) {
    return this.http.post<RadioStatus>(`${this.apiUrl}/radio/frequency`, {
      frequency_hz: frequencyHz,
    });
  }

  checkBand(frequencyHz: number) {
    return this.http.get<BandCheckResult>(
      `${this.apiUrl}/radio/band-check/${frequencyHz}`,
    );
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

  setTxPowerLevel(value: number) {
    return this.http.post<RadioStatus>(`${this.apiUrl}/radio/tx-power`, { value });
  }

  setAfGain(value: number) {
    return this.http.post<RadioStatus>(`${this.apiUrl}/radio/af-gain`, { value });
  }

  setRfGain(value: number) {
    return this.http.post<RadioStatus>(`${this.apiUrl}/radio/rf-gain`, { value });
  }

  setMicGain(value: number) {
    return this.http.post<RadioStatus>(`${this.apiUrl}/radio/mic-gain`, { value });
  }

  setKeySpeed(wpm: number) {
    return this.http.post<RadioStatus>(`${this.apiUrl}/radio/key-speed`, { wpm });
  }

  getBackend() {
    return this.http.get<RadioBackendInfo>(`${this.apiUrl}/radio/backend`);
  }

  setBackend(backend: RadioBackend) {
    return this.http.post<RadioBackendInfo>(`${this.apiUrl}/radio/backend`, {
      backend,
    });
  }

  testConnection() {
    return this.http.get<RadioConnectionTestResult>(`${this.apiUrl}/radio/connection-test`);
  }
}
