import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { RadioApiService } from '../../core/services/radio-api.service';
import { RadioStatusWsService } from '../../core/services/radio-status-ws.service';
import { WaterfallWsService } from '../../core/services/waterfall-ws.service';
import { RadioBackend, RadioMode } from '../../core/models/radio-status.model';
import { WaterfallView } from '../../waterfall/waterfall-view/waterfall-view';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [FormsModule, WaterfallView],
  templateUrl: './dashboard.html',
})
export class Dashboard implements OnInit {
  private readonly radioApi = inject(RadioApiService);
  readonly radioWs = inject(RadioStatusWsService);
  readonly waterfallWs = inject(WaterfallWsService);

  readonly frequencyInput = signal('14074000');

  readonly status = computed(() => this.radioWs.status());
  readonly latestWaterfallFrame = computed(() => this.waterfallWs.latestFrame());

  readonly modes: RadioMode[] = ['LSB', 'USB', 'AM', 'CW', 'CWR', 'NFM'];

  readonly bandPresets = [
    { label: '80m FT8', frequencyHz: 3573000, mode: 'USB' as RadioMode },
    { label: '40m FT8', frequencyHz: 7074000, mode: 'USB' as RadioMode },
    { label: '30m FT8', frequencyHz: 10136000, mode: 'USB' as RadioMode },
    { label: '20m FT8', frequencyHz: 14074000, mode: 'USB' as RadioMode },
    { label: '17m FT8', frequencyHz: 18100000, mode: 'USB' as RadioMode },
    { label: '15m FT8', frequencyHz: 21074000, mode: 'USB' as RadioMode },
    { label: '10m FT8', frequencyHz: 28074000, mode: 'USB' as RadioMode },
  ];

  readonly activeBackend = signal<RadioBackend>('mock');
  readonly availableBackends = signal<RadioBackend[]>([]);
  readonly backendError = signal<string | null>(null);
  readonly commandError = signal<string | null>(null);

  ngOnInit(): void {
    console.log('Dashboard ngOnInit running');

    this.radioWs.connect();
    this.waterfallWs.connect();

    this.radioApi.getBackend().subscribe((info) => {
      console.log('Backend info:', info);
      this.activeBackend.set(info.active_backend);
      this.availableBackends.set(info.available_backends);
    });

    this.radioApi.getStatus().subscribe((status) => {
      console.log('Radio status:', status);
      this.frequencyInput.set(status.frequency_hz.toString());
      this.radioWs.status.set(status);
    });
  }

  formatFrequency(frequencyHz: number | undefined | null): string {
    if (!frequencyHz) {
      return '--.---.---';
    }

    return (frequencyHz / 1_000_000).toFixed(6);
  }

  setFrequency(): void {
    const frequencyHz = Number(this.frequencyInput());

    if (!Number.isFinite(frequencyHz) || frequencyHz <= 0) {
      return;
    }

    this.tuneToFrequency(frequencyHz);
  }

  tuneToFrequency(frequencyHz: number): void {
    this.commandError.set(null);

    const roundedFrequency = Math.round(frequencyHz);

    this.radioApi.setFrequency(roundedFrequency).subscribe({
      next: (status) => {
        this.frequencyInput.set(status.frequency_hz.toString());
        this.radioWs.status.set(status);
      },
      error: (error) => {
        const current = this.status();

        if (current) {
          this.frequencyInput.set(current.frequency_hz.toString());
        }

        this.commandError.set(error.error?.detail ?? 'Failed to set frequency.');
      },
    });
  }

  setMode(mode: RadioMode): void {
    this.commandError.set(null);

    this.radioApi.setMode(mode).subscribe({
      next: (status) => {
        this.radioWs.status.set(status);
      },
      error: (error) => {
        this.commandError.set(error.error?.detail ?? 'Failed to set mode.');
      },
    });
  }

  setPreset(frequencyHz: number, mode: RadioMode): void {
    this.frequencyInput.set(frequencyHz.toString());

    this.radioApi.setFrequency(frequencyHz).subscribe((status) => {
      this.radioWs.status.set(status);

      this.radioApi.setMode(mode).subscribe((modeStatus) => {
        this.radioWs.status.set(modeStatus);
      });
    });
  }

  togglePtt(): void {
    const current = this.status();

    if (!current) {
      return;
    }

    this.commandError.set(null);

    this.radioApi.setPtt(!current.ptt).subscribe({
      next: (status) => {
        this.radioWs.status.set(status);
      },
      error: (error) => {
        this.commandError.set(error.error?.detail ?? 'Failed to toggle PTT.');
      },
    });
  }

  onBackendChange(event: Event): void {
    const select = event.target as HTMLSelectElement;
    const backend = select.value as RadioBackend;

    console.log('Backend dropdown changed:', backend);

    this.commandError.set(null);
    this.setBackend(backend);
  }

  setBackend(backend: RadioBackend): void {
    console.log('setBackend called:', backend);

    if (backend === this.activeBackend()) {
      console.log('Backend already active, skipping:', backend);
      return;
    }

    this.backendError.set(null);
    this.commandError.set(null);

    this.radioApi.setBackend(backend).subscribe({
      next: (info) => {
        console.log('Backend switched:', info);

        this.activeBackend.set(info.active_backend);
        this.availableBackends.set(info.available_backends);

        this.radioWs.reconnect();
        this.waterfallWs.reconnect();

        this.radioApi.getStatus().subscribe({
          next: (status) => {
            this.frequencyInput.set(status.frequency_hz.toString());
            this.radioWs.status.set(status);
          },
          error: (error) => {
            this.commandError.set(error.error?.detail ?? 'Failed to refresh radio status.');
          },
        });
      },
      error: (error) => {
        console.error('Backend switch failed:', error);
        this.backendError.set(error.error?.detail ?? 'Failed to switch radio backend.');
      },
    });
  }
}
