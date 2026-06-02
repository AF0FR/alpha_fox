export interface WaterfallFrame {
  center_frequency_hz: number;
  sample_rate_hz: number;
  min_db: number;
  max_db: number;
  bins: number[];
}
