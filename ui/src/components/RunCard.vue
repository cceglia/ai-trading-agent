<script setup lang="ts">
import type { RunSummary } from "../types";

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

function formatConfidence(confidence: number): string {
  return `${Math.round(confidence)}%`;
}
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
      <span :class="['text-sm font-mono font-medium', biasColor[run.bias] || 'text-terminal-text-tertiary']">
        {{ biasArrow[run.bias] || "–" }} {{ run.bias.replace("_", " ") }}
      </span>
      <span class="text-xs font-mono text-terminal-text-secondary">
        {{ formatConfidence(run.confidence) }}
      </span>
    </div>
    <div class="flex items-center justify-between mt-1">
      <span class="text-xs font-mono text-terminal-text-tertiary uppercase">{{ run.action.replace("_", " ") }}</span>
      <span :class="['text-xs', run.validation_status === 'VALID' ? 'text-terminal-gain' : 'text-terminal-loss']">
        {{ run.validation_status }}
      </span>
    </div>
  </button>
</template>
