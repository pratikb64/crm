<template>
  <div class="h-full w-full rounded border border-outline-gray-1">
    <UpcomingActivities
      v-if="item.chart === 'upcoming_activities'"
      :data="item.data"
    />
    <FunnelConversion
      v-else-if="item.chart === 'funnel_conversion'"
      :data="item.data"
    />
    <DealsByStage
      v-else-if="item.chart === 'deals_by_stage'"
      :data="item.data"
    />
    <TopOpenDeals
      v-else-if="item.chart === 'top_open_deals'"
      :data="item.data"
    />
    <ExpectedClosure
      v-else-if="item.chart === 'expected_closure'"
      :data="item.data"
    />
    <ForecastVsActual
      v-else-if="item.chart === 'forecast_vs_actual'"
      :data="item.data"
    />
  </div>
</template>

<script setup>
import UpcomingActivities from './UpcomingActivities.vue'
import FunnelConversion from './FunnelConversion.vue'
import DealsByStage from './DealsByStage.vue'
import TopOpenDeals from './TopOpenDeals.vue'
import ExpectedClosure from './ExpectedClosure.vue'
import ForecastVsActual from './ForecastVsActual.vue'

defineProps({
  item: {
    type: Object,
    required: true,
  },
})
</script>
