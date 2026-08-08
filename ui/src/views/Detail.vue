<script setup lang="ts">
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useRun } from "../composables/useRun";
import OhlcChart from "../components/OhlcChart.vue";
import {
  actionLabel,
  entryPlanOverlay,
  formatConfidencePct,
  hasCompleteDeterministicSetup,
  isActionableRun,
  isLegacyRun,
  isOperationalRun,
} from "../deterministicSetup";

const route = useRoute();
const router = useRouter();

const symbol = () => (route.params.symbol as string) || "";
const year = () => (route.params.year as string) || "";
const month = () => (route.params.month as string) || "";
const day = () => (route.params.day as string) || "";
const file = () => (route.params.file as string) || "";

const { result, loading, error } = useRun(symbol, year, month, day, file);

const facts = computed(() => result.value?.deterministic_facts ?? null);
const legacy = computed(() => isLegacyRun(result.value));
const operational = computed(() => isOperationalRun(result.value));
const actionable = computed(() => isActionableRun(result.value));
const planComplete = computed(() => hasCompleteDeterministicSetup(result.value));
const overlay = computed(() => entryPlanOverlay(result.value));

const statusLabel = computed(() => result.value?.status.toUpperCase() ?? "");
const statusClass = computed(() => {
  switch (result.value?.status) {
    case "success":
      return "text-terminal-gain";
    case "degraded":
    case "partial":
      return "text-terminal-warning";
    case "error":
      return "text-terminal-loss";
    default:
      return "text-terminal-text-tertiary";
  }
});

const validationClass = computed(() =>
  facts.value?.validation_status === "VALID"
    ? "text-terminal-gain"
    : "text-terminal-loss"
);

function fmt(value: number | null | undefined): string {
  return value == null ? "N/A" : String(value);
}

function blockerLabel(blocker: Record<string, unknown>): string {
  const code = blocker.code ?? blocker.type;
  const reason = blocker.reason;
  if (typeof code === "string" && typeof reason === "string") {
    return `${code}: ${reason}`;
  }
  if (typeof code === "string") return code;
  return JSON.stringify(blocker);
}

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
      <div class="flex items-center gap-2" v-if="result">
        <span
          class="text-xs font-mono px-2 py-0.5"
          :class="legacy ? 'text-terminal-text-tertiary border border-terminal-border' : 'text-terminal-gain border border-terminal-border'"
        >
          {{ legacy ? "LEGACY" : "V2" }}
        </span>
        <span class="text-xs font-mono px-2 py-0.5" :class="statusClass">
          {{ statusLabel }}
        </span>
      </div>
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
      <!-- Legacy callout -->
      <section
        v-if="legacy"
        class="border border-terminal-border bg-terminal-surface p-3"
      >
        <h2 class="text-xs font-sans font-medium text-terminal-warning uppercase tracking-wider mb-1">Legacy result</h2>
        <p class="text-xs font-sans text-terminal-text-secondary">
          Legacy result &mdash; no deterministic v2 facts available. Displayed for
          reference only; not actionable.
        </p>
      </section>

      <!-- Deterministic Facts (authoritative) -->
      <section class="border border-terminal-border bg-terminal-surface p-3">
        <h2 class="text-xs font-sans font-medium text-terminal-text-secondary uppercase tracking-wider mb-2">Deterministic Facts</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Bias</span>
            <span class="text-sm font-mono text-terminal-text">{{ facts?.bias ?? "N/A" }}</span>
          </div>
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Confidence</span>
            <span class="text-sm font-mono text-terminal-text">
              {{ formatConfidencePct(facts?.confidence ?? null, legacy) }}
            </span>
          </div>
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Validation</span>
            <span :class="['text-sm font-mono', validationClass]">{{ facts?.validation_status ?? "UNKNOWN" }}</span>
          </div>
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Operational</span>
            <span :class="['text-sm font-mono', operational ? 'text-terminal-gain' : 'text-terminal-text-tertiary']">
              {{ operational ? "OPERATIONAL" : "NON-OPERATIONAL" }}
            </span>
          </div>
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Setup Status</span>
            <span class="text-sm font-mono text-terminal-text">{{ facts?.setup_status ?? "UNKNOWN" }}</span>
          </div>
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Direction</span>
            <span class="text-sm font-mono text-terminal-text">{{ facts?.direction ?? "NONE" }}</span>
          </div>
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Trade Direction</span>
            <span class="text-sm font-mono text-terminal-text">{{ facts?.trade_direction ?? "NEUTRAL" }}</span>
          </div>
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Setup Grade</span>
            <span class="text-sm font-mono text-terminal-text">{{ facts?.setup_grade ?? "N/A" }}</span>
          </div>
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Classification</span>
            <span class="text-sm font-mono text-terminal-text">{{ facts?.setup_classification_status ?? "N/A" }}</span>
          </div>
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Lifecycle</span>
            <span class="text-sm font-mono text-terminal-text">{{ facts?.setup_lifecycle_status ?? "N/A" }}</span>
          </div>
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">R/R</span>
            <span class="text-sm font-mono text-terminal-text">
              {{ facts ? fmt(facts.rr.calculated_rr) : "N/A" }}
              <span v-if="facts" class="text-terminal-text-tertiary">
                (min {{ facts.rr.minimum_required_rr }})
              </span>
            </span>
          </div>
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">R/R Pass</span>
            <span :class="['text-sm font-mono', facts?.rr.rr_pass ? 'text-terminal-gain' : 'text-terminal-loss']">
              {{ facts?.rr.rr_pass ? "PASS" : "FAIL" }}
            </span>
          </div>
        </div>
        <div v-if="facts?.validation_errors?.length" class="mt-2">
          <span class="text-2xs font-sans text-terminal-text-tertiary block">Validation Errors</span>
          <ul class="mt-0.5 space-y-0.5">
            <li v-for="(err, i) in facts.validation_errors" :key="i" class="text-xs font-mono text-terminal-warning">&bull; {{ err }}</li>
          </ul>
        </div>
      </section>

      <!-- Decision & Entry Plan (authoritative) -->
      <section class="border border-terminal-border bg-terminal-surface p-3">
        <h2 class="text-xs font-sans font-medium text-terminal-text-secondary uppercase tracking-wider mb-2">Decision &amp; Entry Plan</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Action</span>
            <span :class="['text-sm font-mono', actionable ? 'text-terminal-gain' : 'text-terminal-text']">
              {{ result ? actionLabel(result.decision.action) : "N/A" }}
            </span>
          </div>
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Order Type</span>
            <span class="text-sm font-mono text-terminal-text">{{ facts?.entry_plan.entry_type ?? "N/A" }}</span>
          </div>
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Entry</span>
            <span class="text-sm font-mono text-terminal-text">{{ fmt(facts?.entry_plan.entry_price ?? null) }}</span>
          </div>
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Stop Loss</span>
            <span class="text-sm font-mono text-terminal-loss">{{ fmt(facts?.entry_plan.invalidation_price ?? null) }}</span>
          </div>
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Take Profit</span>
            <span class="text-sm font-mono text-terminal-gain">{{ fmt(facts?.entry_plan.target_price ?? null) }}</span>
          </div>
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Est. R/R</span>
            <span class="text-sm font-mono text-terminal-text">{{ fmt(facts?.entry_plan.estimated_reward_risk ?? null) }}</span>
          </div>
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Execution Status</span>
            <span class="text-sm font-mono text-terminal-text">{{ facts?.policy.execution_status ?? "N/A" }}</span>
          </div>
          <div>
            <span class="text-2xs font-sans text-terminal-text-tertiary block">Plan</span>
            <span :class="['text-sm font-mono', planComplete ? 'text-terminal-gain' : 'text-terminal-warning']">
              {{ planComplete ? "COMPLETE" : "INCOMPLETE" }}
            </span>
          </div>
        </div>
        <div v-if="facts?.policy.blockers?.length" class="mt-2">
          <span class="text-2xs font-sans text-terminal-text-tertiary block">Policy Blockers</span>
          <ul class="mt-0.5 space-y-0.5">
            <li v-for="(blocker, i) in facts.policy.blockers" :key="i" class="text-xs font-mono text-terminal-warning">&bull; {{ blockerLabel(blocker) }}</li>
          </ul>
        </div>
        <div v-if="facts?.policy.reason_codes?.length" class="mt-2">
          <span class="text-2xs font-sans text-terminal-text-tertiary block">Reason Codes</span>
          <div class="flex flex-wrap gap-1 mt-0.5">
            <span v-for="code in facts.policy.reason_codes" :key="code" class="text-xs font-mono text-terminal-warning border border-terminal-border px-1.5 py-0.5">
              {{ code }}
            </span>
          </div>
        </div>
        <p class="mt-3 text-xs font-mono text-terminal-text-tertiary">
          Advisory only &mdash; the engine never authorises execution
          (entry_authorized is always false).
        </p>
      </section>

      <!-- Synthesis (presentation-only) -->
      <section class="border border-terminal-border bg-terminal-surface p-3">
        <h2 class="text-xs font-sans font-medium text-terminal-text-secondary uppercase tracking-wider mb-2">Synthesis</h2>
        <div class="flex items-center gap-2 mb-2">
          <span
            :class="['text-xs font-mono px-2 py-0.5 border border-terminal-border', result.synthesis.status === 'SUCCESS' ? 'text-terminal-gain' : result.synthesis.status === 'FAILED' ? 'text-terminal-loss' : 'text-terminal-text-tertiary']"
          >
            {{ result.synthesis.status }}
          </span>
          <span class="text-2xs font-sans text-terminal-text-tertiary">presentation-only</span>
        </div>
        <div>
          <span class="text-2xs font-sans text-terminal-text-tertiary block">Explanation</span>
          <p class="text-xs font-sans text-terminal-text-secondary mt-0.5">
            {{ result.synthesis.explanation || "Unavailable" }}
          </p>
        </div>
        <div v-if="result.synthesis.risks?.length" class="mt-2">
          <span class="text-2xs font-sans text-terminal-text-tertiary block">Risks</span>
          <ul class="mt-0.5 space-y-0.5">
            <li v-for="(risk, i) in result.synthesis.risks" :key="i" class="text-xs font-mono text-terminal-warning">&bull; {{ risk }}</li>
          </ul>
        </div>
        <div v-if="result.synthesis.confluences?.length" class="mt-2">
          <span class="text-2xs font-sans text-terminal-text-tertiary block">Confluences</span>
          <ul class="mt-0.5 space-y-0.5">
            <li v-for="(confluence, i) in result.synthesis.confluences" :key="i" class="text-xs font-mono text-terminal-gain">&bull; {{ confluence }}</li>
          </ul>
        </div>
        <div v-if="result.synthesis.error" class="mt-2">
          <span class="text-2xs font-sans text-terminal-text-tertiary block">Synthesis Error</span>
          <p class="text-xs font-mono text-terminal-loss mt-0.5">{{ result.synthesis.error }}</p>
        </div>
      </section>

      <!-- OHLC Charts -->
      <section>
        <h2 class="text-xs font-sans font-medium text-terminal-text-secondary uppercase tracking-wider mb-2">Price Charts</h2>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-2">
          <div v-for="tf in (['D1', 'H4', 'H1'] as const)" :key="tf">
            <OhlcChart
              :data="result.ohlc?.[tf] || []"
              :overlay="overlay"
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
