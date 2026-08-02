import { describe, it, expect } from "vitest";
import {
  yearFrom,
  monthFrom,
  dayFrom,
  padMonth,
  padDay,
  uniqueYears,
  uniqueMonths,
  uniqueDays,
  preferredOrFirst,
} from "../dates";

// ---------------------------------------------------------------------------
// Parse helpers
// ---------------------------------------------------------------------------
describe("yearFrom", () => {
  it("extracts the year from YYYY-MM-DD", () => {
    expect(yearFrom("2026-07-30")).toBe("2026");
  });
});

describe("monthFrom", () => {
  it("extracts the month from YYYY-MM-DD", () => {
    expect(monthFrom("2026-07-30")).toBe("07");
  });
});

describe("dayFrom", () => {
  it("extracts the day from YYYY-MM-DD", () => {
    expect(dayFrom("2026-07-30")).toBe("30");
  });
});

// ---------------------------------------------------------------------------
// Zero-padding
// ---------------------------------------------------------------------------
describe("padMonth", () => {
  it("pads single-digit months", () => {
    expect(padMonth(1)).toBe("01");
    expect(padMonth(7)).toBe("07");
  });

  it("does not pad double-digit months", () => {
    expect(padMonth(10)).toBe("10");
    expect(padMonth(12)).toBe("12");
  });
});

describe("padDay", () => {
  it("pads single-digit days", () => {
    expect(padDay(1)).toBe("01");
    expect(padDay(9)).toBe("09");
  });

  it("does not pad double-digit days", () => {
    expect(padDay(10)).toBe("10");
    expect(padDay(31)).toBe("31");
  });
});

// ---------------------------------------------------------------------------
// uniqueYears
// ---------------------------------------------------------------------------
describe("uniqueYears", () => {
  it("returns unique years sorted descending", () => {
    const dates = ["2025-03-15", "2026-07-30", "2025-01-01", "2024-12-25"];
    expect(uniqueYears(dates)).toEqual(["2026", "2025", "2024"]);
  });

  it("deduplicates repeated years", () => {
    const dates = ["2026-01-01", "2026-06-15", "2026-12-31"];
    expect(uniqueYears(dates)).toEqual(["2026"]);
  });

  it("returns an empty array for empty input", () => {
    expect(uniqueYears([])).toEqual([]);
  });
});

// ---------------------------------------------------------------------------
// uniqueMonths
// ---------------------------------------------------------------------------
describe("uniqueMonths", () => {
  const dates = ["2025-01-10", "2025-03-20", "2025-01-15", "2026-07-30", "2026-08-01"];

  it("returns all unique months when year is null", () => {
    expect(uniqueMonths(dates, null)).toEqual(["01", "03", "07", "08"]);
  });

  it("filters by year and returns unique months ascending", () => {
    expect(uniqueMonths(dates, "2025")).toEqual(["01", "03"]);
    expect(uniqueMonths(dates, "2026")).toEqual(["07", "08"]);
  });

  it("returns an empty array when the year has no matches", () => {
    expect(uniqueMonths(dates, "2027")).toEqual([]);
  });

  it("returns an empty array for empty input", () => {
    expect(uniqueMonths([], "2025")).toEqual([]);
  });
});

// ---------------------------------------------------------------------------
// uniqueDays
// ---------------------------------------------------------------------------
describe("uniqueDays", () => {
  const dates = [
    "2025-01-10",
    "2025-01-15",
    "2025-03-20",
    "2026-07-30",
    "2026-07-31",
    "2026-08-01",
  ];

  it("returns all unique days when year and month are null", () => {
    expect(uniqueDays(dates, null, null)).toEqual([
      "01", "10", "15", "20", "30", "31",
    ]);
  });

  it("filters by year only", () => {
    expect(uniqueDays(dates, "2025", null)).toEqual(["10", "15", "20"]);
  });

  it("filters by year and month", () => {
    expect(uniqueDays(dates, "2026", "07")).toEqual(["30", "31"]);
  });

  it("returns days sorted numerically ascending", () => {
    expect(uniqueDays(dates, null, null)).toEqual([
      "01", "10", "15", "20", "30", "31",
    ]);
  });

  it("returns an empty array when nothing matches", () => {
    expect(uniqueDays(dates, "2027", "01")).toEqual([]);
  });
});

// ---------------------------------------------------------------------------
// preferredOrFirst
// ---------------------------------------------------------------------------
describe("preferredOrFirst", () => {
  it("returns preferred when it exists in values", () => {
    expect(preferredOrFirst(["01", "05", "31"], "05")).toBe("05");
  });

  it("returns first value when preferred is absent", () => {
    expect(preferredOrFirst(["01", "05", "31"], "15")).toBe("01");
  });

  it("returns null when values is empty", () => {
    expect(preferredOrFirst([], "05")).toBeNull();
  });

  it("returns the only value when values has one element and preferred matches", () => {
    expect(preferredOrFirst(["07"], "07")).toBe("07");
  });

  it("returns the only value when values has one element and preferred does not match", () => {
    expect(preferredOrFirst(["07"], "08")).toBe("07");
  });
});
