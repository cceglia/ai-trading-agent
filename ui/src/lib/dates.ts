/**
 * Date utility helpers for the trading analysis dashboard.
 *
 * All run dates are guaranteed by the API contract to be canonical
 * YYYY-MM-DD strings.
 */

/** Extract the year portion of a YYYY-MM-DD date string. */
export function yearFrom(d: string): string {
  return d.slice(0, 4);
}

/** Extract the month portion of a YYYY-MM-DD date string. */
export function monthFrom(d: string): string {
  return d.slice(5, 7);
}

/** Extract the day portion of a YYYY-MM-DD date string. */
export function dayFrom(d: string): string {
  return d.slice(8, 10);
}

/** Zero-pad a month number (1-12) to "01"-"12". */
export function padMonth(n: number): string {
  return String(n).padStart(2, "0");
}

/** Zero-pad a day number (1-31) to "01"-"31". */
export function padDay(n: number): string {
  return String(n).padStart(2, "0");
}

/** Unique years from dates, sorted descending. */
export function uniqueYears(dates: string[]): string[] {
  return [...new Set(dates.map(yearFrom))].sort().reverse();
}

/** Unique months from dates, filtered by year when non-null, sorted ascending. */
export function uniqueMonths(dates: string[], year: string | null): string[] {
  const filtered = year ? dates.filter((d) => d.startsWith(year)) : dates;
  return [...new Set(filtered.map(monthFrom))].sort();
}

/** Unique days from dates, filtered by year+month when non-null, sorted ascending. */
export function uniqueDays(
  dates: string[],
  year: string | null,
  month: string | null,
): string[] {
  let filtered = dates;
  if (year) filtered = filtered.filter((d) => d.startsWith(year));
  if (month) filtered = filtered.filter((d) => monthFrom(d) === month);
  return [...new Set(filtered.map(dayFrom))].sort((a, b) => Number(a) - Number(b));
}

/**
 * Return `preferred` if it exists in `values`, otherwise the first value.
 * Returns `null` when `values` is empty.
 */
export function preferredOrFirst(
  values: string[],
  preferred: string,
): string | null {
  return values.includes(preferred) ? preferred : values[0] ?? null;
}
