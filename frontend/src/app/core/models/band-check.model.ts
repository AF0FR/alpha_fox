export interface BandCheckResult {
  frequency_hz: number;
  allowed: boolean;
  band_name: string | null;
  lower_hz: number | null;
  upper_hz: number | null;
  message: string;
}
