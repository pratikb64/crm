<template>
  <SettingsLayoutBase>
    <template #title>
      <div class="flex items-center gap-2">
        <Button
          variant="ghost"
          icon-left="chevron-left"
          :label="
            holidayListData.business_holiday_name || __('New Business Holiday')
          "
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
          holidayListResource.setValue.loading ||
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
        <div class="flex items-center gap-2 mt-2">
          <span class="text-sm">
            There are in total
            <b>{{ holidayListData.holidays.length }}</b> holidays in this
            list</span
          >
        </div>
        <hr class="mt-2 mb-8 border-outline-gray-2" />
        <div class="space-y-2">
          <FormControl
            :type="'text'"
            size="sm"
            variant="subtle"
            :placeholder="__('Name')"
            :label="__('Name')"
            v-model="holidayListData.business_holiday_name"
            required
            @change="validateHolidayListData('business_holiday_name')"
            maxlength="100"
          />
          <ErrorMessage
            :message="holidayListDataErrors.business_holiday_name"
          />
        </div>
        <hr class="my-8 border-outline-gray-2" />
        <div>
          <div class="flex flex-col gap-1">
            <span class="text-lg font-semibold text-ink-gray-8">{{
              __('Valid from')
            }}</span>
            <span class="text-p-sm text-ink-gray-6">
              {{ __('Choose the duration of this holiday list.') }}
            </span>
          </div>
          <div class="mt-3.5 flex gap-5 flex-col md:flex-row">
            <div class="w-full space-y-1.5">
              <FormLabel :label="__('From date')" for="from_date" required />
              <DatePicker
                v-model="holidayListData.from_date"
                variant="subtle"
                placeholder="11/01/2025"
                class="w-full"
                id="from_date"
                :formatter="(date) => getFormattedDate(date)"
                :debounce="300"
                @update:model-value="updateDuration('from_date')"
              >
                <template #prefix>
                  <LucideCalendar class="size-4" />
                </template>
              </DatePicker>
              <ErrorMessage
                :message="
                  holidayListDataErrors.from_date ||
                  holidayListDataErrors.dateRange
                "
              />
            </div>
            <div class="w-full space-y-1.5">
              <FormLabel :label="__('To date')" for="to_date" required />
              <DatePicker
                v-model="holidayListData.to_date"
                variant="subtle"
                placeholder="25/12/2025"
                class="w-full"
                id="to_date"
                :formatter="(date) => getFormattedDate(date)"
                :debounce="300"
                @update:model-value="updateDuration('to_date')"
              >
                <template #prefix>
                  <LucideCalendar class="size-4" />
                </template>
              </DatePicker>
              <ErrorMessage :message="holidayListDataErrors.to_date" />
            </div>
          </div>
        </div>
        <hr class="my-8 border-outline-gray-2" />
        <div>
          <div class="flex flex-col gap-1">
            <div class="text-lg font-semibold text-ink-gray-8">
              {{ __('Recurring holidays') }}
            </div>
            <div class="text-p-sm text-ink-gray-6">
              {{ __('Add recurring holidays such as weekends.') }}
            </div>
          </div>
          <div class="mt-5">
            <RecurringHolidaysList
              :holidayData="holidayListData"
              :holidays="holidayListData.holidays"
            />
          </div>
        </div>
        <hr class="my-8 border-outline-gray-2" />
        <div>
          <div class="flex justify-between items-center">
            <div class="flex justify-between flex-col gap-1">
              <span class="text-lg font-semibold text-ink-gray-8">
                {{ __('Holidays') }}
              </span>
              <div class="text-p-sm text-ink-gray-6">
                {{
                  __(
                    'Add holidays here to make sure they’re excluded from SLA calculations.',
                  )
                }}
              </div>
            </div>
            <TabButtons
              :buttons="[
                {
                  value: 'calendar',
                  icon: 'calendar',
                },
                {
                  value: 'list',
                  icon: 'list',
                },
              ]"
              v-model="holidayListView"
            />
          </div>
          <div class="mt-5">
            <HolidaysTableView v-if="holidayListView === 'list'" />
            <HolidaysCalendarView v-else />
          </div>
          <div class="mt-2.5 flex justify-between items-center">
            <Button
              variant="subtle"
              :label="__('Add Holiday')"
              @click="dialog.show = true"
              icon-left="plus"
            />
            <!-- Indicators -->
            <div class="flex gap-4" v-if="holidayListView === 'calendar'">
              <div class="gap-1 flex items-center">
                <span class="bg-yellow-100 size-4 rounded-sm" />
                <span class="text-sm text-ink-gray-6">{{
                  __('Holidays')
                }}</span>
              </div>
              <div class="gap-1 flex items-center">
                <span class="bg-gray-100 size-4 rounded-sm" />
                <span class="text-sm text-ink-gray-6">{{
                  __('Recurring holidays')
                }}</span>
              </div>
            </div>
          </div>
        </div>
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
  ConfirmDialog,
  createResource,
  DatePicker,
  ErrorMessage,
  FormControl,
  FormLabel,
  LoadingIndicator,
  toast,
} from 'frappe-ui'
import { inject, onMounted, onUnmounted, ref, watch } from 'vue'
import SettingsLayoutBase from '../../Layouts/SettingsLayoutBase.vue'
import {
  resetHolidayListErrors,
  holidayListData,
  holidayListDataErrors,
  validateHolidayListData,
  updateWeeklyOffDates,
} from './utils'
import { disableSettingModalOutsideClick } from '../../../composables/settings'
import { convertToConditions } from '../../../utils'
import RecurringHolidaysList from './RecurringHolidaysList.vue'

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
const dialog = ref({
  show: false,
  holiday_date: new Date(),
  description: '',
  editing: null,
})
const holidayListView = ref('calendar')
const holidayListResource = inject('holidayListResource')
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
    holidayListData.value = newData
    step.value.data = newData

    initialData.value = JSON.stringify(newData)
    const conditionsAvailable = holidayListData.value.condition?.length > 0
    const conditionsJsonAvailable =
      holidayListData.value.condition_json?.length > 0
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
  const validationErrors = validateHolidayListData(undefined, !useNewUI.value)

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
  holidayListResource.insert.submit(
    {
      ...holidayListData.value,
      condition: convertToConditions({
        conditions: holidayListData.value.condition_json,
        fieldPrefix: 'doc',
      }),
      condition_json: JSON.stringify(holidayListData.value.condition_json),
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
      new_name: holidayListData.value.business_holiday_name,
    }
  },
})

const updateBusinessHoliday = async () => {
  await holidayListResource.setValue.submit(
    {
      ...holidayListData.value,
      name: step.value.data.name,
      condition: useNewUI.value
        ? convertToConditions({
            conditions: holidayListData.value.condition_json,
            fieldPrefix: 'doc',
          })
        : holidayListData.value.condition,
      condition_json: useNewUI.value
        ? JSON.stringify(holidayListData.value.condition_json)
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
    holidayListData.value.name !== holidayListData.value.business_holiday_name
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
      name: holidayListData.value.business_holiday_name,
    })
  } else {
    await getBusinessHolidayResource.reload()
  }

  toast.success(__('Business holiday updated'))
  holidayListResource.reload()
}

const updateDuration = (key) => {
  validateHolidayListData(key)
  if (
    !holidayListDataErrors.value.dateRange ||
    holidayListDataErrors.value.dateRange === ''
  ) {
    updateWeeklyOffDates()
  }
}

watch(
  holidayListData,
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
  resetHolidayListErrors()
  disableSettingModalOutsideClick.value = false
})
</script>
