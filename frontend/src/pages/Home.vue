<template>
  <LayoutHeader>
    <template #left-header>
      <div class="text-lg font-medium text-gray-900">{{ __('Home') }}</div>
    </template>
    <template #right-header>
      <div class="flex items-center gap-2">
        <Button
          v-if="layout.length > 0 && !editing"
          :label="__('Refresh')"
          variant="subtle"
          :icon-left="LucideRefreshCcw"
          :disabled="isLoading"
          @click="agentDashboard.reload({ reset_layout: false })"
        />
        <Button
          v-if="editing && isDashboardModified"
          :label="__('Reset')"
          variant="subtle"
          :icon-left="LucideUndo2"
          :disabled="isLoading"
          @click="onReset"
        />
        <!-- v-if="editing || isDirty" -->
        <Button
          v-if="editing || isDirty"
          :label="__('Save')"
          variant="subtle"
          :disabled="!isDirty"
          :loading="isLoading"
          @click="onSave"
        />
        <Button
          v-if="layout.length > 0 && !editing"
          :label="__('Edit')"
          variant="subtle"
          :iconLeft="LucidePenLine"
          :disabled="isLoading"
          @click="onEdit"
        />
        <Button
          v-if="editing"
          :label="__('Cancel')"
          variant="subtle"
          :disabled="isLoading"
          @click="onCancel"
        />
        <Dropdown
          v-if="chartsDropdown.length > 0"
          :options="chartsDropdown"
          placement="right"
        >
          <Button
            :label="__('New')"
            variant="solid"
            icon-left="plus"
            :disabled="isLoading"
          />
        </Dropdown>
      </div>
    </template>
  </LayoutHeader>
  <div class="h-screen overflow-auto">
    <div
      class="flex flex-col p-1 pt-4 md:p-4 md:px-3 mx-auto max-w-[1500px] w-full grow relative h-full"
    >
      <div class="grow pb-12">
        <div
          v-if="agentDashboard.loading"
          class="flex items-center justify-center h-full"
        >
          <LoadingIndicator class="size-6" />
        </div>
        <div
          v-if="!agentDashboard.loading && layout.length > 0"
          class="text-xl font-semibold text-ink-gray-8 pl-2"
        >
          {{ __('Hey') }}, {{ getUser().full_name }}
        </div>
        <div
          v-if="!agentDashboard.loading && layout.length === 0"
          class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"
        >
          <div class="flex flex-col items-center justify-center gap-1">
            <FeatherIcon name="layout" class="size-12 text-ink-gray-8" />
            <div class="text-xl font-semibold text-ink-gray-8">
              {{ __('No charts added') }}
            </div>
            <div class="text-sm text-ink-gray-5">
              {{ __('Add charts to get started') }}
            </div>
          </div>
        </div>
        <div class="mt-5">
          <GridLayout
            v-if="!agentDashboard.loading && layout.length > 0"
            class="h-fit w-full"
            :class="[editing ? 'mb-[20rem] !select-none' : '']"
            :cols="60"
            :rowHeight="14"
            :disabled="!editing"
            :modelValue="layout.map((item) => item.layout)"
            @update:modelValue="onLayoutUpdate"
          >
            <template #item="{ index }">
              <div
                class="group relative flex h-full w-full p-2 text-ink-gray-8"
              >
                <div
                  class="flex h-full w-full items-center justify-center"
                  :class="
                    editing
                      ? 'pointer-events-none  [&>div:first-child]:rounded [&>div:first-child]:group-hover:ring-2 [&>div:first-child]:group-hover:ring-outline-gray-2'
                      : ''
                  "
                >
                  <ChartItem
                    :item="layout[index]"
                    :index="index"
                    @update:item="layout[index] = $event"
                    @update:selected-statuses="onStatusSelectionChange"
                  />
                </div>
                <div
                  v-if="editing"
                  class="flex absolute right-0 top-0 bg-surface-gray-6 rounded cursor-pointer opacity-0 group-hover:opacity-100"
                >
                  <div
                    class="rounded p-1 hover:bg-surface-gray-5"
                    @click="layout.splice(index, 1)"
                  >
                    <FeatherIcon name="trash-2" class="size-3 text-ink-white" />
                  </div>
                </div>
              </div>
            </template>
          </GridLayout>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import {
  Button,
  createResource,
  Dropdown,
  FeatherIcon,
  GridLayout,
  toast,
} from 'frappe-ui'
import { computed, provide, ref, watch } from 'vue'
import ChartItem from '../components/Home/ChartItem.vue'
import { usersStore } from '@/stores/users'
import LucidePenLine from '~icons/lucide/pen-line'
import LucideRefreshCcw from '~icons/lucide/refresh-ccw'
import LucideUndo2 from '~icons/lucide/undo-2'

const { getUser } = usersStore()
const editing = ref(false)
const layout = ref([])
const oldLayout = ref([])

const isDirty = computed(() => {
  return (
    JSON.stringify(cleanUpLayoutData(layout.value)) !==
    JSON.stringify(cleanUpLayoutData(oldLayout.value))
  )
})

const isLoading = computed(() => {
  return (
    agentDashboard.loading || createDashboard.loading || saveDashboard.loading
  )
})

const agentDashboard = createResource({
  url: 'crm.api.agent_home.agent_home.get_dashboard',
  auto: true,
  transform(data) {
    data.layout = data.layout.map((item) => {
      return {
        ...item,
        layout: {
          ...item.layout,
          i: Math.random().toString(36).substring(2, 9),
        },
      }
    })
    return data
  },
  onSuccess(data) {
    layout.value = data.layout
    oldLayout.value = JSON.parse(JSON.stringify(data.layout))
  },
})

const cleanUpLayoutData = (layout) => {
  return layout.map((item) => {
    const l = item.layout
    const result = {
      chart: item.chart,
      layout: {
        x: l.x,
        y: l.y,
        w: l.w,
        h: l.h,
        minW: l.minW,
        minH: l.minH,
        maxW: l.maxW,
        maxH: l.maxH,
      },
    }
    // Include selected_statuses for funnel conversion charts
    if (item.chart === 'funnel_conversion') {
      result.selected_statuses = item.selected_statuses
    }
    return result
  })
}

const isDashboardModified = computed(() => {
  if (!agentDashboard.data?.default_layout) return false
  const _layout = cleanUpLayoutData(layout.value)
  const defaultLayout = cleanUpLayoutData(
    JSON.parse(agentDashboard.data.default_layout),
  )
  return JSON.stringify(_layout) !== JSON.stringify(defaultLayout)
})

provide('agentDashboard', agentDashboard)
provide('dashboardData', layout)

const createDashboard = createResource({
  url: 'frappe.client.insert',
  makeParams() {
    return {
      doc: {
        doctype: 'CRM Dashboard',
        title: getUser().name,
        layout: JSON.stringify(cleanUpLayoutData(layout.value)),
      },
    }
  },
  onSuccess() {
    toast.success(__('Dashboard saved'))
    agentDashboard.reload()
  },
})

const saveDashboard = createResource({
  url: 'frappe.client.set_value',
  makeParams() {
    return {
      doctype: 'CRM Dashboard',
      name: getUser().name,
      fieldname: 'layout',
      value: JSON.stringify(cleanUpLayoutData(layout.value)),
    }
  },
  onSuccess() {
    toast.success(__('Dashboard saved'))
    oldLayout.value = JSON.parse(JSON.stringify(layout.value))
  },
})

const chartsDropdown = computed(() => {
  const _charts = [
    {
      label: __('Upcoming Activities'),
      chart: 'upcoming_activities',
      onClick: () =>
        addChart('upcoming_activities', {
          w: 60,
          h: 32,
          // minW: 25,
          // minH: 32,
          // maxH: 32,
        }),
    },
    {
      label: __('Funnel Conversion'),
      chart: 'funnel_conversion',
      onClick: () =>
        addChart('funnel_conversion', {
          w: 25,
          h: 31,
          selected_statuses: [],
          // minW: 25,
          // minH: 31,
        }),
    },
    {
      label: __('Top Open Deals'),
      chart: 'top_open_deals',
      onClick: () =>
        addChart('top_open_deals', {
          w: 20,
          h: 19,
          minW: 20,
          minH: 19,
        }),
    },
    {
      label: __('Deals By Stage'),
      chart: 'deals_by_stage',
      onClick: () =>
        addChart('deals_by_stage', {
          w: 20,
          h: 19,
          minW: 20,
          minH: 19,
        }),
    },
    {
      label: __('Expected Closure'),
      chart: 'expected_closure',
      onClick: () =>
        addChart('expected_closure', {
          w: 20,
          h: 19,
          minW: 20,
          minH: 19,
        }),
    },
    {
      label: __('Forecast vs Actual'),
      chart: 'revenue_performance',
      onClick: () =>
        addChart('revenue_performance', {
          w: 30,
          h: 31,
          minW: 30,
          minH: 31,
        }),
    },
  ].filter((chart) => {
    return !layout.value.some((item) => item.chart === chart.chart)
  })
  return _charts
})

const addChart = (chart, config) => {
  if (!editing.value) {
    onEdit()
  }
  layout.value.unshift({
    chart: chart,
    data: {},
    layout: {
      x: 0,
      y: 0,
      w: config.w,
      h: config.h,
      i: Math.random().toString(),
      minW: config.minW,
      minH: config.minH,
      maxW: config.maxW,
      maxH: config.maxH,
    },
    selected_statuses:
      chart === 'funnel_conversion'
        ? config.selected_statuses || []
        : undefined,
  })
}

const onEdit = () => {
  editing.value = true
}

const onSave = () => {
  if (agentDashboard.data?.dashboard_id) {
    saveDashboard.submit().then(() => {
      editing.value = false
    })
  } else {
    createDashboard.submit().then(() => {
      editing.value = false
    })
  }
}

const onCancel = () => {
  layout.value = JSON.parse(JSON.stringify(oldLayout.value))
  editing.value = false
}

const onReset = () => {
  agentDashboard.submit({
    reset_layout: true,
  })
}

const onLayoutUpdate = (newLayout) => {
  layout.value.forEach((item, idx) => {
    item.layout = newLayout[idx]
  })
}

const onStatusSelectionChange = (event) => {
  // Update the selected_statuses for the funnel_conversion chart
  const funnelChart = layout.value.find(
    (item) => item.chart === 'funnel_conversion',
  )
  if (funnelChart) {
    funnelChart.selected_statuses = event.statuses
  }
}
</script>
