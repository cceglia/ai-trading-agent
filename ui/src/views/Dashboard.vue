<script setup lang="ts">
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useRuns } from "../composables/useRuns";
import { startRun } from "../lib/api";
import RunCard from "../components/RunCard.vue";
import SymbolSidebar from "../components/SymbolSidebar.vue";
import TimelineBar from "../components/TimelineBar.vue";
import type { RunSummary } from "../types";

const router = useRouter();
const { runs, loading: runsLoading, error: runsError, reload } = useRuns();

const selectedSymbol = ref<string | null>(null);
const runNowLoading = ref(false);
const runNowError = ref<string | null>(null);

// Derive unique symbols from runs
const symbols = computed(() => {
  const symSet = new Set(runs.value.map((r) => r.symbol));
  return Array.from(symSet).sort();
});

// Derive unique dates from runs
const dates = computed(() => {
  const dateSet = new Set(runs.value.map((r) => r.date));
  return Array.from(dateSet).sort().reverse();
});

const selectedDate = ref<string | null>(null);

// Filter runs by selected symbol and date
const filteredRuns = computed(() => {
  let result = runs.value;
  if (selectedSymbol.value) {
    result = result.filter((r) => r.symbol === selectedSymbol.value);
  }
  if (selectedDate.value) {
    result = result.filter((r) => r.date === selectedDate.value);
  }
  return result;
});

async function handleRunNow() {
  runNowLoading.value = true;
  runNowError.value = null;
  try {
    const symbolsToRun = selectedSymbol.value ? [selectedSymbol.value] : ["XAUUSD"];
    await startRun({ symbols: symbolsToRun });
    await reload();
  } catch (e: any) {
    runNowError.value = e?.message || "Run failed";
  } finally {
    runNowLoading.value = false;
  }
}

function selectRun(run: RunSummary) {
  const [year, month, day] = run.date.split("-");
  router.push(`/run/${run.symbol}/${year}/${month}/${day}/result-${run.time}`);
}

function selectSymbol(symbol: string | null) {
  selectedSymbol.value = symbol;
}

function selectDate(date: string | null) {
  selectedDate.value = date;
}

const runCountBySymbol = computed(() => {
  const counts: Record<string, number> = {};
  for (const r of runs.value) {
    counts[r.symbol] = (counts[r.symbol] || 0) + 1;
  }
  return counts;
});
</script>

<template>
  <div class="h-screen flex flex-col bg-terminal-bg">
    <!-- Top bar -->
    <header class="flex items-center justify-between px-3 py-2 border-b border-terminal-border bg-terminal-surface">
      <h1 class="text-xs font-sans font-medium text-terminal-text uppercase tracking-wider">Analysis Terminal</h1>
      <div class="flex items-center gap-2">
        <!-- Symbol dropdown filter -->
        <select
          v-model="selectedSymbol"
          class="bg-terminal-bg border border-terminal-border text-terminal-text-secondary text-xs font-mono px-2 py-1"
        >
          <option :value="null">All Symbols</option>
          <option v-for="s in symbols" :key="s" :value="s">{{ s }}</option>
        </select>
        <!-- Run Now button -->
        <button
          class="px-3 py-1 text-xs font-sans font-medium bg-terminal-gain text-terminal-bg hover:opacity-90 disabled:opacity-50"
          :disabled="runNowLoading"
          @click="handleRunNow"
        >
          {{ runNowLoading ? "Running..." : "Run Now" }}
        </button>
      </div>
    </header>

    <!-- Main content: sidebar + timeline + cards -->
    <div class="flex-1 flex overflow-hidden">
      <!-- Symbol Sidebar -->
      <SymbolSidebar
        :symbols="symbols"
        :selected="selectedSymbol"
        :run-counts="runCountBySymbol"
        :total-runs="runs.length"
        @select="selectSymbol"
      />

      <!-- Right side: timeline + cards -->
      <div class="flex-1 flex flex-col overflow-hidden">
        <!-- Timeline bar -->
        <TimelineBar
          :dates="dates"
          :selected="selectedDate"
          @select="selectDate"
        />

        <!-- Run cards grid -->
        <div class="flex-1 overflow-y-auto p-3">
          <!-- Loading state -->
          <div v-if="runsLoading" class="flex items-center justify-center h-full">
            <span class="text-xs font-mono text-terminal-text-tertiary">Loading...</span>
          </div>

          <!-- Error state -->
          <div v-else-if="runsError" class="flex items-center justify-center h-full">
            <span class="text-xs font-mono text-terminal-loss">{{ runsError }}</span>
          </div>

          <!-- Empty state -->
          <div v-else-if="filteredRuns.length === 0" class="flex items-center justify-center h-full">
            <span class="text-xs font-mono text-terminal-text-tertiary">No runs found. Click "Run Now" to start an analysis.</span>
          </div>

          <!-- Run cards -->
          <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2">
            <RunCard
              v-for="(run, index) in filteredRuns"
              :key="`${run.symbol}-${run.date}-${run.time}-${index}`"
              :run="run"
              @select="selectRun"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Run Now loading overlay -->
    <div
      v-if="runNowLoading"
      class="fixed inset-0 bg-terminal-bg/80 flex items-center justify-center z-50"
    >
      <div class="text-center">
        <div class="text-terminal-gain text-2xl mb-2 font-mono">&#x27F3;</div>
        <span class="text-xs font-mono text-terminal-text-secondary">Running analysis...</span>
      </div>
    </div>

    <!-- Run Now error toast -->
    <div
      v-if="runNowError"
      class="fixed bottom-4 right-4 bg-terminal-loss text-terminal-text px-4 py-2 text-xs font-mono z-50"
    >
      {{ runNowError }}
      <button class="ml-2 text-terminal-text/70" @click="runNowError = null">&times;</button>
    </div>
  </div>
</template>
