<template>
  <div class="flex flex-col rounded-md p-4 grow w-full h-full overflow-hidden">
    <div class="flex flex-col gap-1 shrink-0 mb-4">
      <div class="text-lg font-semibold text-ink-gray-8">
        {{ __('Expected Closures') }}
      </div>
      <div class="text-p-sm text-ink-gray-5">
        {{ __('Actual vs projected sales for the month') }}
      </div>
    </div>
    <div
      v-if="isForecastingEnabled"
      class="text-xl font-bold text-ink-gray-7 mb-2"
    >
      {{ formattedActual }} / {{ formattedProjected }}
    </div>
    <div class="relative grow w-full flex flex-col justify-center pb-6">
      <ECharts
        v-if="chartOptions && isForecastingEnabled"
        :options="chartOptions"
        class="w-full h-13"
      />
      <EmptyState2
        v-if="!isForecastingEnabled"
        :title="__('Forecasting Disabled')"
        :description="__('Enable it to see expected closures against targets')"
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
import EmptyState2 from '@/components/ListViews/EmptyState2.vue'

const props = defineProps({
  data: {
    type: Object,
    required: false,
  },
})

const { settings } = getSettings()

const isForecastingEnabled = computed(() => {
  return Boolean(settings.value?.enable_forecasting) === true
})

const getExpectedClosureResource = createResource({
  url: 'crm.api.agent_home.agent_home.get_expected_closure',
})

const chartConfig = computed(() => {
  if (getExpectedClosureResource.fetched) {
    return getExpectedClosureResource.data
  }
  return props.data || { actual: 19200, projected: 24000 }
})

const formatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
})

const formattedActual = computed(() => {
  return formatter.format(chartConfig.value?.actual || 0)
})

const formattedProjected = computed(() => {
  return formatter.format(chartConfig.value?.projected || 0)
})

const chartOptions = computed(() => {
  if (!chartConfig.value) return null

  const actual = chartConfig.value.actual
  const projected = chartConfig.value.projected

  return {
    grid: {
      left: 0,
      right: 0,
      top: 0,
      bottom: 0,
    },
    xAxis: {
      type: 'value',
      max: projected,
      show: false,
    },
    yAxis: {
      type: 'category',
      data: ['Closure'],
      show: false,
    },
    series: [
      {
        type: 'bar',
        data: [actual],
        barWidth: 40,
        showBackground: true,
        backgroundStyle: {
          color: '#F4F5F6',
          borderRadius: [0, 4, 4, 0],
        },
        itemStyle: {
          color: '#2EB68F',
          borderRadius: [4, 0, 0, 4],
        },
        z: 2,
      },
      {
        type: 'custom',
        data: [actual],
        z: 3,
        renderItem: function (params, api) {
          const x = api.coord([api.value(0), 0])[0]
          const y = api.coord([api.value(0), 0])[1]
          const barHeight = 40

          return {
            type: 'line',
            shape: {
              x1: x,
              y1: y - barHeight / 2 - 20, // slightly above
              x2: x,
              y2: y + barHeight / 2 + 20, // extends below
            },
            style: {
              stroke: '#374151',
              lineWidth: 1.5,
            },
          }
        },
      },
    ],
  }
})

onMounted(() => {
  if (!props.data) {
    getExpectedClosureResource.fetch()
  }
})

function openForecastingSettings() {
  activeSettingsPage.value = 'Forecasting'
  showSettings.value = true
}
</script>
