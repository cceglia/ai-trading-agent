import { ref, watch } from "vue";
import { fetchRunResult } from "../lib/api";
import { formatApiError } from "../lib/errors";
import type { FullResult } from "../types";

export function useRun(
  symbol: () => string,
  year: () => string,
  month: () => string,
  day: () => string,
  file: () => string
) {
  const result = ref<FullResult | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function load() {
    const s = symbol();
    const y = year();
    const m = month();
    const d = day();
    const f = file();

    if (!s || !y || !m || !d || !f) return;

    loading.value = true;
    error.value = null;
    try {
      result.value = await fetchRunResult(s, y, m, d, f);
    } catch (e: unknown) {
      error.value = formatApiError(e, "Failed to load run result");
    } finally {
      loading.value = false;
    }
  }

  // Watch all params and reload when any changes
  watch([symbol, year, month, day, file], load, { immediate: true });

  return { result, loading, error };
}
