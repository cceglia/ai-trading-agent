<script setup lang="ts">
import { computed } from "vue";
import { use } from "echarts/core";
import { CandlestickChart, LineChart } from "echarts/charts";
import { GridComponent, TooltipComponent, LegendComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import type { SeriesOption } from "echarts";
import VChart from "vue-echarts";
import type { OHLCBar, SLTPOverlay } from "../types";

use([CandlestickChart, LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

const props = defineProps<{
  data: OHLCBar[];
  overlay?: SLTPOverlay;
  timeframe: string;
}>();

const chartOption = computed(() => {
  const dates = props.data.map((d) => d.time);
  const ohlc = props.data.map((d) => [d.open, d.close, d.low, d.high]);

  const series: SeriesOption[] = [
    {
      type: "candlestick",
      data: ohlc,
      itemStyle: {
        color: "#00D4AA",
        color0: "#FF4757",
        borderColor: "#00D4AA",
        borderColor0: "#FF4757",
      },
    },
  ];

  if (props.overlay) {
    const prices: { price: number; name: string }[] = [];
    if (props.overlay.entry_price != null) {
      prices.push({ price: props.overlay.entry_price, name: "Entry" });
    }
    if (props.overlay.stop_loss != null) {
      prices.push({ price: props.overlay.stop_loss, name: "SL" });
    }
    if (props.overlay.take_profit != null) {
      prices.push({ price: props.overlay.take_profit, name: "TP" });
    }

    for (const p of prices) {
      series.push({
        type: "line",
        data: Array(dates.length).fill(p.price),
        name: p.name,
        symbol: "none",
        lineStyle: {
          type: "dashed" as const,
          width: 1,
          color: p.name === "SL" ? "#FF4757" : p.name === "TP" ? "#00D4AA" : "#FFB800",
        },
      });
    }
  }

  return {
    backgroundColor: "transparent",
    grid: { left: "5%", right: "5%", top: "10%", bottom: "10%" },
    xAxis: {
      type: "category" as const,
      data: dates,
      axisLine: { lineStyle: { color: "#2A2A2A" } },
      axisLabel: { color: "#808086", fontSize: 10, fontFamily: "JetBrains Mono" },
      splitLine: { show: false },
    },
    yAxis: {
      type: "value" as const,
      scale: true,
      axisLine: { show: false },
      axisLabel: { color: "#808086", fontSize: 10, fontFamily: "JetBrains Mono" },
      splitLine: { lineStyle: { color: "#2A2A2A", type: "dashed" as const } },
    },
    tooltip: {
      trigger: "axis" as const,
      backgroundColor: "#141414",
      borderColor: "#2A2A2A",
      textStyle: { color: "#FFFFFF", fontFamily: "JetBrains Mono", fontSize: 11 },
    },
    series,
  };
});
</script>

<template>
  <div class="border border-terminal-border bg-terminal-surface p-2">
    <div class="flex items-center justify-between mb-1 px-1">
      <span class="text-xs font-mono text-terminal-text-secondary font-medium uppercase">{{ timeframe }}</span>
    </div>
    <v-chart :option="chartOption" autoresize style="height: 350px" />
  </div>
</template>
