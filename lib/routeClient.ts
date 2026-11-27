/**
 * Route requests to the backend (no app imports besides types, so it is testable with `node --test` against a real HTTP server).
 *
 * Behaviour that matters to the UI:
 *  - A request cancelled by the CALLER (a newer tap/search superseded it) returns { aborted: true } and NO error message, so the
 *    screen can ignore it instead of showing "failed" and wiping the route.
 *  - A network failure ("Failed to fetch") is retried twice (after 0.8 s and 1.6 s): the first request after the phone wakes or the
 *    app starts often fails while the network settles.
 *  - A server error, a slow server and an unreachable server each give a different, readable message.
 */
import type { RouteMode, RouteResponse, Point } from './types';

export interface RouteClientOptions {
  fetchImpl: typeof fetch;
  baseUrl: string;
  timeoutMs?: number;
  /** delays before retry 1 and retry 2; tests pass small values */
  retryDelaysMs?: number[];
}

export async function requestRoute(
  opts: RouteClientOptions,
  mode: RouteMode,
  from: Point,
  to: Point,
  signal?: AbortSignal
): Promise<RouteResponse> {
  const timeoutMs = opts.timeoutMs ?? 90000;
  const delays = opts.retryDelaysMs ?? [800, 1600];
  const endpoint = mode === 'dynamic' ? '/dynamic-route' : '/route';
  const params = new URLSearchParams({
    from_lat: String(from.lat),
    from_lng: String(from.lng),
    to_lat: String(to.lat),
    to_lng: String(to.lng),
  });
  const url = `${opts.baseUrl}${endpoint}?${params.toString()}`;

  const cancelled = (): RouteResponse => ({ status: 'error', aborted: true, message: 'Request cancelled' });
  if (signal?.aborted) return cancelled();

  // one controller for both reasons to stop: the caller's signal and our own timeout
  const controller = new AbortController();
  let timedOut = false;
  const onCallerAbort = () => controller.abort();
  signal?.addEventListener('abort', onCallerAbort);
  const timer = setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, timeoutMs);

  try {
    let response: Response | null = null;
    for (let attempt = 0; ; attempt++) {
      try {
        response = await opts.fetchImpl(url, { signal: controller.signal });
        break;
      } catch (err: any) {
        if (signal?.aborted) return cancelled();
        if (timedOut) {
          return { status: 'error', message: 'The routing server took too long to answer. Try again.' };
        }
        if (attempt >= delays.length) {
          return {
            status: 'error',
            message: `Can't reach the routing server (${opts.baseUrl}). Check that it is running and your network works.`,
          };
        }
        await new Promise((resolve) => setTimeout(resolve, delays[attempt]));
        if (signal?.aborted) return cancelled();
      }
    }

    let data: any = null;
    try {
      data = await response.json();
    } catch {
      // the download itself can be cancelled or can stall: that is not an unreadable answer
      if (signal?.aborted) return cancelled();
      if (timedOut) {
        return { status: 'error', message: 'The routing server took too long to answer. Try again.' };
      }
      data = null;
    }

    if (!response.ok) {
      const detail = [data?.message, data?.detail].find((d) => typeof d === 'string' && d) || '';
      return {
        status: 'error',
        message: detail ? String(detail) : `The routing server returned an error (${response.status}).`,
      };
    }
    if (!data || typeof data !== 'object') {
      return { status: 'error', message: 'The routing server sent an unreadable answer.' };
    }
    if (data.status === 'error' && !data.message) {
      return { status: 'error', message: 'No route could be calculated between these places.' };
    }
    return data as RouteResponse;
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener('abort', onCallerAbort);
  }
}
