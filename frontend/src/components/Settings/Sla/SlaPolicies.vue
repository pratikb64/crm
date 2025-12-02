<template>
  <SettingsLayoutBase
    title="SLA Policies"
    description="Manage your service level agreement policies"
  >
    <template #header-actions>
      <Button
        label="New"
        variant="solid"
        icon-left="plus"
        @click="createNewSlaPolicy"
      />
    </template>
    <template #content>
      <div
        v-if="slaPolicyList.list.loading && !slaPolicyList.list.data"
        class="flex items-center justify-center mt-12"
      >
        <LoadingIndicator class="w-4" />
      </div>
      <div v-else class="h-full">
        <div
          v-if="!slaPolicyList.list.loading && !slaPolicyList.list.data?.length"
          class="flex flex-col items-center justify-center gap-4 h-full"
        >
          <div
            class="p-4 size-14.5 rounded-full bg-surface-gray-1 flex justify-center items-center"
          >
            <ShieldCheck class="size-6 text-ink-gray-6" />
          </div>
          <div class="flex flex-col items-center gap-1">
            <div class="text-base font-medium text-ink-gray-6">
              {{ __('No SLA found') }}
            </div>
            <div class="text-p-sm text-ink-gray-5 max-w-60 text-center">
              {{ __('Add one to get started.') }}
            </div>
          </div>
          <Button
            :label="__('New')"
            variant="outline"
            icon-left="plus"
            @click="goToNew()"
          />
        </div>
        <div v-else class="-ml-2">
          <div
            class="grid grid-cols-6 items-center gap-3 text-sm text-gray-600 ml-2"
          >
            <div class="col-span-5">
              {{ __('Policy Name') }}
            </div>
            <div class="col-span-1">{{ __('Enabled') }}</div>
          </div>
          <hr class="mt-2 mx-2" />
          <div v-for="(sla, index) in slaPolicyList.list.data" :key="sla.name">
            <div
              class="grid grid-cols-6 items-center gap-4 cursor-pointer hover:bg-gray-50 rounded"
            >
              <div
                @click="updateStep('view', sla, true)"
                class="w-full pl-2 col-span-5 flex flex-col justify-center h-14"
              >
                <div
                  class="text-base text-ink-gray-7 font-medium flex items-center gap-2"
                >
                  {{ sla.name }}
                  <Badge v-if="sla.default_sla" color="gray" size="sm"
                    >Default</Badge
                  >
                </div>
                <div
                  v-if="sla.description && sla.description.length > 0"
                  class="text-sm w-full text-ink-gray-5 mt-1 truncate"
                >
                  {{ sla.description }}
                </div>
              </div>
              <div class="flex justify-between items-center w-full pr-2">
                <div>
                  <Switch
                    size="sm"
                    :modelValue="sla.enabled"
                    @update:modelValue="onToggle"
                  />
                </div>
                <div>
                  <Dropdown placement="right" :options="dropdownOptions">
                    <Button
                      icon="more-horizontal"
                      variant="ghost"
                      @click="isConfirmingDelete = false"
                    />
                  </Dropdown>
                </div>
              </div>
            </div>
            <hr
              v-if="index !== slaPolicyList.list.data.length - 1"
              class="mx-2"
            />
          </div>
        </div>
      </div>
    </template>
  </SettingsLayoutBase>
  <Dialog
    :options="{ title: __('Duplicate SLA Policy') }"
    v-model="duplicateDialog.show"
  >
    <template #body-content>
      <div class="flex flex-col gap-4">
        <FormControl
          :label="__('New SLA Policy Name')"
          type="text"
          v-model="duplicateDialog.name"
        />
      </div>
    </template>
    <template #actions>
      <div class="flex gap-2 justify-end">
        <Button
          variant="subtle"
          :label="__('Close')"
          @click="duplicateDialog.show = false"
        />
        <Button variant="solid" :label="__('Duplicate')" @click="duplicate()" />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import {
  Badge,
  Button,
  Dialog,
  Dropdown,
  FormControl,
  LoadingIndicator,
  Switch,
  toast,
} from 'frappe-ui'
import SettingsLayoutBase from '../../Layouts/SettingsLayoutBase.vue'
import { inject, ref } from 'vue'
import ShieldCheck from '~icons/lucide/shield-check'
import { ConfirmDelete } from '../../../utils'

const slaPolicyList = inject('slaPolicyListResource')
console.log('slaPolicyList', slaPolicyList)
const updateStep = inject('updateStep')

const goToNew = () => {
  updateStep('view', null, true)
}

function createNewSlaPolicy() {}

const duplicateDialog = ref({
  show: false,
  name: '',
})

const props = defineProps({
  data: {
    type: Object,
    required: true,
  },
})

const isConfirmingDelete = ref(false)

const dropdownOptions = [
  {
    label: __('Duplicate'),
    onClick: () => {
      duplicateDialog.value = {
        show: true,
        name: props.data.name + ' (Copy)',
      }
    },
    icon: 'copy',
  },
  ...ConfirmDelete({
    onConfirmDelete: () => deleteSla(),
    isConfirmingDelete,
  }),
]

const duplicate = () => {
  createResource({
    url: 'helpdesk.api.sla.duplicate_sla',
    params: {
      docname: props.data.name,
      new_name: duplicateDialog.value.name,
    },
    onSuccess: (data) => {
      slaPolicyList.reload()
      toast.success(__('SLA policy duplicated'))
      duplicateDialog.value = {
        show: false,
        name: '',
      }
      setTimeout(() => {
        updateStep('view', data, true)
      }, 250)
    },
    auto: true,
  })
}

const deleteSla = () => {
  if (!isConfirmingDelete.value) {
    isConfirmingDelete.value = true
    return
  }

  slaPolicyList.delete.submit(props.data.name, {
    onSuccess: () => {
      toast.success(__('SLA policy deleted'))
    },
  })
}

const onToggle = () => {
  if (props.data.default_sla) {
    toast.error(__('SLA set as default cannot be disabled'))
    return
  }
  slaPolicyList.setValue.submit(
    {
      name: props.data.name,
      enabled: !props.data.enabled,
    },
    {
      onSuccess: () => {
        toast.success(__('SLA policy status updated'))
      },
    },
  )
}
</script>
