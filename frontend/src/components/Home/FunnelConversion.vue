<template>
  <div class="flex flex-col rounded-md p-4 grow w-full h-full overflow-hidden">
    <div class="flex flex-col gap-1 shrink-0 mb-4">
      <div class="flex items-center justify-between">
        <div class="flex flex-col gap-1">
          <div class="text-lg font-semibold text-ink-gray-8">
            {{ __('Funnel Conversion') }}
          </div>
          <div class="text-p-sm text-ink-gray-5">
            {{ __('Visualize lead-to-deal progress') }}
          </div>
        </div>
        <div class="flex items-center gap-2">
          <MultiSelect
            v-if="getLeadStatusesResource.fetched"
            :options="getLeadStatusesResource.data"
            v-model="selectedStatuses"
            placeholder="Select Statuses"
            @update:model-value="onStatusSelectionChange"
            :hide-search="false"
            class="w-64"
          >
            <template #target="{ togglePopover }">
              <button
                @click="togglePopover"
                class="w-full flex items-center justify-between px-3 py-2 text-sm border border-gray-200 rounded-md hover:bg-gray-50 transition-colors text-left"
              >
                <span class="text-gray-700">
                  {{
                    selectedStatuses.length === 0
                      ? 'Select Statuses'
                      : selectedStatuses.length ===
                          getLeadStatusesResource.data?.length
                        ? 'All Statuses'
                        : `${selectedStatuses.length} Selected`
                  }}
                </span>
                <svg
                  class="w-4 h-4 text-gray-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </button>
            </template>
          </MultiSelect>
        </div>
      </div>
    </div>
    <div class="relative grow w-full flex flex-col">
      <ECharts
        v-if="chartOptions && selectedStatuses.length > 0"
        :options="chartOptions"
        class="absolute inset-0 w-full h-full"
      />
      <EmptyState2
        v-if="selectedStatuses.length === 0"
        :title="__('No Statuses Selected')"
        :description="
          __('Select lead statuses to visualize funnel conversion data')
        "
      />
    </div>
  </div>
</template>

<script setup>
import { createResource, ECharts, MultiSelect } from 'frappe-ui'
import { computed, inject, onMounted, ref, nextTick } from 'vue'
import EmptyState2 from '../ListViews/EmptyState2.vue'

const props = defineProps({
  data: {
    type: Array,
    required: false,
  },
  selectedStatuses: {
    type: Array,
    default: () => [],
  },
})

const dashboardData = inject('dashboardData')
console.log('🚀 ~ dashboardData:', dashboardData)

const colors = computed(() => {
  const count = chartConfig.value?.length || 5
  const h = 242
  const s = 83.7
  const startL = 75.9
  const maxL = 90

  return Array.from({ length: count }, (_, i) => {
    const ratio = count === 1 ? 0 : (count - 1 - i) / (count - 1)
    const l = startL + (maxL - startL) * ratio
    return `hsl(${h} ${s}% ${l.toFixed(1)}%)`
  })
})

// State for status selection
const selectedStatuses = ref(props.selectedStatuses)

// Resources
const getLeadStatusesResource = createResource({
  url: 'crm.api.agent_home.agent_home.get_lead_statuses',
  auto: true,
})

const getFunnelConversionResource = createResource({
  url: 'crm.api.agent_home.agent_home.get_funnel_conversion',
})

const chartConfig = computed(() => {
  let data = []
  if (getFunnelConversionResource.fetched) {
    data = getFunnelConversionResource.data || []
  } else {
    data = props.data || []
  }

  // Sort data by lead status order when lead statuses are available
  if (getLeadStatusesResource.fetched && data.length > 0) {
    const statusOrder = new Map(
      getLeadStatusesResource.data.map((s, i) => [s.value, i]),
    )
    data = [...data].sort((a, b) => {
      const aIndex = statusOrder.get(a.label) ?? Infinity
      const bIndex = statusOrder.get(b.label) ?? Infinity
      return aIndex - bIndex
    })
  }

  return data
})

// Methods
const onStatusSelectionChange = async () => {
  // Update selected_statuses directly on the layout item
  if (dashboardData?.value) {
    const funnelItem = dashboardData.value.find(
      (item) => item.chart === 'funnel_conversion',
    )
    if (funnelItem) {
      funnelItem.selected_statuses = selectedStatuses.value
    }
  }
  // Fetch new data when statuses change
  if (selectedStatuses.value.length > 0) {
    fetchFunnelConversionData()
  }
}

// Fetch funnel conversion data with selected statuses
const fetchFunnelConversionData = () => {
  if (selectedStatuses.value.length > 0) {
    getFunnelConversionResource.submit({
      statuses: selectedStatuses.value,
    })
  }
}

const chartOptions = computed(() => {
  if (!chartConfig.value?.length) return null

  const dataValues = chartConfig.value.map((item) => item.value)
  const categories = chartConfig.value.map((item) => item.label)
  const maxValue = Math.max(...dataValues) * 1.1 || 1

  return {
    grid: {
      left: 0,
      right: 0,
      top: 66,
      bottom: 0,
    },
    tooltip: {
      show: true,
      trigger: 'item',
      formatter: (params) => {
        return `${params.name}: ${params.value}`
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
    xAxis: {
      type: 'category',
      data: categories,
      boundaryGap: true,
      show: false,
    },
    yAxis: {
      type: 'value',
      show: false,
      min: 0,
      max: maxValue,
    },
    series: [
      {
        type: 'custom',
        emphasis: {
          disabled: true,
        },
        data: dataValues.map((val, i) => ({
          name: categories[i],
          value: val,
          itemStyle: { color: colors.value[i % colors.length] },
        })),
        renderItem: function (params, api) {
          const val = dataValues[params.dataIndex]
          const maxValue = Math.max(...dataValues)
          const minBarHeight = maxValue * 0.06
          const nextVal = Math.max(val - minBarHeight, 0)

          const width = api.size([1, 0])[0]

          const cx = api.coord([params.dataIndex, 0])[0]
          const x = cx - width / 2
          const nextX = cx + width / 2

          const y1 = api.coord([0, val])[1]
          const y2 = api.coord([0, nextVal])[1]
          const yBottom = api.coord([0, 0])[1]

          return {
            type: 'group',
            children: [
              {
                type: 'path',
                shape: {
                  pathData: (function () {
                    const r = 8
                    const m = (y2 - y1) / (nextX - x)
                    return `
                      M ${x} ${yBottom}
                      L ${x} ${y1}
                      L ${nextX - r} ${y2 - m * r}
                      Q ${nextX} ${y2} ${nextX} ${y2 + r}
                      L ${nextX} ${yBottom}
                      Z
                    `
                  })(),
                },
                style: {
                  fill: colors.value[params.dataIndex % colors.value.length],
                },
                emphasis: {
                  style: {
                    fill: colors.value[params.dataIndex % colors.value.length],
                  },
                },
              },
              {
                type: 'text',
                x: params.dataIndex === 0 ? x : x + 16,
                y: 8,
                style: {
                  text: val.toString(),
                  fill: '#111827',
                  fontSize: 20,
                  fontWeight: 500,
                  textVerticalAlign: 'top',
                  width: width - 32,
                  overflow: 'truncate',
                },
              },
              {
                type: 'text',
                x: params.dataIndex === 0 ? x : x + 16,
                y: 36,
                style: {
                  text: categories[params.dataIndex] || '',
                  fill: '#6b7280',
                  fontSize: 13,
                  textVerticalAlign: 'top',
                  width: width - 32,
                  overflow: 'truncate',
                },
              },
              ...(params.dataIndex < dataValues.length - 1
                ? [
                    {
                      type: 'line',
                      shape: {
                        x1: nextX,
                        y1: 0,
                        x2: nextX,
                        y2: api.getHeight(),
                      },
                      style: {
                        stroke: '#E5E7EB',
                        lineWidth: 1,
                      },
                    },
                  ]
                : []),
            ],
          }
        },
      },
    ],
  }
})

onMounted(() => {
  if (!Array.isArray(props.data)) {
    selectedStatuses.value = props.selectedStatuses
    // Wait for preferences to load, then fetch data
    nextTick(() => {
      fetchFunnelConversionData()
    })
  }
})
</script>
