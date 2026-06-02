import { inject, Injectable, signal } from '@angular/core';

import { RadioStatus } from '../models/radio-status.model';
import { WS_URL } from '../tokens/api-url.token';

@Injectable({
  providedIn: 'root',
})
export class RadioStatusWsService {
  private readonly wsUrl = inject(WS_URL);

  readonly status = signal<RadioStatus | null>(null);
  readonly connected = signal(false);

  private socket: WebSocket | null = null;

  connect(): void {
    if (this.socket) {
      return;
    }

    this.socket = new WebSocket(`${this.wsUrl}/ws/radio/status`);

    this.socket.onopen = () => {
      this.connected.set(true);
    };

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data) as RadioStatus;
      this.status.set(data);
    };

    this.socket.onclose = () => {
      this.connected.set(false);
      this.socket = null;
    };

    this.socket.onerror = () => {
      this.connected.set(false);
    };
  }

  disconnect(): void {
    this.socket?.close();
    this.socket = null;
    this.connected.set(false);
  }
}
