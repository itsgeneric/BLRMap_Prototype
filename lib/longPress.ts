/**
 * Press-and-hold detection for the map (pure, testable with `node --test`).
 *
 * A long press fires once after `holdMs` if the finger/mouse stayed within `moveTolerancePx` of where it went down and nothing
 * cancelled it (lifting, a drag, a second finger, zooming). A normal tap or a quick drag never fires, so touching the map around
 * can no longer select places by accident.
 */
export interface LongPressOptions<T> {
  holdMs?: number;
  moveTolerancePx?: number;
  onLongPress: (payload: T) => void;
  /** injectable for tests */
  setTimer?: (fn: () => void, ms: number) => unknown;
  clearTimer?: (handle: unknown) => void;
}

export class LongPressDetector<T> {
  private holdMs: number;
  private tolerance: number;
  private onLongPress: (payload: T) => void;
  private setTimer: (fn: () => void, ms: number) => unknown;
  private clearTimer: (handle: unknown) => void;
  private handle: unknown = null;
  private startX = 0;
  private startY = 0;
  private active = false;

  constructor(opts: LongPressOptions<T>) {
    this.holdMs = opts.holdMs ?? 550;
    this.tolerance = opts.moveTolerancePx ?? 12;
    this.onLongPress = opts.onLongPress;
    this.setTimer = opts.setTimer ?? ((fn, ms) => setTimeout(fn, ms));
    this.clearTimer = opts.clearTimer ?? ((h) => clearTimeout(h as ReturnType<typeof setTimeout>));
  }

  /** The finger / mouse went down at screen position (x, y). `payload` is handed to onLongPress if the hold completes. */
  start(x: number, y: number, payload: T): void {
    this.cancel();
    this.active = true;
    this.startX = x;
    this.startY = y;
    this.handle = this.setTimer(() => {
      if (!this.active) return;
      this.active = false;
      this.handle = null;
      this.onLongPress(payload);
    }, this.holdMs);
  }

  /** The pointer moved: drifting further than the tolerance means the user is dragging, not holding. */
  move(x: number, y: number): void {
    if (!this.active) return;
    if (Math.hypot(x - this.startX, y - this.startY) > this.tolerance) this.cancel();
  }

  /** Lifted, dragged, zoomed, or a second finger arrived. */
  cancel(): void {
    this.active = false;
    if (this.handle !== null) {
      this.clearTimer(this.handle);
      this.handle = null;
    }
  }

  end(): void {
    this.cancel();
  }

  isPending(): boolean {
    return this.active;
  }
}
