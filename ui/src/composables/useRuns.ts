import { ref, onMounted } from "vue";
import { fetchRuns } from "../lib/api";
import type { RunSummary } from "../types";

export function useRuns() {
  const runs = ref<RunSummary[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function load(params?: { symbol?: string; from?: string; to?: string }) {
    loading.value = true;
    error.value = null;
    try {
      runs.value = await fetchRuns(params);
    } catch (e: any) {
      error.value = e?.message || "Failed to load runs";
    } finally {
      loading.value = false;
    }
  }

  onMounted(() => load());

  return { runs, loading, error, reload: load };
}
