<template>
  <div class="flex flex-col rounded-md p-4 grow w-full h-full overflow-hidden">
    <div class="flex flex-col gap-1 shrink-0 mb-4">
      <div class="text-lg font-semibold text-ink-gray-8">
        {{ __('Deals By Stage') }}
      </div>
      <div class="text-p-sm text-ink-gray-5">
        {{ __('Track your deal progress') }}
      </div>
    </div>
    <div class="relative grow w-full flex flex-col gap-3">
      <ECharts
        v-if="chartOptions"
        :options="chartOptions"
        class="w-full h-4 shrink-0"
      />
      <div class="flex flex-col gap-3 w-full mt-3 grow">
        <div
          v-if="!chartConfig || chartConfig.length === 0"
          class="h-full text-sm text-ink-gray-5 relative"
        >
          <div class="flex flex-col gap-2 w-full grow">
            <div class="bg-surface-gray-1 rounded-full w-full h-2.5"></div>
            <div class="w-full grow flex flex-col gap-4 mt-4">
              <div class="bg-surface-gray-1 rounded-full w-1/2 h-4"></div>
              <div class="bg-surface-gray-1 rounded-full w-1/2 h-4"></div>
              <div class="bg-surface-gray-1 rounded-full w-1/2 h-4"></div>
              <div class="bg-surface-gray-1 rounded-full w-1/2 h-4"></div>
            </div>
            <EmptyState2
              :title="__('No deals')"
              :description="__('You don\'t have any deals yet')"
            />
          </div>
        </div>
        <div
          v-for="(item, index) in chartConfig"
          :key="item.label"
          class="flex items-center justify-between text-base"
        >
          <div class="flex items-center gap-3">
            <div
              class="size-2 rounded-full shrink-0"
              :style="{ backgroundColor: colors[index % colors.length] }"
            />
            <span class="text-ink-gray-7">{{ item.label }}</span>
          </div>
          <span class="font-medium text-ink-gray-8">{{
            formatCurrency(item.value)
          }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { createResource, ECharts } from 'frappe-ui'
import { computed, onMounted } from 'vue'
import EmptyState2 from '../ListViews/EmptyState2.vue'
import { formatCurrency } from '../../utils/numberFormat.js'

const props = defineProps({
  data: {
    type: Array,
    required: false,
  },
})

const colors = ['#4AB1ED', '#8157ED', '#4363F3', '#DD56D8']

const getDealsByStageResource = createResource({
  url: 'crm.api.agent_home.agent_home.get_deals_by_stage',
})

const chartConfig = computed(() => {
  if (getDealsByStageResource.fetched) {
    return getDealsByStageResource.data
  }
  return props.data || []
})

const chartOptions = computed(() => {
  if (!chartConfig.value?.length) return null

  return {
    grid: {
      left: 0,
      right: 0,
      top: 0,
      bottom: 0,
    },
    xAxis: {
      type: 'value',
      show: false,
      max: 'dataMax',
    },
    yAxis: {
      type: 'category',
      data: ['Deals'],
      show: false,
    },
    tooltip: {
      show: true,
      trigger: 'item',
      formatter: (params) => {
        return `${params.seriesName}: ${formatCurrency(params.value)}`
      },
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
    },
    series: chartConfig.value.map((item, index) => {
      const isFirst = index === 0
      const isLast = index === chartConfig.value.length - 1
      return {
        name: item.label,
        type: 'bar',
        stack: 'total',
        barWidth: 12,
        itemStyle: {
          color: colors[index % colors.length],
          borderRadius: [
            isFirst ? 6 : 0,
            isLast ? 6 : 0,
            isLast ? 6 : 0,
            isFirst ? 6 : 0,
          ],
          borderColor: '#ffffff',
          borderWidth: 2,
        },
        data: [item.value],
      }
    }),
  }
})

onMounted(() => {
  if (!props.data || props.data.length === 0) {
    getDealsByStageResource.fetch()
  }
})
</script>
