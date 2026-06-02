import {
  AfterViewInit,
  Component,
  ElementRef,
  effect,
  inject,
  OnDestroy,
  viewChild,
} from '@angular/core';

import { WaterfallWsService } from '../../core/services/waterfall-ws.service';
import { WaterfallFrame } from '../../core/models/waterfall-frame.model';

@Component({
  selector: 'app-waterfall-view',
  standalone: true,
  templateUrl: './waterfall-view.html',
})
export class WaterfallView implements AfterViewInit, OnDestroy {
  private readonly waterfallWs = inject(WaterfallWsService);

  readonly canvas = viewChild.required<ElementRef<HTMLCanvasElement>>('canvas');

  private context: CanvasRenderingContext2D | null = null;
  private imageData: ImageData | null = null;

  constructor() {
    effect(() => {
      const frame = this.waterfallWs.latestFrame();

      if (frame) {
        this.drawFrame(frame);
      }
    });
  }

  ngAfterViewInit(): void {
    const canvas = this.canvas().nativeElement;
    this.context = canvas.getContext('2d', { willReadFrequently: true });

    this.resizeCanvas();
    window.addEventListener('resize', this.resizeCanvas);
  }

  ngOnDestroy(): void {
    window.removeEventListener('resize', this.resizeCanvas);
  }

  private readonly resizeCanvas = (): void => {
    const canvas = this.canvas().nativeElement;
    const parent = canvas.parentElement;

    if (!parent) {
      return;
    }

    canvas.width = parent.clientWidth;
    canvas.height = 280;

    this.context = canvas.getContext('2d', { willReadFrequently: true });
    this.imageData = this.context?.createImageData(canvas.width, canvas.height) ?? null;
  };

  private drawFrame(frame: WaterfallFrame): void {
    const canvas = this.canvas().nativeElement;

    if (!this.context || canvas.width <= 0 || canvas.height <= 0) {
      return;
    }

    const existing = this.context.getImageData(0, 0, canvas.width, canvas.height - 1);
    this.context.putImageData(existing, 0, 1);

    const row = this.context.createImageData(canvas.width, 1);

    for (let x = 0; x < canvas.width; x++) {
      const binIndex = Math.floor((x / canvas.width) * frame.bins.length);
      const db = frame.bins[binIndex] ?? frame.min_db;
      const intensity = this.normalizeDb(db, frame.min_db, frame.max_db);
      const [r, g, b] = this.colorMap(intensity);

      const offset = x * 4;
      row.data[offset] = r;
      row.data[offset + 1] = g;
      row.data[offset + 2] = b;
      row.data[offset + 3] = 255;
    }

    this.context.putImageData(row, 0, 0);
  }

  private normalizeDb(value: number, minDb: number, maxDb: number): number {
    const normalized = (value - minDb) / (maxDb - minDb);
    return Math.max(0, Math.min(1, normalized));
  }

  private colorMap(value: number): [number, number, number] {
    if (value < 0.25) {
      const t = value / 0.25;
      return [0, Math.floor(20 + t * 60), Math.floor(80 + t * 100)];
    }

    if (value < 0.5) {
      const t = (value - 0.25) / 0.25;
      return [0, Math.floor(80 + t * 120), Math.floor(180 - t * 80)];
    }

    if (value < 0.75) {
      const t = (value - 0.5) / 0.25;
      return [Math.floor(t * 255), Math.floor(200 - t * 80), 40];
    }

    const t = (value - 0.75) / 0.25;
    return [255, Math.floor(120 + t * 135), Math.floor(40 + t * 180)];
  }
}
