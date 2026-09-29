import { describe, expect, it } from 'vitest';
import { visibleCount } from './paging';

describe('visibleCount', () => {
  it('shows one page to start with', () => {
    expect(visibleCount(1_000, 1, 100)).toBe(100);
  });

  it('grows by a page each time', () => {
    expect(visibleCount(1_000, 3, 100)).toBe(300);
  });

  it('never exceeds the list', () => {
    expect(visibleCount(250, 5, 100)).toBe(250);
  });

  it('shows everything when the list is shorter than a page', () => {
    expect(visibleCount(7, 1, 100)).toBe(7);
  });

  it('treats a nonsensical page count as the first page', () => {
    expect(visibleCount(1_000, 0, 100)).toBe(100);
  });
});
