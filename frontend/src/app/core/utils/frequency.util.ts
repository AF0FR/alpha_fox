export interface FrequencyParseResult {
  frequencyHz: number | null;
  error: string | null;
}

export function parseFrequencyInput(input: string): FrequencyParseResult {
  const trimmed = input.trim().toLowerCase();

  if (!trimmed) {
    return {
      frequencyHz: null,
      error: 'Frequency is required.',
    };
  }

  const normalized = trimmed
    .replaceAll(',', '')
    .replace(/\s+/g, '');

  const match = normalized.match(/^([0-9]*\.?[0-9]+)(hz|khz|k|mhz|m)?$/);

  if (!match) {
    return {
      frequencyHz: null,
      error: 'Frequency must look like 14.074, 14.074 MHz, 7074 kHz, or 14074000.',
    };
  }

  const value = Number(match[1]);
  const unit = match[2] ?? inferUnit(normalized, value);

  if (!Number.isFinite(value) || value <= 0) {
    return {
      frequencyHz: null,
      error: 'Frequency must be a positive number.',
    };
  }

  const multiplier = unitMultiplier(unit);
  const frequencyHz = Math.round(value * multiplier);

  return {
    frequencyHz,
    error: null,
  };
}

export function formatFrequencyMHz(frequencyHz: number | null | undefined): string {
  if (!frequencyHz) {
    return '--.---.---';
  }

  return (frequencyHz / 1_000_000).toFixed(6);
}

export function formatFrequencyInput(frequencyHz: number | null | undefined): string {
  if (!frequencyHz) {
    return '';
  }

  return (frequencyHz / 1_000_000).toFixed(6);
}

function inferUnit(rawInput: string, value: number): 'hz' | 'khz' | 'mhz' {
  if (rawInput.includes('.')) {
    return 'mhz';
  }

  if (value >= 1_000_000) {
    return 'hz';
  }

  if (value >= 1_000) {
    return 'khz';
  }

  return 'mhz';
}

function unitMultiplier(unit: string): number {
  switch (unit) {
    case 'hz':
      return 1;

    case 'khz':
    case 'k':
      return 1_000;

    case 'mhz':
    case 'm':
      return 1_000_000;

    default:
      return 1;
  }
}
