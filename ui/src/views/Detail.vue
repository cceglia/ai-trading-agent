<script setup lang="ts">
import { useRoute, useRouter } from "vue-router";
import { useRun } from "../composables/useRun";
import OhlcChart from "../components/OhlcChart.vue";

const route = useRoute();
const router = useRouter();

const symbol = () => (route.params.symbol as string) || "";
const year = () => (route.params.year as string) || "";
const month = () => (route.params.month as string) || "";
const day = () => (route.params.day as string) || "";
const file = () => (route.params.file as string) || "";

const { result, loading, error } = useRun(symbol, year, month, day, file);

function goBack() {
  router.push("/");
}
</script>

<template>
  <div class="min-h-screen bg-terminal-bg">
    <!-- Header -->
    <header class="flex items-center justify-between px-4 py-2 border-b border-terminal-border bg-terminal-surface">
      <div class="flex items-center gap-3">
        <button
          class="text-xs font-mono text-terminal-text-secondary hover:text-terminal-text"
          @click="goBack"
        >
          &larr; Back
        </button>
        <h1 class="text-sm font-sans font-medium text-terminal-text" v-if="result">
          {{ result.symbol }} &mdash; {{ result.run_id }}
        </h1>
      </div>
      <span
        v-if="result"
        class="text-xs font-mono px-2 py-0.5"
        :class="result.status === 'success' ? 'text-terminal-gain' : result.status === 'error' ? 'text-terminal-loss' : 'text-terminal-warning'"
      >
        {{ result.status.toUpperCase() }}
      </span>
    </header>

    <!-- Loading state -->
    <div v-if="loading" class="flex items-center justify-center h-64">
      <span class="text-xs font-mono text-terminal-text-tertiary">Loading...</span>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="flex items-center justify-center h-64">
      <span class="text-xs font-mono text-terminal-loss">{{ error }}</span>
    </div>

    <!-- Content -->
    <div v-else-if="result" class="p-4 space-y-4 max-w-7xl mx-auto">
      <!-- Market Context -->
      <section class="border border-terminal-border bg-terminal-surface p-3">
        <h2 class="text-xs font-sans font-medium text-terminal-text-secondary uppercase tracking-wider mb-2">Market Context</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Bias</span>
            <span class="text-sm font-mono" :class="result.market_context?.bias?.includes('bullish') ? 'text-terminal-gain' : result.market_context?.bias?.includes('bearish') ? 'text-terminal-loss' : 'text-terminal-text'">
              {{ result.market_context?.bias || "N/A" }}
            </span>
          </div>
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Confidence</span>
            <span class="text-sm font-mono text-terminal-text">{{ result.market_context?.confidence ?? "N/A" }}%</span>
          </div>
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Price</span>
            <span class="text-sm font-mono text-terminal-text">{{ result.market_context?.current_price ?? "N/A" }}</span>
          </div>
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Price Time</span>
            <span class="text-sm font-mono text-terminal-text">{{ result.market_context?.current_price_time ?? "N/A" }}</span>
          </div>
        </div>
        <div class="mt-2">
          <span class="text-2xs font-sans text-terminal-text-tertiary block">Reasoning</span>
          <p class="text-xs font-sans text-terminal-text-secondary mt-0.5">{{ result.market_context?.reasoning || "N/A" }}</p>
        </div>
        <div v-if="result.market_context?.key_levels?.length" class="mt-2">
          <span class="text-2xs font-sans text-terminal-text-tertiary block">Key Levels</span>
          <div class="flex flex-wrap gap-1 mt-0.5">
            <span v-for="level in result.market_context.key_levels" :key="level" class="text-xs font-mono text-terminal-warning border border-terminal-border px-1.5 py-0.5">
              {{ level }}
            </span>
          </div>
        </div>
      </section>

      <!-- Decision -->
      <section class="border border-terminal-border bg-terminal-surface p-3" v-if="result.decision">
        <h2 class="text-xs font-sans font-medium text-terminal-text-secondary uppercase tracking-wider mb-2">Decision</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Action</span>
            <span class="text-sm font-mono text-terminal-text">{{ result.decision.action.replace("_", " ") }}</span>
          </div>
          <div v-if="result.decision.entry_price != null">
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Entry</span>
            <span class="text-sm font-mono text-terminal-text">{{ result.decision.entry_price }}</span>
          </div>
          <div v-if="result.decision.stop_loss != null">
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Stop Loss</span>
            <span class="text-sm font-mono text-terminal-loss">{{ result.decision.stop_loss }}</span>
          </div>
          <div v-if="result.decision.take_profit != null">
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Take Profit</span>
            <span class="text-sm font-mono text-terminal-gain">{{ result.decision.take_profit }}</span>
          </div>
          <div v-if="result.decision.risk_reward_ratio != null">
            <span class="text-2xs font-sans text-terminal-text-tertiary block">R/R Ratio</span>
            <span class="text-sm font-mono text-terminal-text">{{ result.decision.risk_reward_ratio }}</span>
          </div>
        </div>
        <div class="mt-2">
          <span class="text-2xs font-sans text-terminal-text-tertiary block">Reasoning</span>
          <p class="text-xs font-sans text-terminal-text-secondary mt-0.5">{{ result.decision.reasoning }}</p>
        </div>
      </section>

      <!-- Review -->
      <section class="border border-terminal-border bg-terminal-surface p-3" v-if="result.review">
        <h2 class="text-xs font-sans font-medium text-terminal-text-secondary uppercase tracking-wider mb-2">Review</h2>
        <div class="flex items-center gap-2 mb-2">
          <span :class="['text-xs font-mono', result.review.approved ? 'text-terminal-gain' : 'text-terminal-loss']">
            {{ result.review.approved ? "APPROVED" : "REJECTED" }}
          </span>
          <span v-if="result.review.risk_management_ok === false" class="text-xs font-mono text-terminal-warning">&#9888; Risk</span>
          <span v-if="result.review.htf_alignment_ok === false" class="text-xs font-mono text-terminal-warning">&#9888; HTF</span>
          <span v-if="result.review.calendar_clear === false" class="text-xs font-mono text-terminal-warning">&#9888; Calendar</span>
        </div>
        <div v-if="result.review.concerns?.length">
          <span class="text-2xs font-sans text-terminal-text-tertiary block">Concerns</span>
          <ul class="mt-0.5 space-y-0.5">
            <li v-for="(c, i) in result.review.concerns" :key="i" class="text-xs font-mono text-terminal-warning">&bull; {{ c }}</li>
          </ul>
        </div>
      </section>

      <!-- OHLC Charts -->
      <section>
        <h2 class="text-xs font-sans font-medium text-terminal-text-secondary uppercase tracking-wider mb-2">Price Charts</h2>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-2">
          <div v-for="tf in (['D1', 'H4', 'H1'] as const)" :key="tf">
            <OhlcChart
              :data="result.ohlc[tf] || []"
              :overlay="result.sl_tp_overlay"
              :timeframe="tf"
            />
          </div>
        </div>
      </section>

      <!-- Errors -->
      <section v-if="result.errors?.length" class="border border-terminal-border bg-terminal-surface p-3">
        <h2 class="text-xs font-sans font-medium text-terminal-loss uppercase tracking-wider mb-2">Errors</h2>
        <ul class="space-y-0.5">
          <li v-for="(err, i) in result.errors" :key="i" class="text-xs font-mono text-terminal-text-secondary">&bull; {{ err }}</li>
        </ul>
      </section>
      <div v-if="result.fatal_error" class="border border-terminal-loss bg-terminal-surface p-3">
        <span class="text-xs font-mono text-terminal-loss">Fatal: {{ result.fatal_error }}</span>
      </div>
    </div>
  </div>
</template>
