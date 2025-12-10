<template>
  <SettingsLayoutBase>
    <template #title>
      <div class="flex items-center gap-2">
        <Button
          variant="ghost"
          icon-left="chevron-left"
          :label="slaData.sla_name || __('New SLA Policy')"
          size="md"
          @click="goBack()"
          class="cursor-pointer -ml-4 hover:bg-transparent focus:bg-transparent focus:outline-none focus:ring-0 focus:ring-offset-0 focus-visible:none active:bg-transparent active:outline-none active:ring-0 active:ring-offset-0 active:text-ink-gray-5 font-semibold text-ink-gray-7 text-lg hover:opacity-70 !pr-0"
        />
        <Badge
          :variant="'subtle'"
          :theme="'orange'"
          size="sm"
          :label="__('Unsaved')"
          v-if="isDirty"
        />
      </div>
    </template>
    <template #header-actions>
      <div class="flex gap-4 items-center">
        <div
          class="flex items-center justify-between gap-2 cursor-pointer"
          @click="toggleEnabled"
        >
          <Switch size="sm" v-model="slaData.enabled" />
          <span class="text-sm text-ink-gray-7 font-medium">
            {{ __('Enabled') }}
          </span>
        </div>
        <Button
          :label="__('Save')"
          theme="gray"
          variant="solid"
          @click="saveSla()"
          :disabled="Boolean(!isDirty && step.data)"
          :loading="slaData.loading || slaPolicyListResource.setValue.loading"
        />
      </div>
    </template>
    <template #content> </template>
  </SettingsLayoutBase>
</template>

<script setup>
import { Badge, Button, Switch } from 'frappe-ui'
import { inject, ref } from 'vue'
import SettingsLayoutBase from '../../Layouts/SettingsLayoutBase.vue'

const isDirty = ref(false)
const initialData = ref(null)
const useNewUI = ref(true)
const isOldSla = ref(false)

const slaPolicyListResource = inject('slaPolicyListResource')
const step = inject('step')
const updateStep = inject('updateStep')

const deskUrl = `${window.location.origin}/app/hd-service-level-agreement/${step.value.data?.name}`

const slaData = ref({
  name: 'asd',
  sla_name: '',
  apply_on: '',
  enabled: true,
  default: false,
  rolling_responses: true,
  start_date: '',
  end_date: '',
  condition: [],
  condition_json: [],
  priorities: [],
  holiday_list: 'Default',
  working_hours: [],
})

const saveSla = () => {}
</script>
