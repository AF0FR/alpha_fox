export type RadioMode = 'LSB' | 'USB' | 'AM' | 'CW' | 'CWR' | 'NFM';

export interface RadioStatus {
  connected: boolean;
  radio_name: string;
  frequency_hz: number;
  mode: RadioMode;
  ptt: boolean;
  vfo: string;
  swr: number | null;
  power_watts: number | null;
  alc: number | null;
  voltage: number | null;
}


export type RadioBackend = 'mock' | 'sim' | 'hamlib';

export interface RadioBackendInfo {
  active_backend: RadioBackend;
  available_backends: RadioBackend[];
}
