<template>
  <div class="flex flex-col rounded-md p-4 grow w-full h-full overflow-hidden">
    <div class="flex flex-col gap-1 shrink-0 mb-6">
      <div class="text-lg font-semibold text-ink-gray-8">
        {{ __('Revenue Performance') }}
      </div>
      <div class="text-p-sm text-ink-gray-5">
        {{ __('Track your actual sales revenue against projected targets.') }}
      </div>
    </div>
    <div class="relative grow w-full flex flex-col">
      <ECharts
        v-if="chartOptions"
        :options="chartOptions"
        class="absolute inset-0 w-full h-full"
      />
    </div>
  </div>
</template>

<script setup>
import { createResource, ECharts } from 'frappe-ui'
import { computed, onMounted } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    required: false,
  },
})

// Fallback default data while API loads
const defaultData = {
  categories: [
    'Jan',
    '',
    '',
    'Feb',
    '',
    '',
    'Mar',
    '',
    '',
    'Apr',
    '',
    '',
    'May',
    '',
    '',
    'Jun',
    '',
  ],
  forecast: [
    18000, 37000, 31000, 64000, 59000, 70000, 109000, 76000, 67000, 116000,
    121000, 144000, 119000, 158000, 146000, 174000, 175000,
  ],
  actual: [
    0, 31000, 32000, 21000, 51000, 52000, 79000, 66000, 74000, 90000, 93000,
    119000, 101000, 117000, 129000,
  ],
}

const getForecastResource = createResource({
  url: 'crm.api.agent_home.agent_home.get_forecast_vs_actual',
})

const chartConfig = computed(() => {
  if (getForecastResource.fetched && getForecastResource.data) {
    return getForecastResource.data
  }
  if (props.data && props.data.forecast && props.data.forecast.length > 0) {
    return props.data
  }
  return defaultData
})

const chartOptions = computed(() => {
  if (!chartConfig.value) return null

  const categories = chartConfig.value.categories
  const forecast = chartConfig.value.forecast
  const actual = chartConfig.value.actual

  return {
    grid: {
      left: 10,
      right: 15,
      top: 10,
      bottom: 30, // Space for legend and x-axis
      containLabel: true,
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#fff',
      borderColor: '#E5E7EB',
      borderWidth: 1,
      padding: [8, 12],
      textStyle: {
        color: '#111827',
        fontSize: 13,
      },
      extraCssText:
        'box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1); border-radius: 8px;',
      valueFormatter: (value) => {
        if (value == null) return ''
        return '$' + value.toLocaleString()
      },
    },
    legend: {
      data: ['Forecast', 'Actual'],
      bottom: 0,
      icon: 'circle',
      itemGap: 24,
      textStyle: {
        color: '#374151',
        fontSize: 14,
        fontWeight: 400,
      },
    },
    xAxis: {
      type: 'category',
      data: categories,
      boundaryGap: false,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: '#6B7280',
        fontSize: 12,
        margin: 12,
        formatter: (value) => (value === '' ? '' : value),
      },
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 200000,
      interval: 25000,
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: '#E5E7EB',
        },
      },
      axisLabel: {
        color: '#6B7280',
        fontSize: 12,
        formatter: (value) => {
          if (value === 0) return '$0'
          return '$' + value / 1000 + 'k'
        },
      },
    },
    series: [
      {
        name: 'Forecast',
        type: 'line',
        data: forecast.map((val, index) => ({
          value: val,
          symbol: index === forecast.length - 1 ? 'circle' : 'none',
          symbolSize: 8,
        })),
        itemStyle: {
          color: '#7C3AED', // purple/indigo
        },
        lineStyle: {
          width: 2,
        },
        z: 2,
      },
      {
        name: 'Actual',
        type: 'line',
        data: actual.map((val, index) => ({
          value: val,
          symbol: index === actual.length - 1 ? 'circle' : 'none',
          symbolSize: 8,
        })),
        itemStyle: {
          color: '#E879F9', // pink/magenta
        },
        lineStyle: {
          width: 2,
        },
        z: 3,
      },
    ],
  }
})

onMounted(() => {
  if (!props.data) {
    getForecastResource.fetch()
  }
})
</script>
