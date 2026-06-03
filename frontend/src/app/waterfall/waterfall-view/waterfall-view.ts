import {
  AfterViewInit,
  Component,
  ElementRef,
  effect,
  inject,
  input,
  OnDestroy,
  output,
  signal,
  viewChild,
} from '@angular/core';

import { WaterfallWsService } from '../../core/services/waterfall-ws.service';
import { WaterfallFrame } from '../../core/models/waterfall-frame.model';

interface ScaleTick {
  frequencyHz: number;
  positionPercent: number;
  major: boolean;
  labeled: boolean;
}

interface HamBand {
  name: string;
  lowerHz: number;
  upperHz: number;
}

interface VisibleHamBand {
  name: string;
  leftPercent: number;
  widthPercent: number;
}

@Component({
  selector: 'app-waterfall-view',
  standalone: true,
  templateUrl: './waterfall-view.html',
})
export class WaterfallView implements AfterViewInit, OnDestroy {
  private readonly waterfallWs = inject(WaterfallWsService);

  readonly centerFrequencyHz = input<number | null>(null);
  readonly currentFrequencyHz = input<number | null>(null);
  readonly sampleRateHz = input<number | null>(null);

  readonly tuneRequested = output<number>();

  readonly canvas = viewChild.required<ElementRef<HTMLCanvasElement>>('canvas');

  readonly paused = signal(false);
  readonly hoverFrequencyHz = signal<number | null>(null);
  readonly pendingTuneFrequencyHz = signal<number | null>(null);
  readonly draggingTune = signal(false);

  readonly snapStepHz = signal<number>(0);

  readonly heatmapGainDb = signal<number>(20);
  readonly heatmapContrast = signal<number>(2.0);
  readonly heatmapFloorOffsetDb = signal<number>(0);
  readonly heatmapPalette = signal<'classic' | 'cool' | 'hot'>('classic');

  readonly snapOptions = [
    { label: 'Off', value: 0 },
    { label: '10 Hz', value: 10 },
    { label: '50 Hz', value: 50 },
    { label: '100 Hz', value: 100 },
    { label: '1 kHz', value: 1_000 },
    { label: '10 kHz', value: 10_000 },
    { label: '100 kHz', value: 100_000 },
  ];

  readonly selectedDisplaySpanHz = signal<number>(0);

  readonly displaySpanOptions = [
    { label: 'Auto', value: 0 },
    { label: '24 kHz', value: 24_000 },
    { label: '48 kHz', value: 48_000 },
    { label: '96 kHz', value: 96_000 },
    { label: '192 kHz', value: 192_000 },
    { label: '384 kHz', value: 384_000 },
  ];

  private context: CanvasRenderingContext2D | null = null;

  readonly hamBands: HamBand[] = [
    { name: '160m', lowerHz: 1_800_000, upperHz: 2_000_000 },
    { name: '80m', lowerHz: 3_500_000, upperHz: 4_000_000 },
    { name: '60m', lowerHz: 5_330_500, upperHz: 5_406_400 },
    { name: '40m', lowerHz: 7_000_000, upperHz: 7_300_000 },
    { name: '30m', lowerHz: 10_100_000, upperHz: 10_150_000 },
    { name: '20m', lowerHz: 14_000_000, upperHz: 14_350_000 },
    { name: '17m', lowerHz: 18_068_000, upperHz: 18_168_000 },
    { name: '15m', lowerHz: 21_000_000, upperHz: 21_450_000 },
    { name: '12m', lowerHz: 24_890_000, upperHz: 24_990_000 },
    { name: '10m', lowerHz: 28_000_000, upperHz: 29_700_000 },
    { name: '6m', lowerHz: 50_000_000, upperHz: 54_000_000 },
  ];

  constructor() {
    effect(() => {
      const frame = this.waterfallWs.latestFrame();

      if (frame && !this.paused()) {
        this.drawFrame(frame);
      }
    });
  }

  ngAfterViewInit(): void {
    const canvas = this.canvas().nativeElement;
    this.context = canvas.getContext('2d', { willReadFrequently: true });

    if (this.context) {
      this.context.imageSmoothingEnabled = false;
    }

    this.resizeCanvas();
    window.addEventListener('resize', this.resizeCanvas);
  }

  ngOnDestroy(): void {
    window.removeEventListener('resize', this.resizeCanvas);
  }

  togglePause(): void {
    this.paused.update((current) => !current);
  }

  clear(): void {
    const canvas = this.canvas().nativeElement;

    if (!this.context) {
      return;
    }

    this.context.clearRect(0, 0, canvas.width, canvas.height);
  }

  setDisplaySpan(value: string): void {
    this.selectedDisplaySpanHz.set(Number(value));
  }

  effectiveSpanHz(): number | null {
    const sourceSpan = this.sampleRateHz();
    const selectedSpan = this.selectedDisplaySpanHz();

    if (!sourceSpan) {
      return null;
    }

    if (!selectedSpan || selectedSpan <= 0) {
      return sourceSpan;
    }

    return Math.min(selectedSpan, sourceSpan);
  }

  setSnapStep(value: string): void {
    this.snapStepHz.set(Number(value));
  }

  setHeatmapGainDb(value: string): void {
    this.heatmapGainDb.set(Number(value));
  }

  setHeatmapContrast(value: string): void {
    this.heatmapContrast.set(Number(value));
  }

  setHeatmapFloorOffsetDb(value: string): void {
    this.heatmapFloorOffsetDb.set(Number(value));
  }

  setHeatmapPalette(value: string): void {
    if (value === 'classic' || value === 'cool' || value === 'hot') {
      this.heatmapPalette.set(value);
    }
  }

  onMouseLeave(): void {
    if (this.draggingTune()) {
      return;
    }

    this.hoverFrequencyHz.set(null);
  }

  onPointerDown(event: PointerEvent): void {
    const canvas = this.canvas().nativeElement;
    canvas.setPointerCapture(event.pointerId);

    const frequencyHz = this.frequencyFromPointerEvent(event);

    this.draggingTune.set(true);
    this.pendingTuneFrequencyHz.set(frequencyHz);
    this.hoverFrequencyHz.set(frequencyHz);
  }

  onPointerMove(event: PointerEvent): void {
    const frequencyHz = this.frequencyFromPointerEvent(event);

    this.hoverFrequencyHz.set(frequencyHz);

    if (this.draggingTune()) {
      this.pendingTuneFrequencyHz.set(frequencyHz);
    }
  }

  onPointerUp(event: PointerEvent): void {
    const canvas = this.canvas().nativeElement;

    if (canvas.hasPointerCapture(event.pointerId)) {
      canvas.releasePointerCapture(event.pointerId);
    }

    const frequencyHz = this.pendingTuneFrequencyHz();

    this.draggingTune.set(false);
    this.pendingTuneFrequencyHz.set(null);

    if (!frequencyHz || frequencyHz <= 0) {
      return;
    }

    this.tuneRequested.emit(Math.round(frequencyHz));
  }

  onPointerCancel(event: PointerEvent): void {
    const canvas = this.canvas().nativeElement;

    if (canvas.hasPointerCapture(event.pointerId)) {
      canvas.releasePointerCapture(event.pointerId);
    }

    this.draggingTune.set(false);
    this.pendingTuneFrequencyHz.set(null);
  }

  formatFrequency(frequencyHz: number | null | undefined): string {
    if (!frequencyHz) {
      return '--.---000';
    }

    return (frequencyHz / 1_000_000).toFixed(6);
  }

  formatTickFrequency(frequencyHz: number | null | undefined): string {
    if (!frequencyHz) {
      return '--.---';
    }

    return (frequencyHz / 1_000_000).toFixed(3);
  }

  scaleTicks(): ScaleTick[] {
    const center = this.centerFrequencyHz();
    const span = this.effectiveSpanHz();

    if (!center || !span) {
      return [];
    }

    const left = center - span / 2;
    const right = center + span / 2;

    const majorStepHz = this.chooseMajorStep(span);
    const minorStepHz = majorStepHz / 4;

    const firstMinor = Math.ceil(left / minorStepHz) * minorStepHz;
    const ticks: ScaleTick[] = [];

    for (let frequencyHz = firstMinor; frequencyHz <= right; frequencyHz += minorStepHz) {
      const isMajor = frequencyHz % majorStepHz === 0;
      const isHalfMajor = frequencyHz % (majorStepHz / 2) === 0;

      ticks.push({
        frequencyHz,
        positionPercent: ((frequencyHz - left) / span) * 100,
        major: isMajor,
        labeled: isMajor || isHalfMajor,
      });
    }

    return ticks;
  }

  previewFrequencyHz(): number | null {
    return this.pendingTuneFrequencyHz() ?? this.currentFrequencyHz();
  }

  previewFrequencyPositionPercent(): number {
    const center = this.centerFrequencyHz();
    const preview = this.previewFrequencyHz();
    const span = this.effectiveSpanHz();

    if (!center || !preview || !span) {
      return 50;
    }

    const left = center - span / 2;
    const position = ((preview - left) / span) * 100;

    return Math.max(0, Math.min(100, position));
  }

  showPreviewFrequencyMarker(): boolean {
    if (this.draggingTune()) {
      return true;
    }

    return this.showSeparateCurrentFrequencyLabel();
  }

  showSeparateCurrentFrequencyLabel(): boolean {
    const center = this.centerFrequencyHz();
    const current = this.currentFrequencyHz();
    const span = this.effectiveSpanHz();

    if (!center || !current || !span) {
      return false;
    }

    return Math.abs(current - center) > span * 0.02;
  }

  centerLabel(): string {
    const center = this.centerFrequencyHz();
    const current = this.currentFrequencyHz();

    if (!center) {
      return 'Center --.---000';
    }

    if (!this.showSeparateCurrentFrequencyLabel() && current && !this.draggingTune()) {
      return `Center/VFO ${this.formatFrequency(center)}`;
    }

    return `Center ${this.formatFrequency(center)}`;
  }

  private readonly resizeCanvas = (): void => {
    const canvas = this.canvas().nativeElement;
    const parent = canvas.parentElement;

    if (!parent) {
      return;
    }

    const cssWidth = parent.clientWidth;
    const cssHeight = 320;
    const pixelRatio = window.devicePixelRatio || 1;

    canvas.width = Math.floor(cssWidth * pixelRatio);
    canvas.height = Math.floor(cssHeight * pixelRatio);

    canvas.style.width = `${cssWidth}px`;
    canvas.style.height = `${cssHeight}px`;

    this.context = canvas.getContext('2d', { willReadFrequently: true });

    if (this.context) {
      this.context.imageSmoothingEnabled = false;
    }
  };

  private frequencyFromPointerEvent(event: PointerEvent): number {
    const canvas = this.canvas().nativeElement;
    const rect = canvas.getBoundingClientRect();

    const center = this.centerFrequencyHz();
    const span = this.effectiveSpanHz();

    if (!center || !span || rect.width <= 0) {
      return 0;
    }

    const x = Math.max(0, Math.min(rect.width, event.clientX - rect.left));
    const ratio = x / rect.width;
    const offsetHz = ratio * span - span / 2;
    const rawFrequencyHz = center + offsetHz;

    return this.applySnap(rawFrequencyHz);
  }

  private applySnap(frequencyHz: number): number {
    const stepHz = this.snapStepHz();

    if (!stepHz || stepHz <= 0) {
      return frequencyHz;
    }

    return Math.round(frequencyHz / stepHz) * stepHz;
  }

  visibleHamBands(): VisibleHamBand[] {
    const center = this.centerFrequencyHz();
    const span = this.effectiveSpanHz();

    if (!center || !span) {
      return [];
    }

    const visibleLowerHz = center - span / 2;
    const visibleUpperHz = center + span / 2;

    return this.hamBands
      .map((band) => {
        const lowerHz = Math.max(band.lowerHz, visibleLowerHz);
        const upperHz = Math.min(band.upperHz, visibleUpperHz);

        if (upperHz <= lowerHz) {
          return null;
        }

        const leftPercent = ((lowerHz - visibleLowerHz) / span) * 100;
        const widthPercent = ((upperHz - lowerHz) / span) * 100;

        return {
          name: band.name,
          leftPercent: Math.max(0, Math.min(100, leftPercent)),
          widthPercent: Math.max(0, Math.min(100, widthPercent)),
        };
      })
      .filter((band): band is VisibleHamBand => band !== null);
  }

  private drawFrame(frame: WaterfallFrame): void {
    const canvas = this.canvas().nativeElement;

    if (!this.context || canvas.width <= 0 || canvas.height <= 0) {
      return;
    }

    const existing = this.context.getImageData(0, 0, canvas.width, canvas.height - 1);
    this.context.putImageData(existing, 0, 1);

    const row = this.context.createImageData(canvas.width, 1);

    const sourceSpan = frame.sample_rate_hz;
    const displaySpan = this.effectiveSpanHz() ?? sourceSpan;
    const visibleRatio = Math.min(1, displaySpan / sourceSpan);
    const visibleBinCount = Math.max(1, Math.floor(frame.bins.length * visibleRatio));
    const firstVisibleBin = Math.floor((frame.bins.length - visibleBinCount) / 2);

    for (let x = 0; x < canvas.width; x++) {
      const binIndex = firstVisibleBin + Math.floor((x / canvas.width) * visibleBinCount);
      const db = frame.bins[binIndex] ?? frame.min_db;

      const adjustedDb = db + this.heatmapGainDb();
      const adjustedMinDb = frame.min_db + this.heatmapFloorOffsetDb();

      const intensity = this.sharpenIntensity(
        this.normalizeDb(adjustedDb, adjustedMinDb, frame.max_db),
      );

      const [r, g, b] = this.colorMap(intensity);

      const offset = x * 4;
      row.data[offset] = r;
      row.data[offset + 1] = g;
      row.data[offset + 2] = b;
      row.data[offset + 3] = 255;
    }

    this.context.putImageData(row, 0, 0);
  }

  private sharpenIntensity(value: number): number {
    const contrast = this.heatmapContrast();
    const adjusted = Math.pow(value, contrast);

    return Math.max(0, Math.min(1, adjusted));
  }

  private chooseMajorStep(spanHz: number): number {
    if (spanHz <= 48_000) {
      return 10_000;
    }

    if (spanHz <= 96_000) {
      return 20_000;
    }

    if (spanHz <= 192_000) {
      return 40_000;
    }

    if (spanHz <= 384_000) {
      return 50_000;
    }

    return 100_000;
  }

  private normalizeDb(value: number, minDb: number, maxDb: number): number {
    const normalized = (value - minDb) / (maxDb - minDb);
    return Math.max(0, Math.min(1, normalized));
  }

  private colorMap(value: number): [number, number, number] {
    switch (this.heatmapPalette()) {
      case 'cool':
        return this.coolColorMap(value);

      case 'hot':
        return this.hotColorMap(value);

      case 'classic':
      default:
        return this.classicColorMap(value);
    }
  }

  private classicColorMap(value: number): [number, number, number] {
    if (value < 0.18) {
      return [0, 10, 35];
    }

    if (value < 0.35) {
      const t = (value - 0.18) / 0.17;
      return [0, Math.floor(30 + t * 90), Math.floor(90 + t * 120)];
    }

    if (value < 0.58) {
      const t = (value - 0.35) / 0.23;
      return [0, Math.floor(120 + t * 120), Math.floor(210 - t * 120)];
    }

    if (value < 0.78) {
      const t = (value - 0.58) / 0.20;
      return [Math.floor(60 + t * 195), Math.floor(220 - t * 80), 35];
    }

    const t = (value - 0.78) / 0.22;
    return [255, Math.floor(140 + t * 115), Math.floor(40 + t * 160)];
  }

  private coolColorMap(value: number): [number, number, number] {
    if (value < 0.20) {
      return [0, 8, 30];
    }

    if (value < 0.50) {
      const t = (value - 0.20) / 0.30;
      return [0, Math.floor(40 + t * 120), Math.floor(120 + t * 135)];
    }

    if (value < 0.80) {
      const t = (value - 0.50) / 0.30;
      return [Math.floor(t * 120), Math.floor(160 + t * 95), 255];
    }

    const t = (value - 0.80) / 0.20;
    return [Math.floor(120 + t * 135), 255, 255];
  }

  private hotColorMap(value: number): [number, number, number] {
    if (value < 0.20) {
      return [10, 0, 0];
    }

    if (value < 0.45) {
      const t = (value - 0.20) / 0.25;
      return [Math.floor(60 + t * 160), Math.floor(t * 60), 0];
    }

    if (value < 0.75) {
      const t = (value - 0.45) / 0.30;
      return [255, Math.floor(60 + t * 160), 0];
    }

    const t = (value - 0.75) / 0.25;
    return [255, Math.floor(220 + t * 35), Math.floor(t * 220)];
  }
}
