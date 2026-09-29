import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiFetch, parseJsonOrThrow } from './api';

afterEach(() => {
  vi.restoreAllMocks();
  vi.useRealTimers();
});

describe('apiFetch', () => {
  it('turns a network failure into an actionable message', async () => {
    // A bare `TypeError: Failed to fetch` used to reach the user verbatim.
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new TypeError('Failed to fetch'));

    await expect(apiFetch('/api/dashboard')).rejects.toThrow('Cannot reach the backend');
  });

  it('gives up on a read that never answers', async () => {
    vi.useFakeTimers();
    vi.spyOn(globalThis, 'fetch').mockImplementation(
      (_input, init) =>
        new Promise((_resolve, reject) => {
          init?.signal?.addEventListener('abort', () =>
            reject(new DOMException('The operation was aborted.', 'AbortError')),
          );
        }),
    );

    const pending = apiFetch('/api/services');
    const assertion = expect(pending).rejects.toThrow('did not answer within 20 seconds');
    await vi.advanceTimersByTimeAsync(20_000);
    await assertion;
  });

  it('does not put a timeout on a scan', async () => {
    // A scan is bounded on the server; aborting the request would hide its
    // result without stopping it.
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('{}'));

    await apiFetch('/api/scan', { method: 'POST' });

    expect(fetchSpy.mock.calls[0][1]?.signal).toBeUndefined();
  });
});

describe('parseJsonOrThrow', () => {
  it("surfaces the backend's own explanation", async () => {
    const response = new Response(JSON.stringify({ detail: 'A registry scan is already running.' }), {
      status: 409,
    });

    await expect(parseJsonOrThrow(response)).rejects.toThrow('A registry scan is already running.');
  });

  it('falls back to the status code when the body is not JSON', async () => {
    const response = new Response('<html>bad gateway</html>', { status: 502 });

    await expect(parseJsonOrThrow(response)).rejects.toThrow('status 502');
  });

  it('returns the parsed body on success', async () => {
    const response = new Response(JSON.stringify({ services_count: 3 }), { status: 200 });

    await expect(parseJsonOrThrow<{ services_count: number }>(response)).resolves.toEqual({
      services_count: 3,
    });
  });
});
