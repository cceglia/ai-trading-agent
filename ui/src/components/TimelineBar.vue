<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  years: string[];
  months: string[];
  days: string[];
  selectedYear: string | null;
  selectedMonth: string | null;
  selectedDay: string | null;
}>();

const emit = defineEmits<{
  selectYear: [year: string | null];
  selectMonth: [month: string | null];
  selectDay: [day: string | null];
}>();

/** Writable computed proxies — no duplicated state, no sync watchers needed. */
const localYear = computed({
  get: () => props.selectedYear,
  set: (v) => emit("selectYear", v),
});
const localMonth = computed({
  get: () => props.selectedMonth,
  set: (v) => emit("selectMonth", v),
});
const localDay = computed({
  get: () => props.selectedDay,
  set: (v) => emit("selectDay", v),
});
</script>

<template>
  <div class="border-b border-terminal-border bg-terminal-surface px-3 py-2 overflow-x-auto">
    <div class="flex gap-2 items-center">
      <select
        v-model="localYear"
        class="bg-terminal-bg border border-terminal-border text-terminal-text-secondary text-xs font-mono px-2 py-1"
      >
        <option :value="null">All Years</option>
        <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
      </select>

      <select
        v-model="localMonth"
        class="bg-terminal-bg border border-terminal-border text-terminal-text-secondary text-xs font-mono px-2 py-1"
      >
        <option :value="null">All Months</option>
        <option v-for="m in months" :key="m" :value="m">{{ m }}</option>
      </select>

      <select
        v-model="localDay"
        class="bg-terminal-bg border border-terminal-border text-terminal-text-secondary text-xs font-mono px-2 py-1"
      >
        <option :value="null">All Days</option>
        <option v-for="d in days" :key="d" :value="d">{{ d }}</option>
      </select>
    </div>
  </div>
</template>
