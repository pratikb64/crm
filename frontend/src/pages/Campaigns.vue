<template>
  <CampaignLayoutHeader>
    <template #left-header>
      <Breadcrumbs
        :items="[
          {
            label: 'Campaigns',
            route: { name: 'Campaigns' },
          },
        ]"
      >
        <template #prefix="{ item }">
          <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
        </template>
      </Breadcrumbs>
    </template>
    <template #right-header>
      <CustomActions
        v-if="campaignsListView?.customListActions"
        :actions="campaignsListView.customListActions"
      />
      <Button
        variant="solid"
        :label="__('Create')"
        :loading="isCampaignCreating"
        @click="createNewCampaign"
      >
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </template>
  </CampaignLayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="campaigns"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="CRM Campaign"
  />
  <CampaignsListView
    ref="campaignsListView"
    v-if="campaigns.data && campaigns.data.total_count > 0"
    v-model="campaigns.data.page_length_count"
    v-model:list="campaigns"
    :rows="rows"
    :columns="campaigns.data.columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: campaigns.data.row_count,
      totalCount: campaigns.data.total_count,
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
    v-if="campaigns.data && campaigns.data.total_count == 0"
    class="flex h-full items-center justify-center"
  >
    <div
      class="flex flex-col items-center gap-3 text-xl font-medium text-ink-gray-4"
    >
      <LeadsIcon class="h-10 w-10" />
      <span>{{ __('No {0} Found', [__('Campaigns')]) }}</span>
      <Button
        :label="__('Create')"
        :loading="isCampaignCreating"
        @click="createNewCampaign"
      >
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </div>
  </div>
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import MultipleAvatar from '@/components/MultipleAvatar.vue'
import CustomActions from '@/components/CustomActions.vue'
import EmailAtIcon from '@/components/Icons/EmailAtIcon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import LeadsIcon from '@/components/Icons/LeadsIcon.vue'
import CampaignLayoutHeader from '@/components/CampaignLayoutHeader.vue'
import ViewControls from '@/components/ViewControls.vue'
import { getMeta } from '@/stores/meta'
import { globalStore } from '@/stores/global'
import { usersStore } from '@/stores/users'
import { statusesStore } from '@/stores/statuses'
import { callEnabled } from '@/composables/settings'
import { formatDate, timeAgo, website, formatTime } from '@/utils'
import { Breadcrumbs, createResource } from 'frappe-ui'
import { useRouter } from 'vue-router'
import { ref, computed, reactive, h, watch } from 'vue'
import CampaignsListView from '@/components/ListViews/CampaignsListView.vue'
import { capture } from '@/telemetry'

const { getFormattedPercent, getFormattedFloat, getFormattedCurrency } =
  getMeta('CRM Campaign')
const { getUser } = usersStore()
const { getLeadStatus } = statusesStore()
const router = useRouter()

const campaignsListView = ref(null)
const isCampaignCreating = ref(false)

// leads data is loaded in the ViewControls component
const campaigns = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

watch(campaigns, () => {
  console.log('campaigns', campaigns.value)
  console.log('campaignsListView', campaignsListView.value)
})

// Rows
const rows = computed(() => {
  if (!campaigns.value?.data?.data) return []
  return parseRows(campaigns.value?.data.data, campaigns.value.data.columns)
})

function parseRows(rows, columns = []) {
  let view_type = campaigns.value.data.view_type
  let key = view_type === 'kanban' ? 'fieldname' : 'key'
  let type = view_type === 'kanban' ? 'fieldtype' : 'type'

  return rows.map((campaign) => {
    let _rows = {}
    campaigns.value?.data.rows.forEach((row) => {
      _rows[row] = campaign[row]

      let fieldType = columns?.find((col) => (col[key] || col.value) == row)?.[
        type
      ]

      if (
        fieldType &&
        ['Date', 'Datetime'].includes(fieldType) &&
        !['modified', 'creation'].includes(row)
      ) {
        _rows[row] = formatDate(
          campaign[row],
          '',
          true,
          fieldType == 'Datetime',
        )
      }

      if (fieldType && fieldType == 'Float') {
        _rows[row] = getFormattedFloat(row, campaign)
      }

      if (row == 'campaign_name') {
        _rows[row] = campaign.campaign_name
      } else if (['modified', 'creation'].includes(row)) {
        _rows[row] = {
          label: formatDate(campaign[row]),
          timeAgo: __(timeAgo(campaign[row])),
        }
      }
    })
    return _rows
  })
}

function createNewCampaign() {
  router.push({ name: 'Create Campaign' })
}
</script>
