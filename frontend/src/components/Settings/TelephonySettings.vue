<template>
  <div class="flex h-full flex-col gap-6">
    <div class="flex justify-between p-8 pb-0">
      <div class="flex flex-col gap-1 w-9/12">
        <h2
          class="flex gap-2 text-xl font-semibold leading-none h-5 text-ink-gray-8"
        >
          {{ __('Telephony settings') }}
          <Badge
            v-if="
              isDirty.twilio ||
              isDirty.exotel ||
              isDirty.telephonyAgent ||
              isDirty.defaultMedium
            "
            :label="__('Not Saved')"
            variant="subtle"
            theme="orange"
          />
        </h2>
        <p class="text-p-base text-ink-gray-6">
          {{ __('Configure telephony settings for your CRM') }}
        </p>
      </div>
      <div class="flex item-center space-x-2 w-3/12 justify-end">
        <Button
          :label="__('Update')"
          variant="solid"
          @click="update"
          :disabled="
            !isDirty.twilio &&
            !isDirty.exotel &&
            !isDirty.telephonyAgent &&
            !isDirty.defaultMedium
          "
          :loading="
            twilio.save.loading ||
            exotel.save.loading ||
            telephonyAgent.save.loading
          "
        />
      </div>
    </div>
    <div
      v-if="!twilio.get.loading || !exotel.get.loading"
      class="h-full flex flex-col gap-8 overflow-y-auto p-8 pt-0"
    >
      <div>
        <div class="text-base font-semibold text-ink-gray-8">
          {{ __('Agent settings') }}
        </div>
        <div class="text-p-xs text-ink-gray-6 mt-1">
          {{ __('Configure your agent’s telephony details.') }}
        </div>
        <div class="grid grid-cols-2 gap-4 mt-4">
          <div class="flex flex-col gap-1.5">
            <FormControl
              type="select"
              v-model="defaultCallingMedium"
              :label="__('Default medium')"
              :options="[
                { label: __(''), value: '' },
                { label: __('Twilio'), value: 'Twilio' },
                { label: __('Exotel'), value: 'Exotel' },
              ]"
              :description="__('Default calling medium for logged in user')"
            />
            <ErrorMessage
              :message="
                twilioErrors.default_medium || exotelErrors.default_medium
              "
            />
          </div>
          <div
            class="flex flex-col gap-1.5"
            v-if="telephonyAgent.doc && twilio.doc?.enabled"
          >
            <FormControl
              label="Twilio number"
              type="text"
              required
              v-model="telephonyAgent.doc.twilio_number"
            />
            <ErrorMessage :message="twilioErrors.number" />
          </div>
          <div
            class="flex flex-col gap-1.5"
            v-if="telephonyAgent.doc && exotel.doc?.enabled"
          >
            <FormControl
              label="Exotel number"
              type="text"
              required
              v-model="telephonyAgent.doc.exotel_number"
            />
            <ErrorMessage :message="exotelErrors.number" />
          </div>
          <div
            class="flex flex-col gap-1.5"
            v-if="telephonyAgent.doc && exotel.doc?.enabled"
          >
            <FormControl
              label="Personal mobile no"
              type="text"
              required
              v-model="telephonyAgent.doc.mobile_no"
              :description="__('Required for exotel integration')"
            />
            <ErrorMessage :message="exotelErrors.mobileNo" />
          </div>
        </div>
      </div>
      <div>
        <!-- Twilio -->
        <div v-if="isManager()" class="flex flex-col justify-between">
          <span class="text-base font-semibold text-ink-gray-8">
            {{ __('Twilio') }}
          </span>
          <div class="mt-4">
            <div class="grid grid-cols-2 gap-4">
              <Checkbox
                label="Enabled"
                v-model="twilio.doc.enabled"
                @update:modelValue="twilio.doc.enabled = $event ? 1 : 0"
              />
              <Checkbox
                label="Record Calls"
                v-model="twilio.doc.record_calls"
                v-if="twilio.doc.enabled"
                @update:modelValue="twilio.doc.record_calls = $event ? 1 : 0"
              />
            </div>
            <div class="grid grid-cols-2 gap-4 mt-4" v-if="twilio.doc.enabled">
              <div class="flex flex-col gap-2">
                <FormControl
                  label="Account SID"
                  required
                  v-model="twilio.doc.account_sid"
                  placeholder="Account SID"
                />
                <ErrorMessage :message="twilioErrors.accountSid" />
              </div>
              <div class="flex flex-col gap-2">
                <Password
                  label="Auth Token"
                  required
                  v-model="twilio.doc.auth_token"
                  placeholder="Auth Token"
                />
                <ErrorMessage :message="twilioErrors.authToken" />
              </div>
              <FormControl
                v-if="twilio.doc.api_key"
                label="API Key"
                v-model="twilio.doc.api_key"
                disabled
              />
              <Password
                v-if="twilio.doc.api_secret"
                label="API Secret"
                v-model="twilio.doc.api_secret"
                disabled
              />
              <Autocomplete
                v-if="twilio.originalDoc?.account_sid && twilioApps.length > 0"
                label="TwiML App Name"
                :model-value="twilio.doc.app_name"
                @update:modelValue="twilio.doc.app_name = $event.value"
                :options="twilioApps"
              >
                <template #footer="{ togglePopover }">
                  <Button
                    label="Refresh Apps"
                    theme="gray"
                    variant="subtle"
                    class="w-full"
                    icon-left="refresh-cw"
                    @click="refreshApps(togglePopover)"
                    :loading="twilioAppsResource.loading"
                  />
                </template>
              </Autocomplete>
              <FormControl
                v-if="twilio.doc.twiml_sid"
                label="TwiML App SID"
                v-model="twilio.doc.twiml_sid"
                disabled
              />
            </div>
          </div>
        </div>
      </div>
      <div>
        <!-- Exotel -->
        <div v-if="isManager()" class="flex flex-col justify-between">
          <span class="text-base font-semibold text-ink-gray-8">
            {{ __('Exotel') }}
          </span>
          <div class="mt-4">
            <div class="grid grid-cols-2 gap-4">
              <Checkbox
                label="Enabled"
                v-model="exotel.doc.enabled"
                @update:modelValue="exotel.doc.enabled = $event ? 1 : 0"
              />
              <Checkbox
                label="Record Calls"
                v-model="exotel.doc.record_call"
                v-if="exotel.doc.enabled"
                @update:modelValue="exotel.doc.record_call = $event ? 1 : 0"
              />
            </div>
            <div class="grid grid-cols-2 gap-4 mt-4" v-if="exotel.doc.enabled">
              <div class="flex flex-col gap-2">
                <FormControl
                  label="Account SID"
                  required
                  v-model="exotel.doc.account_sid"
                  placeholder="Account SID"
                />
                <ErrorMessage :message="exotelErrors.accountSid" />
              </div>
              <div class="flex flex-col gap-2">
                <FormControl
                  label="Webhook Verify Token"
                  required
                  v-model="exotel.doc.webhook_verify_token"
                  placeholder="Webhook Verify Token"
                />
                <ErrorMessage :message="exotelErrors.webhookVerifyToken" />
              </div>

              <div class="flex flex-col gap-2">
                <FormControl
                  label="API Key"
                  required
                  v-model="exotel.doc.api_key"
                  placeholder="API Key"
                />
                <ErrorMessage :message="exotelErrors.apiKey" />
              </div>
              <div class="flex flex-col gap-2">
                <Password
                  label="API Token"
                  required
                  v-model="exotel.doc.api_token"
                  placeholder="API Token"
                />
                <ErrorMessage :message="exotelErrors.apiToken" />
              </div>
              <div class="flex flex-col gap-2">
                <FormControl
                  label="Subdomain"
                  required
                  v-model="exotel.doc.subdomain"
                  placeholder="Subdomain"
                />
                <ErrorMessage :message="exotelErrors.subdomain" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- General -->
      <!-- <FormControl
        type="select"
        v-model="defaultCallingMedium"
        :label="__('Default medium')"
        :options="[
          { label: __(''), value: '' },
          { label: __('Twilio'), value: 'Twilio' },
          { label: __('Exotel'), value: 'Exotel' },
        ]"
        class="w-1/2"
        :description="__('Default calling medium for logged in user')"
      /> -->
    </div>
    <div v-else class="flex flex-1 items-center justify-center">
      <LoadingIndicator class="size-8" />
    </div>
    <ErrorMessage :message="twilio.save.error || exotel.save.error || error" />
  </div>
</template>
<script setup>
import FieldLayout from '@/components/FieldLayout/FieldLayout.vue'
import {
  createDocumentResource,
  createResource,
  FormControl,
  Spinner,
  Badge,
  ErrorMessage,
  call,
  Autocomplete,
  Password,
  Checkbox,
  Select,
  FormLabel,
  LoadingIndicator,
} from 'frappe-ui'
import { defaultCallingMedium } from '@/composables/settings'
import { usersStore } from '@/stores/users'
import { toast } from 'frappe-ui'
import { getRandom } from '@/utils'
import { ref, computed, watch, nextTick } from 'vue'

const { isManager, isTelephonyAgent, getUser } = usersStore()

const isDirty = ref({
  twilio: false,
  exotel: false,
  telephonyAgent: false,
  defaultMedium: false,
})

const twilioErrors = ref({
  accountSid: '',
  authToken: '',
  number: '',
  default_medium: '',
})

const exotelErrors = ref({
  accountSid: '',
  webhookVerifyToken: '',
  subdomain: '',
  apiKey: '',
  apiToken: '',
  number: '',
  mobileNo: '',
  default_medium: '',
})

const twilioApps = ref([])

// const twilioFields = createResource({
//   url: 'crm.api.doc.get_fields',
//   cache: ['fields', 'CRM Twilio Settings'],
//   params: {
//     doctype: 'CRM Twilio Settings',
//     allow_all_fieldtypes: true,
//   },
//   auto: true,
// })

// const exotelFields = createResource({
//   url: 'crm.api.doc.get_fields',
//   cache: ['fields', 'CRM Exotel Settings'],
//   params: {
//     doctype: 'CRM Exotel Settings',
//     allow_all_fieldtypes: true,
//   },
//   auto: true,
// })

const twilio = createDocumentResource({
  doctype: 'CRM Twilio Settings',
  name: 'CRM Twilio Settings',
  fields: ['*'],
  auto: true,
  // setValue: {
  //   onSuccess: () => {
  //     toast.success(__('Twilio settings updated successfully'))
  //   },
  //   onError: (err) => {
  //     toast.error(err.message + ': ' + err.messages[0])
  //   },
  // },
})

const exotel = createDocumentResource({
  doctype: 'CRM Exotel Settings',
  name: 'CRM Exotel Settings',
  fields: ['*'],
  auto: true,
  // setValue: {
  //   onSuccess: () => {
  //     toast.success(__('Exotel settings updated successfully'))
  //   },
  //   onError: (err) => {
  //     toast.error(err.message + ': ' + err.messages[0])
  //   },
  // },
})

const telephonyAgent = createDocumentResource({
  doctype: 'CRM Telephony Agent',
  name: getUser().name,
  cache: ['crm_telephony_agent'],
  fields: ['*'],
  auto: false,
})

const twilioAppsResource = createResource({
  url: 'crm.integrations.twilio.api.fetch_applications',
  onSuccess() {
    twilio.reload()
  },
})

createResource({
  url: 'crm.api.telephony.create_telephony_agent',
  auto: true,
  onSuccess() {
    telephonyAgent.get.submit()
  },
})

// const twilioTabs = computed(() => {
//   if (!twilioFields.data) return []
//   let _tabs = []
//   let fieldsData = twilioFields.data

//   if (fieldsData[0].type != 'Tab Break') {
//     let _sections = []
//     if (fieldsData[0].type != 'Section Break') {
//       _sections.push({
//         name: 'first_section',
//         columns: [{ name: 'first_column', fields: [] }],
//       })
//     }
//     _tabs.push({ name: 'first_tab', sections: _sections })
//   }

//   fieldsData.forEach((field) => {
//     let last_tab = _tabs[_tabs.length - 1]
//     let _sections = _tabs.length ? last_tab.sections : []
//     if (field.fieldtype === 'Tab Break') {
//       _tabs.push({
//         label: field.label,
//         name: field.fieldname,
//         sections: [
//           {
//             name: 'section_' + getRandom(),
//             columns: [{ name: 'column_' + getRandom(), fields: [] }],
//           },
//         ],
//       })
//     } else if (field.fieldtype === 'Section Break') {
//       _sections.push({
//         label: field.label,
//         name: field.fieldname,
//         hideBorder: field.hide_border,
//         columns: [{ name: 'column_' + getRandom(), fields: [] }],
//       })
//     } else if (field.fieldtype === 'Column Break') {
//       _sections[_sections.length - 1].columns.push({
//         name: field.fieldname,
//         fields: [],
//       })
//     } else {
//       let last_section = _sections[_sections.length - 1]
//       let last_column = last_section.columns[last_section.columns.length - 1]
//       last_column.fields.push(field)
//     }
//   })

//   return _tabs
// })

// const exotelTabs = computed(() => {
//   if (!exotelFields.data) return []
//   let _tabs = []
//   let fieldsData = exotelFields.data

//   if (fieldsData[0].type != 'Tab Break') {
//     let _sections = []
//     if (fieldsData[0].type != 'Section Break') {
//       _sections.push({
//         name: 'first_section',
//         columns: [{ name: 'first_column', fields: [] }],
//       })
//     }
//     _tabs.push({ name: 'first_tab', sections: _sections })
//   }

//   fieldsData.forEach((field) => {
//     let last_tab = _tabs[_tabs.length - 1]
//     let _sections = _tabs.length ? last_tab.sections : []
//     if (field.fieldtype === 'Tab Break') {
//       _tabs.push({
//         label: field.label,
//         name: field.fieldname,
//         sections: [
//           {
//             name: 'section_' + getRandom(),
//             columns: [{ name: 'column_' + getRandom(), fields: [] }],
//           },
//         ],
//       })
//     } else if (field.fieldtype === 'Section Break') {
//       _sections.push({
//         label: field.label,
//         name: field.fieldname,
//         hideBorder: field.hide_border,
//         columns: [{ name: 'column_' + getRandom(), fields: [] }],
//       })
//     } else if (field.fieldtype === 'Column Break') {
//       _sections[_sections.length - 1].columns.push({
//         name: field.fieldname,
//         fields: [],
//       })
//     } else {
//       let last_section = _sections[_sections.length - 1]
//       let last_column = last_section.columns[last_section.columns.length - 1]
//       last_column.fields.push(field)
//     }
//   })

//   return _tabs
// })

const mediumChanged = ref(false)

watch(defaultCallingMedium, () => {
  isDirty.value.defaultMedium = true
})

function update() {
  console.log(isDirty.value)
  if (!validateIfDefaultMediumIsEnabled()) return
  if (mediumChanged.value) {
    updateMedium()
  }

  if (!isManager()) return

  if (twilio.isDirty) {
    twilio.save.submit()
  }
  if (exotel.isDirty) {
    exotel.save.submit()
  }
}

async function updateMedium() {
  await call('crm.integrations.api.set_default_calling_medium', {
    medium: defaultCallingMedium.value,
  })
  mediumChanged.value = false
  error.value = ''
  toast.success(__('Default calling medium updated successfully'))
}

const error = ref('')

function validateIfDefaultMediumIsEnabled() {
  if (isTelephonyAgent() && !isManager()) return true

  if (defaultCallingMedium.value === 'Twilio' && !twilio.doc.enabled) {
    error.value = __('Twilio is not enabled')
    return false
  }
  if (defaultCallingMedium.value === 'Exotel' && !exotel.doc.enabled) {
    error.value = __('Exotel is not enabled')
    return false
  }
  return true
}

watch(
  () => telephonyAgent.doc,
  (newVal) => {
    isDirty.value.telephonyAgent = isDocDirty(
      newVal,
      telephonyAgent.originalDoc,
    )
  },
  { deep: true },
)

watch(
  () => twilio.doc,
  (newVal) => {
    isDirty.value.twilio = isDocDirty(newVal, twilio.originalDoc)
    twilioApps.value =
      newVal.twilio_apps?.split(',').map((app) => ({
        label: app,
        value: app,
      })) || []
  },
  { deep: true },
)

watch(
  () => exotel.doc,
  (newVal) => {
    isDirty.value.exotel = isDocDirty(newVal, exotel.originalDoc)
  },
  { deep: true },
)

const isDocDirty = (doc, originalDoc) => {
  return JSON.stringify(doc) !== JSON.stringify(originalDoc)
}

const validateTwilio = (twilio, telephonyAgent, twilioErrors) => {
  if (telephonyAgent.default_medium === 'Twilio' && !twilio.enabled) {
    twilioErrors.value.default_medium =
      'Enable Twilio to set it as default medium'
  } else {
    twilioErrors.value.default_medium = ''
  }

  if (!twilio.enabled) {
    return
  }

  if (!twilio.account_sid) {
    twilioErrors.value.accountSid = 'Account SID is required'
  } else {
    twilioErrors.value.accountSid = ''
  }

  if (!twilio.auth_token) {
    twilioErrors.value.authToken = 'Auth Token is required'
  } else {
    twilioErrors.value.authToken = ''
  }

  if (!telephonyAgent.twilio_number) {
    twilioErrors.value.number = 'Number is required'
  } else if (!validatePhone(telephonyAgent.twilio_number)) {
    twilioErrors.value.number = 'Please enter a valid phone number'
  } else {
    twilioErrors.value.number = ''
  }
}

const validateExotel = (exotel, telephonyAgent, exotelErrors) => {
  if (telephonyAgent.default_medium === 'Exotel' && !exotel.enabled) {
    exotelErrors.value.default_medium =
      'Enable Exotel to set it as default medium'
  } else {
    exotelErrors.value.default_medium = ''
  }

  if (!exotel.enabled) {
    return
  }

  if (!exotel.account_sid) {
    exotelErrors.value.accountSid = 'Account SID is required'
  } else {
    exotelErrors.value.accountSid = ''
  }

  if (!exotel.webhook_verify_token) {
    exotelErrors.value.webhookVerifyToken = 'Webhook Verify Token is required'
  } else {
    exotelErrors.value.webhookVerifyToken = ''
  }

  if (!exotel.subdomain) {
    exotelErrors.value.subdomain = 'Subdomain is required'
  } else {
    exotelErrors.value.subdomain = ''
  }

  if (!exotel.api_key) {
    exotelErrors.value.apiKey = 'API Key is required'
  } else {
    exotelErrors.value.apiKey = ''
  }

  if (!exotel.api_token) {
    exotelErrors.value.apiToken = 'API Token is required'
  } else {
    exotelErrors.value.apiToken = ''
  }

  if (!telephonyAgent.exotel_number) {
    exotelErrors.value.number = 'Number is required'
  } else if (!validatePhone(telephonyAgent.exotel_number)) {
    exotelErrors.value.number = 'Please enter a valid phone number'
  } else {
    exotelErrors.value.number = ''
  }

  if (!telephonyAgent.mobile_no) {
    exotelErrors.value.mobileNo = 'Personal number is required'
  } else if (!validatePhone(telephonyAgent.mobile_no)) {
    exotelErrors.value.mobileNo = 'Please enter a valid phone number'
  } else {
    exotelErrors.value.mobileNo = ''
  }
}

function refreshApps(togglePopover) {
  twilioAppsResource.submit().then(() => {
    // Close and reopen popover to fix bug where search does not work after refreshing list
    togglePopover()
    nextTick(() => {
      togglePopover()
    })
  })
}

const validatePhone = (number) => {
  return /^\+?\d{8,15}$/.test(number)
}
</script>
