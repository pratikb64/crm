<template>
  <div class="flex flex-col rounded-md p-4 grow w-full h-full overflow-hidden">
    <div class="flex flex-col gap-1 shrink-0 mb-6">
      <div class="text-lg font-semibold text-ink-gray-8">
        {{ __('Funnel Conversion') }}
      </div>
      <div class="text-p-sm text-ink-gray-5">
        {{ __('Visualize lead-to-deal progress') }}
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
    type: Array,
    required: false,
  },
})

const colors = ['#F2F2FD', '#E8E8F7', '#D6D5F6', '#B7B6FC', '#928EF5']

const getFunnelConversionResource = createResource({
  url: 'crm.api.agent_home.agent_home.get_funnel_conversion',
})

const chartConfig = computed(() => {
  if (getFunnelConversionResource.fetched) {
    return getFunnelConversionResource.data
  }
  return props.data || []
})

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
          itemStyle: { color: colors[i % colors.length] },
        })),
        renderItem: function (params, api) {
          const val = dataValues[params.dataIndex]
          const maxValue = Math.max(...dataValues)
          const minBarHeight = maxValue * 0.06
          const nextVal = Math.max(val - minBarHeight, 0)

          // width of a category column
          const width = api.size([1, 0])[0]

          // center of the category
          const cx = api.coord([params.dataIndex, 0])[0]

          // left and right bounds
          // To ensure they perfectly align with the text border-r (which separates equally), width/2 logic correctly fills the grid cell
          const x = cx - width / 2
          const nextX = cx + width / 2

          // y values
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
                  fill: api.visual('color'),
                },
                emphasis: {
                  style: {
                    fill: api.visual('color'),
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
    getFunnelConversionResource.fetch()
  }
})
</script>
