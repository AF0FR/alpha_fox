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
  s_meter_raw?: number | null;

  tx_power_level?: number | null;
  af_gain?: number | null;
  rf_gain?: number | null;
  mic_gain?: number | null;
  key_speed_wpm?: number | null;

  rf_gain_experimental?: boolean;
}


export type RadioBackend = 'mock' | 'sim' | 'hamlib';

export interface RadioBackendInfo {
  active_backend: RadioBackend;
  available_backends: RadioBackend[];
}


export interface TxSafetyStatus {
  tx_armed: boolean;
  message: string;
}
