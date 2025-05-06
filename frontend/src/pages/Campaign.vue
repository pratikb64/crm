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
        :label="__('Delete')"
        @click="() => deleteCampaign(props.campaignId)"
      />
      <Button :label="__('Save')" variant="solid" />
    </template>
  </CampaignLayoutHeader>
  <div class="mt-3 gap-4 px-2 sm:px-5">
    <div class="text-lg font-medium">{{ __('Details') }}</div>
    <div class="mt-4 flex gap-4">
      <FormControl
        :type="'text'"
        :ref_for="true"
        size="sm"
        variant="subtle"
        :placeholder="__('Name')"
        :disabled="false"
        :label="__('Name')"
        class="w-full"
      />
    </div>
  </div>
  <hr class="my-4" />
  <div class="px-2 sm:px-5">
    <div class="flex items-center gap-6">
      <div class="text-lg font-medium">{{ __('Audience') }}</div>
      <Filter v-model="list" :doctype="'CRM Lead'" @update="updateFilter" />
    </div>
    <div class="mt-4">
      <AudienceListView
        v-if="filterLength > 0 && list.data?.data?.length > 0"
        :columns="[
          {
            label: 'Name',
            type: 'Data',
            key: 'lead_name',
            width: '12rem',
          },
          {
            label: 'Email',
            type: 'Data',
            key: 'email',
            width: '12rem',
          },
          {
            label: 'Mobile No',
            type: 'Data',
            key: 'mobile_no',
            width: '11rem',
          },
        ]"
        :rows="list.data?.data"
        @update:selections="
          (selections) => emit('selectionsChanged', selections)
        "
      />
      <div
        v-if="filterLength == 0 || list.data?.data?.length == 0"
        class="flex h-52 items-center justify-center"
      >
        <div
          class="flex flex-col items-center gap-3 text-xl font-medium text-ink-gray-4"
        >
          <LeadsIcon class="h-8 w-8" />
          <span>{{ __('Change audience filter') }}</span>
        </div>
      </div>
    </div>
  </div>
  <hr class="my-4" />
  <div class="px-2 sm:px-5">
    <div class="text-lg font-medium">{{ __('Activity list') }}</div>
  </div>
  <ErrorPage
    v-if="errorTitle"
    :errorTitle="errorTitle"
    :errorMessage="errorMessage"
  />
</template>
<script setup>
import Icon from '@/components/Icon.vue'
import CampaignLayoutHeader from '@/components/CampaignLayoutHeader.vue'
import {
  errorMessage as _errorMessage,
  setupCustomizations,
  createToast,
} from '@/utils'
import {
  Breadcrumbs,
  FormControl,
  Button,
  createResource,
  call,
} from 'frappe-ui'
import { computed, ref, watch, onMounted } from 'vue'
import Filter from '@/components/Filter.vue'
import { useRoute, useRouter } from 'vue-router'
import { viewsStore } from '@/stores/views'
import AudienceListView from '@/components/ListViews/AudienceListView.vue'
import { globalStore } from '@/stores/global'
import { getMeta } from '@/stores/meta'
import ErrorPage from '@/components/ErrorPage.vue'

const props = defineProps({
  campaignId: {
    type: String,
    required: true,
  },
})
const list = defineModel()
const view = ref({
  name: '',
  label: '',
  type: 'list',
  icon: '',
  filters: {},
  order_by: 'modified desc',
  column_field: 'status',
  title_field: '',
  kanban_columns: '',
  kanban_fields: '',
  columns: '',
  rows: '',
  load_default_columns: false,
  pinned: false,
  public: false,
})
const { reload: reloadView, getDefaultView, getView } = viewsStore()
const { $dialog, $socket, makeCall } = globalStore()
const errorTitle = ref('')
const errorMessage = ref('')
const filterLength = ref(0)
const route = useRoute()
const router = useRouter()
const { doctypeMeta } = getMeta('CRM Campaign')

const campaign = createResource({
  url: 'crm.fcrm.doctype.crm_campaign.api.get_campaign',
  params: { name: props.campaignId },
  cache: ['campaign', props.campaignId],
  onSuccess: (data) => {
    errorTitle.value = ''
    errorMessage.value = ''
    setupCustomizations(campaign, {
      doc: data,
      $dialog,
      $socket,
      router,
      // updateField,
      createToast,
      deleteDoc: deleteCampaign,
      resource: { campaign },
      call,
    })
  },
  onError: (err) => {
    if (err.messages?.[0]) {
      errorTitle.value = __('Not permitted')
      errorMessage.value = __(err.messages?.[0])
    } else {
      router.push({ name: 'Campaigns' })
    }
  },
})

onMounted(() => {
  if (campaign.data) return
  campaign.fetch()
})

const title = computed(() => {
  let t = doctypeMeta['CRM Campaign']?.title_field || 'name'
  return campaign.data?.[t] || props.campaignId
})
const pageLength = computed(() => list.value?.data?.page_length)
const pageLengthCount = computed(() => list.value?.data?.page_length_count)

list.value = createResource({
  url: 'crm.api.doc.get_data',
  params: getParams(),
  cache: ['CRM Lead', route.query.view, route.params.viewType],
  onSuccess(data) {
    let cv = getView(route.query.view, route.params.viewType, 'CRM Lead')
    let params = list.value.params ? list.value.params : getParams()
    defaultParams.value = {
      doctype: 'CRM Lead',
      filters: params.filters,
      order_by: params.order_by,
      default_filters: props.filters,
      view: {
        custom_view_name: cv?.name || '',
        view_type: cv?.type || route.params.viewType || 'list',
        group_by_field: params?.view?.group_by_field || 'owner',
      },
      column_field: data.column_field,
      title_field: data.title_field,
      kanban_columns: data.kanban_columns,
      kanban_fields: data.kanban_fields,
      columns: data.columns,
      rows: data.rows,
      page_length: params.page_length,
      page_length_count: params.page_length_count,
    }
  },
})

async function deleteCampaign(name) {
  $dialog({
    title: __('Delete Campaign'),
    message: __('Are you sure you want to delete this campaign?'),
    actions: [
      {
        label: __('Delete'),
        theme: 'red',
        variant: 'solid',
        async onClick(close) {
          await call('frappe.client.delete', {
            doctype: 'CRM Campaign',
            name,
          })
          close()
          router.push({ name: 'Campaigns' })
        },
      },
    ],
  })
}

const breadcrumbs = computed(() => {
  let items = [{ label: __('Campaigns'), route: { name: 'Campaigns' } }]

  items.push({
    label: title.value,
    route: {
      name: 'Campaign',
      params: { campaignId: route.params.campaignId },
    },
  })
  return items
})

function getParams() {
  let _view = getView(route.query.view, route.params.viewType, 'CRM Lead')
  const view_name = _view?.name || ''
  const view_type = _view?.type || route.params.viewType || 'list'
  const filters = (_view?.filters && JSON.parse(_view.filters)) || {}
  const order_by = _view?.order_by || 'modified desc'
  const group_by_field = _view?.group_by_field || 'owner'
  const columns = _view?.columns || ''
  const rows = _view?.rows || ''
  const column_field = _view?.column_field || 'status'
  const title_field = _view?.title_field || ''
  const kanban_columns = _view?.kanban_columns || ''
  const kanban_fields = _view?.kanban_fields || ''

  view.value = {
    name: view_name,
    label: _view?.label,
    type: view_type,
    icon: _view?.icon || '',
    filters: filters,
    order_by: order_by,
    group_by_field: group_by_field,
    column_field: column_field,
    title_field: title_field,
    kanban_columns: kanban_columns,
    kanban_fields: kanban_fields,
    columns: columns,
    rows: rows,
    route_name: _view?.route_name || route.name,
    load_default_columns: _view?.row || true,
    pinned: _view?.pinned || false,
    public: _view?.public || false,
  }

  return {
    doctype: 'CRM Lead',
    filters: filters,
    order_by: order_by,
    default_filters: props.filters,
    view: {
      custom_view_name: view_name,
      view_type: view_type,
      group_by_field: group_by_field,
    },
    column_field: column_field,
    title_field: title_field,
    kanban_columns: kanban_columns,
    kanban_fields: kanban_fields,
    columns: columns,
    rows: rows,
    page_length: pageLength.value,
    page_length_count: pageLengthCount.value,
  }
}
const viewUpdated = ref(false)
const defaultParams = ref('')

function updateFilter(filters) {
  viewUpdated.value = true
  if (!defaultParams.value) {
    defaultParams.value = getParams()
  }
  list.value.params = defaultParams.value
  list.value.params.filters = filters
  view.value.filters = filters
  filterLength.value = Object.keys(filters).length
  list.value.reload()
}
</script>
