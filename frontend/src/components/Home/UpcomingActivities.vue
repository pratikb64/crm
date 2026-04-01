<template>
  <div class="flex flex-col rounded-md p-4 grow w-full h-full overflow-hidden">
    <div class="flex gap-4 items-center justify-between">
      <div
        class="flex items-center gap-2 text-lg font-semibold text-ink-gray-8"
      >
        {{ title }}
        <Tooltip :text="tooltipText" placement="top">
          <FeatherIcon name="info" class="size-3" />
        </Tooltip>
      </div>
      <div class="w-max">
        <TabButtons :buttons="chartTabs" v-model="currentTab" />
      </div>
    </div>
    <div class="flex flex-col mt-5 grow overflow-auto hide-scrollbar">
      <table class="w-full table-auto">
        <thead v-if="chartConfig?.activities?.length > 0">
          <tr class="text-sm text-gray-600">
            <th class="p-2 text-left font-normal w-full">
              {{ __('Activity') }}
            </th>
            <th class="p-2 text-left font-normal min-w-20 whitespace-nowrap">
              {{ __('Type') }}
            </th>
            <th class="p-2 text-left font-normal min-w-20 whitespace-nowrap">
              {{ __('Due') }}
            </th>
            <th class="p-2 text-left font-normal min-w-32 whitespace-nowrap">
              {{ __('Related To') }}
            </th>
            <th class="p-2 text-left font-normal min-w-40 whitespace-nowrap">
              {{ __('Account / Person') }}
            </th>
          </tr>
        </thead>
        <tbody v-if="chartConfig?.activities?.length > 0" class="grow">
          <tr
            v-for="activity in chartConfig?.activities"
            :key="activity.name"
            @click="goToActivity(activity)"
            class="text-sm cursor-pointer hover:bg-gray-50 border-t border-outline-gray-1"
          >
            <td class="p-2 py-3 w-full max-w-0 truncate">
              {{ activity.subject }}
            </td>
            <td class="p-2 py-3 min-w-20 truncate max-w-20">
              {{ activity.status }}
            </td>
            <td class="p-2 py-3 min-w-20 truncate max-w-20">
              <Badge
                :label="activity.priority"
                :theme="getPriorityBadgeColor(activity.priority_integer_value)"
              />
            </td>
            <td class="p-2 py-3 w-36 truncate max-w-36">
              {{ activity.agent_group || __('Not Assigned') }}
            </td>
            <td class="p-2 py-3 min-w-40">
              <div
                v-if="activity.reason"
                class="flex items-center gap-1 text-ink-gray-7 truncate w-full"
                :class="getReasonColorClass(activity.reason)"
              >
                <TimerIcon
                  v-if="activity.reason.type === 'leads'"
                  class="size-4 flex-shrink-0"
                />
                <TicketPlusIcon
                  v-else-if="activity.reason.type === 'deals'"
                  class="size-4 flex-shrink-0"
                />
                <CheckCircleIcon
                  v-else-if="activity.reason.type === 'tasks'"
                  class="size-4 flex-shrink-0"
                />
                <span class="truncate">{{ activity.reason.text }}</span>
              </div>
              <span
                v-else
                class="text-ink-gray-4 truncate inline-block w-full align-bottom"
                >{{ __('No reason') }}</span
              >
            </td>
          </tr>
        </tbody>
        <tbody class="relative" v-else>
          <tr
            v-for="i in 8"
            :key="i"
            :class="i > 1 ? 'border-t border-outline-gray-1' : ''"
          >
            <td class="p-2 py-3 w-full max-w-0">
              <div class="h-4 w-full bg-surface-gray-1 rounded-sm max-w-full" />
            </td>
            <td class="p-2 py-3 min-w-14">
              <div class="h-4 w-full bg-surface-gray-1 rounded-sm" />
            </td>
            <td class="p-2 py-3 min-w-21">
              <div class="h-4 w-full bg-surface-gray-1 rounded-sm" />
            </td>
            <td class="p-2 py-3 min-w-28">
              <div class="h-4 w-full bg-surface-gray-1 rounded-sm" />
            </td>
            <td class="p-2 py-3 min-w-40">
              <div class="h-4 w-full bg-surface-gray-1 rounded-sm" />
            </td>
          </tr>
          <EmptyState2
            v-if="chartConfig?.activities?.length === 0"
            :title="emptyStateText.title"
            :description="emptyStateText.description"
          />
        </tbody>
      </table>
      <div
        class="flex justify-between items-center text-sm mt-auto text-ink-gray-5 pl-2 pb-2"
      >
        <div>
          <div
            v-if="chartConfig?.total > 6"
            class="p-2 flex items-center gap-1 text-base text-ink-gray-5 cursor-pointer hover:text-ink-gray-7 w-max select-none mt-3"
            @click="redirectToSeeAll"
          >
            {{ __('See all {0}', [chartConfig?.total + ' ' + currentTab]) }}
            <FeatherIcon name="arrow-right" class="size-4" />
          </div>
        </div>
        <div v-if="chartConfig?.activities?.length > 0" class="mt-3 mb-0.5">
          {{
            __('Showing {0} of {1} {2}', [
              chartConfig?.activities?.length || 0 + '',
              chartConfig?.total || 0 + '',
              chartConfig?.activities?.length > 1
                ? currentTab
                : currentTab.replace(/s$/, ''),
            ])
          }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  Badge,
  createResource,
  FeatherIcon,
  TabButtons,
  Tooltip,
} from 'frappe-ui'
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import TimerIcon from '~icons/lucide/timer'
import TicketPlusIcon from '~icons/lucide/ticket-plus'
import CheckCircleIcon from '~icons/lucide/check-circle'
import EmptyState2 from '../ListViews/EmptyState2.vue'

const router = useRouter()

const props = defineProps({
  data: {
    type: Object,
    required: true,
  },
})

const currentTab = ref('leads')
const chartTabs = [
  {
    label: 'Leads',
    value: 'leads',
  },
  {
    label: 'Deals',
    value: 'deals',
  },
  {
    label: 'Tasks',
    value: 'tasks',
  },
]

const title = computed(() => {
  const labels = {
    leads: __('Leads'),
    deals: __('Deals'),
    tasks: __('Tasks'),
  }
  return labels[currentTab.value] || __('Leads')
})

const tooltipText = computed(() => {
  const texts = {
    leads: __('Leads where SLA response is due soon'),
    deals: __('Deals where SLA response is due soon'),
    tasks: __('Tasks which are due soon'),
  }
  return texts[currentTab.value]
})

const emptyStateText = computed(() => {
  const titles = {
    leads: __('No leads'),
    deals: __('No deals'),
    tasks: __('No tasks'),
  }
  const descriptions = {
    leads: __('All leads are resolved or converted to deals'),
    deals: __('All deals are resolved or converted to deals'),
    tasks: __('All tasks are completed'),
  }
  return {
    title: titles[currentTab.value],
    description: descriptions[currentTab.value],
  }
})

const chartConfig = computed(() => {
  const _data = getUpcomingActivitiesResource.fetched
    ? getUpcomingActivitiesResource.data
    : props.data

  const maxPriority = _data?.max_priority ?? 0
  const minPriority = _data?.min_priority ?? 0
  // Support both old format (leads/total_pending_leads) and new format (activities/total)
  const activities = _data?.activities || _data?.leads || []
  const total = _data?.total ?? _data?.total_pending_leads ?? 0

  return {
    activities,
    maxPriority,
    minPriority,
    total,
  }
})

const getUpcomingActivitiesResource = createResource({
  url: 'crm.api.agent_home.agent_home.get_upcoming_activities',
  params: { activity_type: currentTab.value },
})

watch(currentTab, (newTab) => {
  getUpcomingActivitiesResource.params = { activity_type: newTab }
  getUpcomingActivitiesResource.fetch()
})

function getPriorityBadgeColor(integerValue) {
  const min = chartConfig.value.minPriority || 0
  const max = chartConfig.value.maxPriority || 0
  const range = max - min
  if (range === 0) return 'gray'
  const position = (integerValue - min) / range
  if (position < 0.25) return 'gray'
  if (position < 0.5) return 'green'
  if (position < 0.75) return 'orange'
  return 'red'
}

function getReasonColorClass(reason) {
  if (reason.text.includes('overdue')) {
    return 'text-red-500'
  }
  if (reason.text.includes('due in')) {
    if (reason.text.includes('m') || reason.text.includes('s')) {
      return 'text-red-500'
    }
    if (reason.text.includes('h')) {
      const hoursMatch = reason.text.match(/\d+/)
      const hours = hoursMatch ? parseInt(hoursMatch[0]) : 0
      if (hours <= 2) {
        return 'text-orange-500'
      }
    }
  }
  return ''
}

const goToActivity = (activity) => {
  if (!activity.name) return

  const routeMap = {
    leads: { name: 'Lead', params: { leadId: activity.name } },
    deals: { name: 'Deal', params: { dealId: activity.name } },
    tasks: { name: 'Task', params: { taskId: activity.name } },
  }

  const route = routeMap[currentTab.value]
  if (route) {
    router.push(route)
  }
}

const redirectToSeeAll = () => {
  const routeMap = {
    leads: 'Leads',
    deals: 'Deals',
    tasks: 'Tasks',
  }
  router.push({ name: routeMap[currentTab.value] || 'Leads' })
}

onMounted(() => {
  if (!props.data) {
    getUpcomingActivitiesResource.fetch()
  }
})
</script>
