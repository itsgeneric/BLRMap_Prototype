/**
 * "Latest request wins" (pure, testable with `node --test`).
 * Every new request takes a token; when an answer arrives only the holder of the CURRENT token may touch the screen. A slow,
 * superseded answer is dropped instead of overwriting or clearing what the newer request produced.
 */
export function createLatest() {
  let current = 0;
  return {
    /** start a new request: returns its token and makes every earlier token stale */
    begin(): number {
      current += 1;
      return current;
    },
    isCurrent(token: number): boolean {
      return token === current;
    },
    /** make every outstanding token stale without starting a request (for example when the route is cleared) */
    invalidate(): void {
      current += 1;
    },
  };
}
