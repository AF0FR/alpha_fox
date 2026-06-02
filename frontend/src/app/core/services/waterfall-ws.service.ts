import { inject, Injectable, signal } from '@angular/core';

import { WaterfallFrame } from '../models/waterfall-frame.model';
import { WS_URL } from '../tokens/api-url.token';

@Injectable({
  providedIn: 'root',
})
export class WaterfallWsService {
  private readonly wsUrl = inject(WS_URL);

  readonly connected = signal(false);
  readonly latestFrame = signal<WaterfallFrame | null>(null);

  private socket: WebSocket | null = null;

  connect(): void {
    if (this.socket) {
      return;
    }

    this.socket = new WebSocket(`${this.wsUrl}/ws/waterfall`);

    this.socket.onopen = () => {
      this.connected.set(true);
    };

    this.socket.onmessage = (event) => {
      const frame = JSON.parse(event.data) as WaterfallFrame;
      this.latestFrame.set(frame);
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
