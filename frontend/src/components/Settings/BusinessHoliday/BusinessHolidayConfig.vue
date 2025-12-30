<template>
  <BusinessHolidayList v-if="step.screen == 'list'" />
  <BusinessHolidayView v-else-if="step.screen == 'view'" />
</template>

<script setup>
import BusinessHolidayList from './BusinessHolidayList.vue'
import BusinessHolidayView from './BusinessHolidayView.vue'
import { ref, provide, onUnmounted } from 'vue'
import { createListResource } from 'frappe-ui'

const businessHolidaySearchQuery = ref('')
const step = ref({ screen: 'list', data: null, fetchData: false })

const businessHolidayListData = createListResource({
  doctype: 'CRM Holiday List',
  fields: ['name'],
  cache: ['BusinessHolidayList'],
  orderBy: 'modified desc',
  start: 0,
  pageLength: 999,
  auto: true,
})

provide('businessHolidaySearchQuery', businessHolidaySearchQuery)
provide('businessHolidayListResource', businessHolidayListData)
provide('step', step)
provide('updateStep', updateStep)

function updateStep(newStep, data, fetchData) {
  step.value = { screen: newStep, data, fetchData }
}

onUnmounted(() => {
  businessHolidaySearchQuery.value = ''
  businessHolidayListData.filters = {}
})
</script>
