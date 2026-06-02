import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { RadioApiService } from '../../core/services/radio-api.service';
import { RadioStatusWsService } from '../../core/services/radio-status-ws.service';
import { RadioMode } from '../../core/models/radio-status.model';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './dashboard.html',
})
export class Dashboard implements OnInit {
  private readonly radioApi = inject(RadioApiService);
  readonly radioWs = inject(RadioStatusWsService);

  readonly frequencyInput = signal('14074000');

  readonly status = computed(() => this.radioWs.status());

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

  ngOnInit(): void {
    this.radioWs.connect();

    this.radioApi.getStatus().subscribe((status) => {
      this.frequencyInput.set(status.frequency_hz.toString());
      this.radioWs.status.set(status);
    });
  }

  formatFrequency(frequencyHz: number | undefined): string {
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

    this.radioApi.setFrequency(frequencyHz).subscribe((status) => {
      this.radioWs.status.set(status);
    });
  }

  setMode(mode: RadioMode): void {
    this.radioApi.setMode(mode).subscribe((status) => {
      this.radioWs.status.set(status);
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

    this.radioApi.setPtt(!current.ptt).subscribe((status) => {
      this.radioWs.status.set(status);
    });
  }
}
