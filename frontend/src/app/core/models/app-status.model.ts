import { RadioBackend } from './radio-status.model';

export interface AppStatus {
  app: string;
  backend: string;
  active_radio_backend: RadioBackend;
  available_radio_backends: RadioBackend[];
  radio_connected: boolean;
}
