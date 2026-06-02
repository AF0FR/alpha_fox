import { InjectionToken } from '@angular/core';

export const API_URL = new InjectionToken<string>('API_URL', {
  providedIn: 'root',
  factory: () => 'http://127.0.0.1:8000',
});

export const WS_URL = new InjectionToken<string>('WS_URL', {
  providedIn: 'root',
  factory: () => 'ws://127.0.0.1:8000',
});
