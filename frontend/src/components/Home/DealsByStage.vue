<template>
  <div class="flex flex-col rounded-md p-4 grow w-full h-full overflow-hidden">
    <div class="flex flex-col gap-1 shrink-0 mb-4">
      <div class="flex items-center justify-between">
        <div class="flex flex-col gap-1">
          <div class="text-lg font-semibold text-ink-gray-8">
            {{ __('Deals By Stage') }}
          </div>
          <div class="text-p-sm text-ink-gray-5">
            {{ __('Track your deal progress') }}
          </div>
        </div>
        <div class="flex items-center gap-2">
          <MultiSelect
            v-if="getDealStatusesResource.fetched"
            :options="getDealStatusesResource.data"
            v-model="selectedStages"
            placeholder="Select Stages"
            @update:model-value="onStageSelectionChange"
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
                    selectedStages.length === 0
                      ? 'Select Stages'
                      : selectedStages.length ===
                          getDealStatusesResource.data?.length
                        ? 'All Stages'
                        : `${selectedStages.length} Selected`
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
    <div class="relative grow w-full flex flex-col gap-3">
      <ECharts
        v-if="chartOptions && selectedStages.length > 0"
        :options="chartOptions"
        class="w-full h-4 shrink-0"
      />
      <div class="flex flex-col gap-3 w-full mt-3 grow">
        <div
          v-if="selectedStages.length === 0"
          class="h-full text-sm text-ink-gray-5 relative"
        >
          <EmptyState2
            :title="__('No Stages Selected')"
            :description="__('Select deal stages to view deals by stage data')"
          />
        </div>
        <div
          v-for="(item, index) in chartConfig"
          :key="item.label"
          class="flex items-center justify-between text-base"
          v-show="selectedStages.length > 0"
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
import { createResource, ECharts, MultiSelect } from 'frappe-ui'
import { computed, onMounted, ref, nextTick, watch } from 'vue'
import EmptyState2 from '../ListViews/EmptyState2.vue'
import { formatCurrency } from '../../utils/numberFormat.js'

const props = defineProps({
  data: {
    type: Array,
    required: false,
  },
  selectedStages: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['update:selectedStages'])

const colors = ['#4AB1ED', '#8157ED', '#4363F3', '#DD56D8']

// State for stage selection
const selectedStages = ref(props.selectedStages)

// Resources
const getDealStatusesResource = createResource({
  url: 'crm.api.agent_home.agent_home.get_deal_statuses',
  auto: true,
})

const getDealsByStageResource = createResource({
  url: 'crm.api.agent_home.agent_home.get_deals_by_stage',
})

// Methods
const onStageSelectionChange = async () => {
  emit('update:selectedStages', selectedStages.value)
  // Fetch new data when stages change
  if (selectedStages.value.length > 0) {
    fetchDealsByStageData()
  }
}

// Fetch deals by stage data with selected stages
const fetchDealsByStageData = () => {
  if (selectedStages.value.length > 0) {
    getDealsByStageResource.submit({
      stages: selectedStages.value,
    })
  }
}

const chartConfig = computed(() => {
  if (getDealsByStageResource.fetched) {
    return getDealsByStageResource.data
  }
  return props.data || []
})

const chartOptions = computed(() => {
  if (!chartConfig.value?.length || selectedStages.value.length === 0)
    return null

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
      min: 0,
      scale: true,
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
      // Use a minimal value for rendering but keep original for tooltip
      const displayValue = item.value === 0 ? 0.001 : item.value
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
        data: [displayValue],
        emphasis: {
          itemStyle: {
            opacity: 0.8,
          },
        },
        tooltip: {
          formatter: () => `${item.label}: ${formatCurrency(item.value)}`,
        },
      }
    }),
  }
})

onMounted(() => {
  if (!Array.isArray(props.data)) {
    selectedStages.value = props.selectedStages
    // Wait for preferences to load, then fetch data
    nextTick(() => {
      fetchDealsByStageData()
    })
  }
})

// Watch for changes in props.selectedStages
watch(
  () => props.selectedStages,
  (newStages) => {
    if (JSON.stringify(newStages) !== JSON.stringify(selectedStages.value)) {
      selectedStages.value = newStages
      fetchDealsByStageData()
    }
  },
  { deep: true },
)
</script>
