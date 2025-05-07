<template>
  <CampaignLayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs">
        <template #prefix="{ item }">
          <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
        </template>
      </Breadcrumbs>
    </template>
    <template #right-header>
      <Button
        variant="solid"
        :label="__('Create')"
        :loading="isAudienceCreating"
        @click="createNewAudience"
      >
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </template>
  </CampaignLayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="audiences"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="CRM Audience"
  />
  <AudiencesListView
    ref="audiencesListView"
    v-if="audiences.data && audiences.data.total_count > 0"
    v-model="audiences.data.page_length_count"
    v-model:list="audiences"
    :rows="rows"
    :columns="audiences.data.columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: audiences.data.row_count,
      totalCount: audiences.data.total_count,
    }"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @applyFilter="(data) => viewControls.applyFilter(data)"
    @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
    @likeDoc="(data) => viewControls.likeDoc(data)"
    @selectionsChanged="
      (selections) => viewControls.updateSelections(selections)
    "
  />
  <div
    v-if="audiences.data && audiences.data.total_count == 0"
    class="flex h-full items-center justify-center"
  >
    <div
      class="flex flex-col items-center gap-3 text-xl font-medium text-ink-gray-4"
    >
      <LeadsIcon class="h-10 w-10" />
      <span>{{ __('No {0} Found', [__('Audiences')]) }}</span>
      <Button
        :label="__('Create')"
        :loading="isAudienceCreating"
        @click="createNewAudience"
      >
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </div>
  </div>
</template>

<script setup>
import Icon from '@/components/Icon.vue'
import CampaignLayoutHeader from '@/components/CampaignLayoutHeader.vue'
import {
  errorMessage as _errorMessage,
  setupCustomizations,
  createToast,
} from '@/utils'
import { Breadcrumbs, FormControl, Button } from 'frappe-ui'
import { ref, computed } from 'vue'
import AudiencesListView from '@/components/ListViews/AudiencesListView.vue'
import { createResource } from 'frappe-ui'
import CustomActions from '@/components/CustomActions.vue'
import LeadsIcon from '@/components/Icons/LeadsIcon.vue'
import ViewControls from '@/components/ViewControls.vue'
import { getMeta } from '@/stores/meta'
import { usersStore } from '@/stores/users'
import { statusesStore } from '@/stores/statuses'
import { useRouter } from 'vue-router'

const { getFormattedPercent, getFormattedFloat, getFormattedCurrency } =
  getMeta('CRM Audience')
const { getUser } = usersStore()
const { getLeadStatus } = statusesStore()
const router = useRouter()

const audiences = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

const list = createResource({
  url: 'crm.api.audience.get_audiences',
  params: {
    filters: [],
    limit: 20,
  },
  auto: false,
})

const rows = computed(() => {
  if (!audiences.value?.data?.data) return []
  return parseRows(audiences.value?.data.data, audiences.value.data.columns)
})

function parseRows(rows, columns = []) {
  let view_type = audiences.value.data.view_type
  let key = view_type === 'kanban' ? 'fieldname' : 'key'
  let type = view_type === 'kanban' ? 'fieldtype' : 'type'

  return rows.map((audience) => {
    let _rows = {}
    audiences.value?.data.rows.forEach((row) => {
      _rows[row] = audience[row]

      let fieldType = columns?.find((col) => (col[key] || col.value) == row)?.[
        type
      ]

      if (
        fieldType &&
        ['Date', 'Datetime'].includes(fieldType) &&
        !['modified', 'creation'].includes(row)
      ) {
        _rows[row] = formatDate(
          audience[row],
          '',
          true,
          fieldType == 'Datetime',
        )
      }

      if (fieldType && fieldType == 'Float') {
        _rows[row] = getFormattedFloat(row, audience)
      }

      if (row == 'audience_name') {
        _rows[row] = audience.audience_name
      } else if (['modified', 'creation'].includes(row)) {
        _rows[row] = {
          label: formatDate(audience[row]),
          timeAgo: __(timeAgo(audience[row])),
        }
      }
    })
    return _rows
  })
}

function createNewAudience() {
  router.push({ name: 'Create Audience' })
}

const breadcrumbs = computed(() => {
  let items = [{ label: __('Audiences'), route: { name: 'Audiences' } }]
  return items
})

const isAudienceCreating = ref(false)
</script>
