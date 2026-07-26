<script setup lang="ts">
defineProps<{
  dates: string[];
  selected: string | null;
}>();

const emit = defineEmits<{
  select: [date: string | null];
}>();
</script>

<template>
  <div class="border-b border-terminal-border bg-terminal-surface px-3 py-2 overflow-x-auto">
    <div class="flex gap-1">
      <button
        class="px-2 py-1 text-xs font-mono"
        :class="selected === null ? 'bg-terminal-bg text-terminal-text' : 'text-terminal-text-secondary hover:bg-terminal-surface-hover'"
        @click="emit('select', null)"
      >All</button>
      <button
        v-for="d in dates"
        :key="d"
        class="px-2 py-1 text-xs font-mono"
        :class="selected === d ? 'bg-terminal-bg text-terminal-text' : 'text-terminal-text-secondary hover:bg-terminal-surface-hover'"
        @click="emit('select', d)"
      >{{ d.slice(5) }}</button>
    </div>
  </div>
</template>
