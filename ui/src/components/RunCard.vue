<script setup lang="ts">
import { computed } from "vue";
import type { RunSummary } from "../types";
import { actionLabel, formatConfidencePct, isLegacySummary } from "../deterministicSetup";

const props = defineProps<{ run: RunSummary }>();
const emit = defineEmits<{ select: [run: RunSummary] }>();

const biasColor: Record<string, string> = {
  strong_bullish: "text-terminal-gain",
  bullish: "text-terminal-gain",
  neutral_bullish: "text-terminal-gain",
  neutral: "text-terminal-text-tertiary",
  neutral_bearish: "text-terminal-loss",
  bearish: "text-terminal-loss",
  strong_bearish: "text-terminal-loss",
};

const biasArrow: Record<string, string> = {
  strong_bullish: "▲▲",
  bullish: "▲",
  neutral_bullish: "▲",
  neutral: "–",
  neutral_bearish: "▼",
  bearish: "▼",
  strong_bearish: "▼▼",
};

const biasKey = computed(() => props.run.bias.toLowerCase());
const isOperational = computed(
  () => props.run.operational === true && props.run.validation_status === "VALID"
);
const validationClass = computed(() =>
  props.run.validation_status === "VALID"
    ? "text-terminal-gain"
    : "text-terminal-loss"
);
</script>

<template>
  <button
    class="w-full text-left p-3 border border-terminal-border bg-terminal-surface hover:bg-terminal-surface-hover transition-colors duration-150"
    @click="emit('select', run)"
  >
    <div class="flex items-center justify-between mb-1">
      <span class="text-sm font-sans text-terminal-text-secondary font-medium">{{ run.symbol }}</span>
      <span class="text-xs font-mono text-terminal-text-tertiary">{{ run.date }} {{ run.time }}</span>
    </div>
    <div class="flex items-center gap-2">
      <span :class="['text-sm font-mono font-medium', biasColor[biasKey] || 'text-terminal-text-tertiary']">
        {{ biasArrow[biasKey] || "–" }} {{ run.bias }}
      </span>
      <span class="text-xs font-mono text-terminal-text-secondary">
        {{ formatConfidencePct(run.confidence, isLegacySummary(run)) }}
      </span>
    </div>
    <div class="flex items-center justify-between mt-1">
      <span class="text-xs font-mono text-terminal-text-tertiary uppercase">{{ actionLabel(run.action) }}</span>
      <span :class="['text-xs font-mono', validationClass]">
        {{ run.validation_status }}
      </span>
    </div>
    <div class="flex items-center justify-between mt-1">
      <span class="text-xs font-mono text-terminal-text-tertiary uppercase">
        {{ run.setup_status }} / {{ run.direction }}
      </span>
      <span
        :class="[
          'text-xs font-mono',
          isOperational ? 'text-terminal-gain' : 'text-terminal-text-tertiary',
        ]"
      >
        {{ isOperational ? "OPERATIONAL" : "NON-OPERATIONAL" }}
      </span>
    </div>
  </button>
</template>
