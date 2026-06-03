import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { RadioApiService } from '../../core/services/radio-api.service';
import { RadioStatusWsService } from '../../core/services/radio-status-ws.service';
import { WaterfallWsService } from '../../core/services/waterfall-ws.service';
import { RadioBackend, RadioMode, RadioStatus } from '../../core/models/radio-status.model';
import { WaterfallView } from '../../waterfall/waterfall-view/waterfall-view';
import { AppStatusService } from '../../core/services/app-status.service';
import { BandCheckResult } from '../../core/models/band-check.model';
import {
  formatFrequencyInput,
  formatFrequencyMHz,
  parseFrequencyInput,
} from '../../core/utils/frequency.util';


@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [FormsModule, RouterLink, WaterfallView],
  templateUrl: './dashboard.html',
})
export class Dashboard implements OnInit {
  private readonly radioApi = inject(RadioApiService);
  readonly radioWs = inject(RadioStatusWsService);
  readonly waterfallWs = inject(WaterfallWsService);
  readonly appStatus = inject(AppStatusService);

  readonly frequencyInput = signal('14074000');
  readonly bandCheck = signal<BandCheckResult | null>(null);
  readonly bandWarning = signal<string | null>(null);

  readonly txArmed = signal(false);

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

  readonly commandError = signal<string | null>(null);

  ngOnInit(): void {
    console.log('Dashboard ngOnInit running');

    this.appStatus.refresh();

    this.radioWs.connect();
    this.waterfallWs.connect();

    this.radioApi.getBackend().subscribe((info) => {
      console.log('Backend info:', info);
    });

    this.radioApi.getStatus().subscribe((radioStatus) => {
      console.log('Radio status:', radioStatus);
      this.frequencyInput.set(formatFrequencyInput(radioStatus.frequency_hz));
      this.radioWs.status.set(radioStatus);
    });

    this.radioApi.getTxArmStatus().subscribe((txStatus) => {
      this.txArmed.set(txStatus.tx_armed);
    });
  }

  toggleTxArm(): void {
    this.commandError.set(null);

    if (this.txArmed()) {
      this.radioApi.disarmTxBackend().subscribe({
        next: (txStatus) => {
          this.txArmed.set(txStatus.tx_armed);

          this.radioApi.getStatus().subscribe((radioStatus) => {
            this.radioWs.status.set(radioStatus);
          });
        },
        error: (error) => {
          this.commandError.set(error.error?.detail ?? 'Failed to disarm TX.');
        },
      });

      return;
    }

    this.radioApi.armTx().subscribe({
      next: (txStatus) => {
        this.txArmed.set(txStatus.tx_armed);
      },
      error: (error) => {
        this.commandError.set(error.error?.detail ?? 'Failed to arm TX.');
      },
    });
  }

  disarmTx(): void {
    this.txArmed.set(false);
  }

  formatFrequency(frequencyHz: number | undefined | null): string {
    return formatFrequencyMHz(frequencyHz);
  }

  setFrequency(): void {
    const result = parseFrequencyInput(this.frequencyInput());

    if (result.error || result.frequencyHz === null) {
      this.commandError.set(result.error ?? 'Invalid frequency.');
      return;
    }

    this.validateAndTune(result.frequencyHz);
  }

  validateAndTune(frequencyHz: number): void {
    this.commandError.set(null);
    this.bandWarning.set(null);

    const roundedFrequency = Math.round(frequencyHz);

    this.radioApi.checkBand(roundedFrequency).subscribe({
      next: (result) => {
        this.bandCheck.set(result);

      if (!result.allowed) {
        this.bandWarning.set(`TX blocked: ${result.message}`);
      } else {
        this.bandWarning.set(null);
      }

      this.tuneToFrequency(roundedFrequency);
      },
      error: (error) => {
        this.commandError.set(error.error?.detail ?? 'Failed to validate frequency.');
      },
    });
  }

  tuneToFrequency(frequencyHz: number): void {
    this.commandError.set(null);

    const roundedFrequency = Math.round(frequencyHz);

    this.radioApi.setFrequency(roundedFrequency).subscribe({
      next: (radioStatus: RadioStatus): void => {
        this.frequencyInput.set(formatFrequencyInput(radioStatus.frequency_hz));
        this.radioWs.status.set(radioStatus);
        this.bandWarning.set(null);
      },
      error: (error: any): void => {
        const current = this.status();

        if (current) {
          this.frequencyInput.set(formatFrequencyInput(current.frequency_hz));
        }

        this.commandError.set(error.error?.detail ?? 'Failed to set frequency.');
      },
    });
  }

  setMode(mode: RadioMode): void {
    this.commandError.set(null);

    this.radioApi.setMode(mode).subscribe({
      next: (radioStatus) => {
        this.radioWs.status.set(radioStatus);
      },
      error: (error) => {
        this.commandError.set(error.error?.detail ?? 'Failed to set mode.');
      },
    });
  }

  setPreset(frequencyHz: number, mode: RadioMode): void {
    this.commandError.set(null);
    this.bandWarning.set(null);
    this.frequencyInput.set(formatFrequencyInput(frequencyHz));

    this.radioApi.checkBand(frequencyHz).subscribe({
      next: (bandCheck) => {
        this.bandCheck.set(bandCheck);

        if (!bandCheck.allowed) {
          this.bandWarning.set(`RX only: ${bandCheck.message}`);
        } else {
          this.bandWarning.set(null);
        }

        this.radioApi.setFrequency(frequencyHz).subscribe({
          next: (radioStatus) => {
            this.frequencyInput.set(formatFrequencyInput(radioStatus.frequency_hz));
            this.radioWs.status.set(radioStatus);

            this.radioApi.setMode(mode).subscribe({
              next: (modeStatus) => {
                this.radioWs.status.set(modeStatus);
              },
              error: (error) => {
                this.commandError.set(error.error?.detail ?? 'Failed to set preset mode.');
              },
            });
          },
          error: (error) => {
            const current = this.status();

            if (current) {
              this.frequencyInput.set(formatFrequencyInput(current.frequency_hz));
            }

            this.commandError.set(error.error?.detail ?? 'Failed to set preset frequency.');
          },
        });
      },
      error: (error) => {
        this.commandError.set(error.error?.detail ?? 'Failed to validate preset frequency.');
      },
    });
  }

  togglePtt(): void {
    const current = this.status();

    if (!current) {
      return;
    }

    if (!this.txArmed()) {
      this.commandError.set('TX is not armed. Click Arm TX before using PTT.');
      return;
    }

    this.commandError.set(null);

    this.radioApi.setPtt(!current.ptt).subscribe({
      next: (radioStatus) => {
        this.radioWs.status.set(radioStatus);

        if (!radioStatus.ptt) {
          this.disarmTx();
        }
      },
      error: (error) => {
        this.disarmTx();
        this.commandError.set(error.error?.detail ?? 'Failed to toggle PTT.');
      },
    });
  }

  setTxPowerLevel(value: string): void {
    this.setRadioLevel(() => this.radioApi.setTxPowerLevel(Number(value)));
  }

  setAfGain(value: string): void {
    this.setRadioLevel(() => this.radioApi.setAfGain(Number(value)));
  }

  setRfGain(value: string): void {
    this.setRadioLevel(() => this.radioApi.setRfGain(Number(value)));
  }

  setMicGain(value: string): void {
    this.setRadioLevel(() => this.radioApi.setMicGain(Number(value)));
  }

  setKeySpeed(value: string): void {
    this.setRadioLevel(() => this.radioApi.setKeySpeed(Number(value)));
  }

  private setRadioLevel(request: () => any): void {
    this.commandError.set(null);

    request().subscribe({
      next: (radioStatus: RadioStatus) => {
        this.radioWs.status.set(radioStatus);
      },
      error: (error: any) => {
        this.commandError.set(error.error?.detail ?? 'Failed to set radio control.');
      },
    });
  }
}
