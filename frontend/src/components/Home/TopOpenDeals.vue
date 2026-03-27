<template>
  <div class="flex flex-col rounded-md p-4 grow w-full h-full overflow-hidden">
    <div class="flex flex-col gap-1 shrink-0 mb-4">
      <div class="text-lg font-semibold text-ink-gray-8">
        {{ __('Top Deals') }}
      </div>
      <div class="text-p-sm text-ink-gray-5">
        {{ __('Track your highest value opportunities') }}
      </div>
    </div>
    <div class="grow w-full flex flex-col gap-4 overflow-y-auto">
      <div
        v-if="!chartConfig || chartConfig.length === 0"
        class="space-y-4 h-full text-sm text-ink-gray-5 relative"
      >
        <div class="flex justify-between mt-4">
          <div class="bg-surface-gray-1 w-1/2 h-5"></div>
          <div class="bg-surface-gray-1 w-6 h-5"></div>
        </div>
        <div class="flex justify-between">
          <div class="bg-surface-gray-1 w-1/2 h-5"></div>
          <div class="bg-surface-gray-1 w-6 h-5"></div>
        </div>
        <div class="flex justify-between">
          <div class="bg-surface-gray-1 w-1/2 h-5"></div>
          <div class="bg-surface-gray-1 w-6 h-5"></div>
        </div>
        <div class="flex justify-between">
          <div class="bg-surface-gray-1 w-1/2 h-5"></div>
          <div class="bg-surface-gray-1 w-6 h-5"></div>
        </div>
        <EmptyState2
          :title="__('No open deals')"
          :description="__('You don\'t have any open deals yet')"
        />
      </div>
      <div
        v-for="deal in chartConfig"
        :key="deal.label"
        class="flex items-center justify-between cursor-pointer rounded-md p-1 -m-1 transition-colors"
        @click="goToDeal(deal)"
      >
        <div class="flex items-center gap-3">
          <Avatar shape="square" :src="deal.image" :label="deal.label" />
          <div class="flex items-center gap-1">
            <span class="text-base text-ink-gray-9">{{ deal.label }}</span>
            <FeatherIcon
              name="arrow-up-right"
              class="w-4 h-4 text-ink-gray-5"
            />
          </div>
        </div>
        <div class="text-base font-semibold text-ink-gray-9">
          {{ formatCurrency(deal.value) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Avatar, createResource, FeatherIcon } from 'frappe-ui'
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import EmptyState2 from '../ListViews/EmptyState2.vue'

const props = defineProps({
  data: {
    type: Array,
    required: false,
  },
})

const router = useRouter()

const goToDeal = (deal) => {
  if (deal.name) {
    router.push({ name: 'Deal', params: { dealId: deal.name } })
  }
}

const getTopOpenDealsResource = createResource({
  url: 'crm.api.agent_home.agent_home.get_top_open_deals',
})

const chartConfig = computed(() => {
  if (getTopOpenDealsResource.fetched) {
    return getTopOpenDealsResource.data
  }
  return props.data || []
})

const formatCurrency = (value) => {
  if (value >= 1000) {
    return `$${(value / 1000).toFixed(0)}k`
  }
  return `$${value}`
}

const getIconColorClass = (colorName) => {
  switch (colorName) {
    case 'green':
      return 'bg-green-600'
    case 'pink':
      return 'bg-pink-400'
    case 'red':
      return 'bg-red-500'
    case 'blue':
      return 'bg-blue-600'
    default:
      return 'bg-gray-500'
  }
}

onMounted(() => {
  if (!Array.isArray(props.data)) {
    getTopOpenDealsResource.fetch()
  }
})
</script>
