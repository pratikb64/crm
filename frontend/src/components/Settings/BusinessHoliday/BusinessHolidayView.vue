<template>
  <SettingsLayoutBase>
    <template #title>
      <div class="flex items-center gap-2">
        <Button
          variant="ghost"
          icon-left="chevron-left"
          :label="slaData.sla_name || __('New Business Holiday')"
          size="md"
          @click="goBack()"
          class="cursor-pointer -ml-4 hover:bg-transparent focus:bg-transparent focus:outline-none focus:ring-0 focus:ring-offset-0 focus-visible:none active:bg-transparent active:outline-none active:ring-0 active:ring-offset-0 active:text-ink-gray-5 font-semibold text-ink-gray-7 text-lg hover:opacity-70 !pr-0 !max-w-96 !justify-start"
        />
        <Badge
          variant="subtle"
          theme="orange"
          size="sm"
          :label="__('Unsaved')"
          v-if="isDirty"
        />
      </div>
    </template>
    <template #header-actions>
      <Button
        :label="__('Save')"
        theme="gray"
        variant="solid"
        @click="saveBusinessHoliday()"
        :disabled="Boolean(!isDirty && step.data)"
        :loading="
          businessHolidayListResource.setValue.loading ||
          renameBusinessHolidayResource.loading ||
          getBusinessHolidayResource.loading
        "
      />
    </template>
    <template #content>
      <div
        v-if="getBusinessHolidayResource.loading"
        class="flex items-center h-full justify-center"
      >
        <LoadingIndicator class="w-4" />
      </div>
      <div v-if="!getBusinessHolidayResource.loading">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <FormControl
              :type="'text'"
              size="sm"
              variant="subtle"
              :placeholder="__('Name')"
              :label="__('Name')"
              v-model="businessHolidayData.business_holiday_name"
              required
              @change="validateBusinessHolidayData('business_holiday_name')"
              maxlength="100"
            />
            <ErrorMessage
              :message="businessHolidayDataErrors.business_holiday_name"
              class="mt-2"
            />
          </div>
        </div>
        <hr class="my-8 border-outline-gray-2" />
        <div>
          <div class="flex flex-col gap-1">
            <span class="text-lg font-semibold text-ink-gray-8">{{
              __('Assignment conditions')
            }}</span>
            <span class="text-p-sm text-ink-gray-6">
              {{ __('Choose which tickets are affected by this policy.') }}
            </span>
          </div>
          <div class="mt-3">
            <div class="flex items-center justify-between">
              <Checkbox
                :label="__('Set as default SLA')"
                :model-value="businessHolidayData.default"
                @update:model-value="toggleDefaultBusinessHoliday"
                class="text-ink-gray-6 text-base font-medium"
              />
              <div
                v-if="
                  isOldBusinessHoliday &&
                  step.data &&
                  !businessHolidayData.default
                "
              >
                <Popover trigger="hover" :hoverDelay="0.25" placement="top-end">
                  <template #target>
                    <div
                      class="text-sm text-ink-gray-6 flex gap-1 cursor-default"
                    >
                      {{ __('Old Conditions') }}
                      <FeatherIcon name="info" class="size-4" />
                    </div>
                  </template>
                  <template #body-main>
                    <div
                      class="text-sm text-ink-gray-6 p-2 bg-white rounded-md max-w-96 text-wrap whitespace-pre-wrap leading-5"
                    >
                      <code>{{ businessHolidayData.condition }}</code>
                    </div>
                  </template>
                </Popover>
              </div>
            </div>
            <div class="mt-5">
              <div
                class="flex flex-col gap-3 items-center text-center text-ink-gray-7 text-sm mb-2 border border-outline-gray-3 rounded-md p-3 py-4"
                v-if="!useNewUI"
              >
                <span class="text-p-sm">
                  Conditions for this SLA were created from
                  <a :href="deskUrl" target="_blank" class="underline">desk</a>
                  which are not compatible with this UI, you will need to
                  recreate the conditions here if you want to manage and add new
                  conditions from this UI.
                </span>
                <Button
                  :label="__('I understand, add conditions')"
                  variant="subtle"
                  theme="gray"
                  @click="useNewUI = true"
                />
              </div>
              <SlaAssignmentConditions
                :conditions="businessHolidayData.condition_json"
                v-if="useNewUI"
              />
            </div>
          </div>
        </div>
        <hr class="my-8 border-outline-gray-2" />
        <div>
          <div class="flex flex-col gap-1">
            <span class="text-lg font-semibold text-ink-gray-8">
              {{ __('Valid from') }}
            </span>
            <span class="text-p-sm text-ink-gray-6">
              {{ __('Choose how long this SLA policy will be active.') }}
            </span>
          </div>
          <div class="mt-3.5 flex gap-5 flex-col md:flex-row">
            <div class="w-full space-y-1.5">
              <FormLabel :label="__('Start date')" for="start_date" />
              <DatePicker
                v-model="businessHolidayData.start_date"
                variant="subtle"
                placeholder="11/01/2025"
                class="w-full"
                id="start_date"
                @change="validateBusinessHolidayData('start_date')"
                :formatter="(date) => getFormattedDate(date)"
              >
                <template #prefix>
                  <LucideCalendar class="size-4" />
                </template>
              </DatePicker>
              <ErrorMessage :message="slaDataErrors.start_date" />
            </div>
            <div class="w-full space-y-1.5">
              <FormLabel :label="__('End date')" for="end_date" />
              <DatePicker
                v-model="businessHolidayData.end_date"
                variant="subtle"
                placeholder="25/12/2025"
                class="w-full"
                id="end_date"
                @change="validateBusinessHolidayData('end_date')"
                :formatter="(date) => getFormattedDate(date)"
              >
                <template #prefix>
                  <LucideCalendar class="size-4" />
                </template>
              </DatePicker>
              <ErrorMessage :message="slaDataErrors.end_date" />
            </div>
          </div>
        </div>
        <hr class="my-8 border-outline-gray-2" />
      </div>
    </template>
  </SettingsLayoutBase>
  <ConfirmDialog
    v-model="showConfirmDialog.show"
    :title="showConfirmDialog.title"
    :message="showConfirmDialog.message"
    :onConfirm="showConfirmDialog.onConfirm"
    :onCancel="() => (showConfirmDialog.show = false)"
  />
</template>

<script setup>
import {
  Badge,
  Button,
  Checkbox,
  ConfirmDialog,
  createResource,
  DatePicker,
  ErrorMessage,
  FeatherIcon,
  FormControl,
  FormLabel,
  LoadingIndicator,
  Popover,
  Select,
  Switch,
  toast,
} from 'frappe-ui'
import { inject, onMounted, onUnmounted, ref, watch } from 'vue'
import SettingsLayoutBase from '../../Layouts/SettingsLayoutBase.vue'
import {
  resetBusinessHolidayDataErrors,
  businessHolidayData,
  businessHolidayDataErrors,
  validateBusinessHolidayData,
} from './utils'
import { disableSettingModalOutsideClick } from '../../../composables/settings'
import { convertToConditions } from '../../../utils'

const isDirty = ref(false)
const initialData = ref(null)
const useNewUI = ref(true)
const isOldBusinessHoliday = ref(false)
const showConfirmDialog = ref({
  show: false,
  title: '',
  message: '',
  onConfirm: () => {},
})

const businessHolidayListResource = inject('businessHolidayListResource')
const step = inject('step')
const updateStep = inject('updateStep')

const deskUrl = `${window.location.origin}/app/crm-holiday-list/${step.value.data?.name}`

const getBusinessHolidayResource = createResource({
  url: 'frappe.client.get',
  params: {
    doctype: 'CRM Holiday List',
    name: step.value.data?.name,
  },
  onSuccess(data) {
    let condition_json
    try {
      condition_json = JSON.parse(data.condition_json || '[]')
    } catch (error) {
      toast.error(
        __(
          'Assignment conditions are invalid or corrupt, recreate the conditions.',
        ),
      )
      condition_json = []
    }

    const newData = {
      ...data,
      enabled: Boolean(data.enabled),
      default: Boolean(data.default),
      rolling_responses: Boolean(data.rolling_responses),
      loading: false,
      condition_json: condition_json,
    }
    businessHolidayData.value = newData
    step.value.data = newData

    initialData.value = JSON.stringify(newData)
    const conditionsAvailable = businessHolidayData.value.condition?.length > 0
    const conditionsJsonAvailable =
      businessHolidayData.value.condition_json?.length > 0
    if (conditionsAvailable && !conditionsJsonAvailable) {
      useNewUI.value = false
      isOldBusinessHoliday.value = true
    } else {
      useNewUI.value = true
      isOldBusinessHoliday.value = false
    }
  },
})

if (step.value.data && step.value.fetchData) {
  getBusinessHolidayResource.submit()
} else {
  disableSettingModalOutsideClick.value = true
}

const goBack = () => {
  const confirmDialogInfo = {
    show: true,
    title: __('Unsaved changes'),
    message: __(
      'Are you sure you want to go back? Unsaved changes will be lost.',
    ),
    onConfirm: goBack,
  }
  if (isDirty.value && !showConfirmDialog.value.show) {
    showConfirmDialog.value = confirmDialogInfo
    return
  }
  if (!step.value.data && !showConfirmDialog.value.show) {
    showConfirmDialog.value = confirmDialogInfo
    return
  }
  // Workaround fix for settings modal not closing after going back
  setTimeout(() => {
    step.value = {
      screen: 'list',
      data: null,
      fetchData: true,
    }
  }, 250)
  showConfirmDialog.value.show = false
}

const saveBusinessHoliday = () => {
  const validationErrors = validateBusinessHolidayData(
    undefined,
    !useNewUI.value,
  )

  if (Object.values(validationErrors).some((error) => error)) {
    toast.error(
      __('Invalid fields, check if all are filled in and values are correct.'),
    )
    return
  }

  if (step.value.data) {
    if (isOldBusinessHoliday.value && useNewUI.value) {
      showConfirmDialog.value = {
        show: true,
        title: __('Confirm overwrite'),
        message: __(
          'Your old conditions will be overwritten. Are you sure you want to save?',
        ),
        onConfirm: () => {
          updateBusinessHoliday()
          showConfirmDialog.value.show = false
        },
      }
      return
    }
    updateBusinessHoliday()
  } else {
    createBusinessHoliday()
  }
}

const createBusinessHoliday = () => {
  businessHolidayListResource.insert.submit(
    {
      ...businessHolidayData.value,
      condition: convertToConditions({
        conditions: businessHolidayData.value.condition_json,
        fieldPrefix: 'doc',
      }),
      condition_json: JSON.stringify(businessHolidayData.value.condition_json),
    },
    {
      onSuccess(data) {
        toast.success(__('Holiday list created'))
        updateStep('view', data, true)
        getBusinessHolidayResource.submit({
          doctype: 'CRM Holiday List',
          name: data.name,
        })
      },
      onError(err) {
        const message = err?.messages?.[0]
        toast.error(
          message || __('Some error occurred while creating SLA policy'),
        )
      },
    },
  )
}

const renameBusinessHolidayResource = createResource({
  url: 'frappe.client.rename_doc',
  makeParams() {
    return {
      doctype: 'CRM Holiday List',
      old_name: step.value.data.name,
      new_name: businessHolidayData.value.business_holiday_name,
    }
  },
})

const updateBusinessHoliday = async () => {
  await businessHolidayListResource.setValue.submit(
    {
      ...businessHolidayData.value,
      name: step.value.data.name,
      condition: useNewUI.value
        ? convertToConditions({
            conditions: businessHolidayData.value.condition_json,
            fieldPrefix: 'doc',
          })
        : businessHolidayData.value.condition,
      condition_json: useNewUI.value
        ? JSON.stringify(businessHolidayData.value.condition_json)
        : null,
    },
    {
      onError(err) {
        const message = err?.messages?.[0]
        toast.error(
          message || __('Some error occurred while updating SLA policy'),
        )
      },
    },
  )

  if (
    businessHolidayData.value.name !==
    businessHolidayData.value.business_holiday_name
  ) {
    await renameBusinessHolidayResource.submit().catch(async (er) => {
      const error =
        er?.messages?.[0] ||
        __('Some error occurred while renaming business holiday')
      toast.error(error)
      // Reset assignment rule to previous state
      await getBusinessHolidayResource.reload()
      isLoading.value = false
    })

    getBusinessHolidayResource.submit({
      doctype: 'CRM Holiday List',
      name: businessHolidayData.value.business_holiday_name,
    })
  } else {
    await getBusinessHolidayResource.reload()
  }

  toast.success(__('Business holiday updated'))
  businessHolidayListResource.reload()
}

watch(
  businessHolidayData,
  (newVal) => {
    if (!initialData.value) return
    isDirty.value = JSON.stringify(newVal) != initialData.value
    if (isDirty.value) {
      disableSettingModalOutsideClick.value = true
    } else {
      disableSettingModalOutsideClick.value = false
    }
  },
  { deep: true },
)

const beforeUnloadHandler = (event) => {
  if (!isDirty.value) return
  event.preventDefault()
  event.returnValue = true
}

onMounted(() => {
  addEventListener('beforeunload', beforeUnloadHandler)
})

onUnmounted(() => {
  removeEventListener('beforeunload', beforeUnloadHandler)
  resetBusinessHolidayDataErrors()
  disableSettingModalOutsideClick.value = false
})
</script>
