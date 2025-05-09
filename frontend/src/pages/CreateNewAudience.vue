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
  <div class="px-2 sm:px-5">
    <div class="mt-4 items-center gap-6">
      <div class="text-sm text-gray-800">
        {{ __('Create list by filtering from leads, contacts or deals') }}
      </div>
      <div class="mt-4 flex gap-4">
        <FormControl
          :label="__('Source')"
          type="select"
          :options="[
            {
              label: 'Leads',
              value: 'CRM Lead',
            },
            {
              label: 'Contacts',
              value: 'CRM Contact',
            },
            {
              label: 'Deals',
              value: 'CRM Deal',
            },
            {
              label: 'Import',
              value: 'Import',
            },
          ]"
          v-model="audience.source"
        />
        <Filter v-if="audience.source != 'Import'" class="mt-5" label="__('Filter')" v-model="list" :doctype="audience.source" @update="updateFilter" />
      </div>
    </div>
  </div>
</template>

<script setup>
import Icon from '@/components/Icon.vue'
import { ref, computed, watch } from 'vue'
import CampaignLayoutHeader from '@/components/CampaignLayoutHeader.vue'
import { Breadcrumbs, Button,FormControl } from 'frappe-ui'
import Filter from '@/components/Filter.vue'

const audience = ref({
  source: 'CRM Lead',
})
watch(audience.source, () => {
  console.log('audience.value', audience.value)
  console.log('audience.value.source', audience.value.source)
})
const isAudienceCreating = ref(false)
const filterLength = ref(0)
const list = defineModel()
const breadcrumbs = computed(() => {
  let items = [
    { label: __('Audiences'), route: { name: 'Audiences' } },
    { label: __('New Audience') },
  ]
  return items
})
const viewUpdated = ref(false)
const defaultParams = ref('')
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

function getParams() {

  return {
    doctype: audience.source,
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
function updateFilter(filters) {
  viewUpdated.value = true
  // if (!defaultParams.value) {
  //   defaultParams.value = getParams()
  // }
  // list.value.params = defaultParams.value
  // list.value.params.filters = filters
  view.value.filters = filters
  filterLength.value = Object.keys(filters).length
  list.value.reload()
}
</script>
