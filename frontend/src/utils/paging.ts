import { useEffect, useState } from 'react';

export const PAGE_SIZE = 100;

/**
 * How many rows to render for `total` items after `pagesShown` pages.
 *
 * A log scan over a large estate can produce thousands of error groups, and
 * rendering every one at once made the table sluggish to scroll and slow to
 * appear. The server sorts by occurrence count, so the first page is always
 * the part that matters most.
 */
export function visibleCount(total: number, pagesShown: number, pageSize = PAGE_SIZE): number {
  return Math.min(total, Math.max(1, pagesShown) * pageSize);
}

/** Incremental "show more" paging over a list, reset whenever the list changes. */
export function usePaged<T>(items: T[], pageSize = PAGE_SIZE) {
  const [pages, setPages] = useState(1);

  // A new scan or a new filter should start from the top again, not keep
  // however far the previous list had been expanded.
  useEffect(() => {
    setPages(1);
  }, [items]);

  const shown = visibleCount(items.length, pages, pageSize);
  return {
    visible: items.slice(0, shown),
    shown,
    total: items.length,
    hasMore: shown < items.length,
    showMore: () => setPages((p) => p + 1),
  };
}
