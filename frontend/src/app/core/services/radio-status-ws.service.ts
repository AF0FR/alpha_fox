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
  private reconnectTimer: number | null = null;
  private manuallyClosed = false;

  connect(): void {
    this.manuallyClosed = false;

    if (this.socket) {
      return;
    }

    this.socket = new WebSocket(`${this.wsUrl}/ws/radio/status`);

    this.socket.onopen = () => {
      this.connected.set(true);
      this.clearReconnectTimer();
    };

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data) as RadioStatus;
      this.status.set(data);
    };

    this.socket.onclose = () => {
      this.connected.set(false);
      this.socket = null;

      if (!this.manuallyClosed) {
        this.scheduleReconnect();
      }
    };

    this.socket.onerror = () => {
      this.connected.set(false);
      this.socket?.close();
    };
  }

  disconnect(): void {
    this.manuallyClosed = true;
    this.clearReconnectTimer();
    this.socket?.close();
    this.socket = null;
    this.connected.set(false);
  }

  reconnect(): void {
    this.disconnect();
    this.manuallyClosed = false;
    this.connect();
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer !== null) {
      return;
    }

    this.reconnectTimer = window.setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, 1000);
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer === null) {
      return;
    }

    window.clearTimeout(this.reconnectTimer);
    this.reconnectTimer = null;
  }
}
