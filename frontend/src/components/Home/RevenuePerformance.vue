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
        v-if="chartOptions && isForecastingEnabled"
        :options="chartOptions"
        class="absolute inset-0 w-full h-full"
      />
      <EmptyState2
        v-if="!isForecastingEnabled"
        :title="__('Forecasting Disabled')"
        :description="
          __('Enable it to track revenue performance against targets')
        "
      >
        <template #action>
          <Button variant="subtle" @click="openForecastingSettings">
            {{ __('Enable') }}
          </Button>
        </template>
      </EmptyState2>
    </div>
  </div>
</template>

<script setup>
import { createResource, ECharts, Button } from 'frappe-ui'
import { computed, onMounted } from 'vue'
import { getSettings } from '@/stores/settings'
import { showSettings, activeSettingsPage } from '@/composables/settings'
import { formatCurrency } from '@/utils/numberFormat'
import EmptyState2 from '@/components/ListViews/EmptyState2.vue'
import { useChartTheme } from '@/composables/useChartTheme.js'

const props = defineProps({
  data: {
    type: Object,
    required: false,
  },
})

const { settings } = getSettings()
const { chartColors } = useChartTheme()

const isForecastingEnabled = computed(() => {
  return Boolean(settings.value?.enable_forecasting) === true
})

const getForecastResource = createResource({
  url: 'crm.api.agent_home.agent_home.get_revenue_performance',
})

const chartConfig = computed(() => {
  if (getForecastResource.fetched && getForecastResource.data) {
    return getForecastResource.data
  }
  if (props.data && props.data.forecast && props.data.forecast.length > 0) {
    return props.data
  }
  return null
})

const chartOptions = computed(() => {
  if (!chartConfig.value) return null

  const categories = chartConfig.value.categories
  const forecast = chartConfig.value.forecast
  const actual = chartConfig.value.actual
  const colors = chartColors.value

  return {
    grid: {
      left: 10,
      right: 15,
      top: 10,
      bottom: 30,
      containLabel: true,
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: colors.tooltip.backgroundColor,
      borderColor: colors.tooltip.borderColor,
      borderWidth: 1,
      padding: [8, 12],
      textStyle: {
        color: colors.tooltip.textColor,
        fontSize: 13,
      },
      extraCssText:
        'box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1); border-radius: 8px;',
      valueFormatter: (value) => {
        if (value == null) return ''
        return formatCurrency(value)
      },
    },
    legend: {
      data: ['Forecast', 'Actual'],
      bottom: 0,
      icon: 'circle',
      itemGap: 24,
      textStyle: {
        color: colors.legend.text,
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
        color: colors.axis.label,
        fontSize: 12,
        margin: 12,
        formatter: (value) => (value === '' ? '' : value),
      },
    },
    yAxis: {
      type: 'value',
      min: 0,
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: colors.axis.splitLine,
        },
      },
      axisLabel: {
        color: colors.axis.label,
        fontSize: 12,
        formatter: (value) => {
          if (value === 0) return formatCurrency(0)
          return formatCurrency(value, null, 'USD', 0)
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

function openForecastingSettings() {
  activeSettingsPage.value = 'Forecasting'
  showSettings.value = true
}
</script>
