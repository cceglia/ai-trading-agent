<script setup lang="ts">
defineProps<{
  symbols: string[];
  selected: string | null;
  runCounts: Record<string, number>;
  totalRuns: number;
}>();

const emit = defineEmits<{
  select: [symbol: string | null];
}>();
</script>

<template>
  <aside class="w-44 border-r border-terminal-border bg-terminal-surface overflow-y-auto flex-shrink-0">
    <div class="p-2">
      <button
        class="w-full text-left px-2 py-1.5 text-xs font-mono"
        :class="selected === null ? 'bg-terminal-bg text-terminal-text' : 'text-terminal-text-secondary hover:bg-terminal-surface-hover'"
        @click="emit('select', null)"
      >
        All ({{ totalRuns }})
      </button>
      <button
        v-for="s in symbols"
        :key="s"
        class="w-full text-left px-2 py-1.5 text-xs font-mono"
        :class="selected === s ? 'bg-terminal-bg text-terminal-text' : 'text-terminal-text-secondary hover:bg-terminal-surface-hover'"
        @click="emit('select', s)"
      >
        {{ s }}
        <span class="text-terminal-text-tertiary ml-1">({{ runCounts[s] || 0 }})</span>
      </button>
    </div>
  </aside>
</template>
