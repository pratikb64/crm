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
      <FormControl
        type="select"
        :options="['Draft', 'Active', 'Inactive']"
        v-model="campaign.status"
        class="w-24"
        />
      <Button
        :label="__('Save')"
        variant="solid"
        @click="onCreateCampaign"
        :loading="isCampaignCreating"
      />
    </template>
  </CampaignLayoutHeader>
  <div class="mt-3 gap-4 px-2 sm:px-5">
    <div class="text-lg font-medium">{{ __('Details') }}</div>
    <div class="mt-4">
      <div class="flex gap-4">
        <FormControl
        :type="'text'"
        :placeholder="__('Name')"
        :label="__('Name')"
        class="w-full"
        v-model="campaign.campaign_name"
        />
        <FormControl
        :type="'text'"
        :placeholder="__('Subject')"
        :label="__('Subject')"
        class="w-full"
        v-model="campaign.subject"
        />
      </div>
      <div class="flex gap-4 mt-4">
        <FormControl
        :type="'text'"
        :placeholder="__('Sender Name')"
        :label="__('Sender Name')"
        class="w-full"
        v-model="campaign.sender_name"
        />
        <FormControl
        :type="'text'"
        :placeholder="__('Sender Email')"
        :label="__('Sender Email')"
        class="w-full"
        v-model="campaign.sender_email"
        />
      </div>
    </div>
  </div>
  <hr class="my-4" />
  <div class="px-2 sm:px-5">
    <div class="flex items-center gap-6">
      <div class="text-lg font-medium">{{ __('Audience') }}</div>
    </div>
    <div class="mt-4 flex flex-1">
      <Grid
        v-model="campaign.audience"
        doctype="CRM Audience"
        parentDoctype="CRM Campaign"
        parentFieldname="campaign_audience"
      />
    </div>
  </div>
  <hr class="my-4" />
  <div class="px-2 sm:px-5">
    <div class="text-lg font-medium">{{ __('Activity list') }}</div>
    <div
      v-if="campaign.activity_list.length > 0"
      class="mt-4 flex items-center gap-4"
    >
      <label class="w-48 text-base text-ink-gray-7">{{ __('Date') }}</label>
      <label class="w-52 text-base text-ink-gray-7">{{ __('Email') }}</label>
      <!-- <label class="w-24 text-base text-ink-gray-7">{{ __('Status') }}</label> -->
    </div>
    <div
      v-for="(activity, index) in campaign.activity_list"
      :key="index"
      class="group mt-4 flex items-center gap-4"
    >
      <FormControl type="date" v-model="activity.date" class="w-48" />
      <div class="w-52">
        <Autocomplete
          :options="emailTemplatesList"
          :model-value="getTemplateValue(activity)"
          @update:model-value="(val) => updateTemplateValue(activity, val)"
          placeholder="Select email template"
          class="w-full"
        >
          <template #item-label="{ option }">
            <div class="flex flex-col gap-1 text-ink-gray-9">
              <div>{{ option.label }}</div>
              <div class="text-sm text-ink-gray-4">
                {{ option.subject }}
              </div>
            </div>
          </template>
          <template #footer>
            <Button
              class="w-full"
              :label="__('Add Email Template')"
              variant="subtle"
              @click="addEmailTemplate"
            >
              <template #prefix>
                <FeatherIcon name="plus" class="h-4" />
              </template>
            </Button>
          </template>
        </Autocomplete>
      </div>
      <!-- <div class="w-24 text-base text-ink-gray-7">{{ activity.status }}</div> -->
      <Button
        class="hidden text-ink-red-4 group-hover:flex"
        variant="ghost"
        icon="trash-2"
        @click="deleteActivity(index)"
      />
    </div>
    <div
      v-if="campaign.activity_list.length == 0"
      class="flex h-36 w-full items-center justify-center"
    >
      <div
        class="flex flex-col items-center gap-3 text-xl font-medium text-ink-gray-4"
      >
        <span>{{ __('No activities added') }}</span>
        <Button
          :label="__('Add Activity')"
          variant="subtle"
          @click="addActivity"
        />
      </div>
    </div>
    <div v-if="campaign.activity_list.length > 0" class="mt-6">
      <Button
        :label="__('Add Activity')"
        variant="subtle"
        @click="addActivity"
      />
    </div>
  </div>
  <!-- <ErrorPage
    v-if="errorTitle"
    :errorTitle="errorTitle"
    :errorMessage="errorMessage"
  /> -->
</template>
<script setup>
import Icon from '@/components/Icon.vue'
import CampaignLayoutHeader from '@/components/CampaignLayoutHeader.vue'
import { errorMessage as _errorMessage, createToast } from '@/utils'
import {
  Breadcrumbs,
  FormControl,
  Button,
  createResource,
  call,
} from 'frappe-ui'
import { computed, ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { globalStore } from '@/stores/global'
import Grid from '@/components/Controls/Grid.vue'

const errorTitle = ref('')
const emailTemplatesList = ref([])
const isCampaignCreating = ref(false)

const campaign = reactive({
  campaign_name: '',
  status: 'Draft',
  sender_email:'',
  sender_name:'',
  subject:'',
  audience: [],
  activity_list: [],
})

const router = useRouter()

const { $dialog } = globalStore()

const createCampaign = createResource({
  url: 'frappe.client.insert',
  makeParams(values) {
    return {
      doc: {
        doctype: 'CRM Campaign',
        ...values,
      },
    }
  },
  validate() {
    if (!campaign.campaign_name) {
      errorTitle.value = __('Campaign Name is required')
      return errorTitle.value
    }
    if (!campaign.subject) {
      errorTitle.value = __('Subject is required')
      return errorTitle.value
    }
    if (!campaign.sender_name) {
      errorTitle.value = __('Sender Name is required')
      return errorTitle.value
    }
    if (!campaign.sender_email) {
      errorTitle.value = __('Sender email is required')
      return errorTitle.value
    }

    return true
  },
})

createResource({
  url: 'crm.api.doc.get_data',
  params: {
    doctype: 'Email Template',
    filters: {},
    order_by: 'modified desc',
  },
  onSuccess(data) {
    console.log('data', data)
    emailTemplatesList.value = data.data.map((item) => {
      return {
        label: item.name,
        value: item.name,
        subject: item.subject,
      }
    })
  },
}).fetch()

const addEmailTemplate = () => {
  window.open('/app/email-template', '_blank')
}

const onSend = () => {
  call('crm.fcrm.doctype.crm_campaign.api.send').then((data) => {
    createToast({
      title: __('Success'),
      message: data,
      variant: 'success',
    })
  })
}

const addActivity = () => {
  campaign.activity_list.push({
    date: '',
    activity: {
      type: 'email',
      data: '',
    },
    status: 'Pending',
  })
}

const deleteActivity = (index) => {
  campaign.activity_list.splice(index, 1)
}

const getTemplateValue = (campaign) => {
  return campaign.activity.data?.value || campaign.activity.data || ''
}

const updateTemplateValue = (campaign, val) => {
  if (typeof val === 'object' && val !== null) {
    campaign.activity.data = val.value
  } else {
    campaign.activity.data = val
  }
}

const onCreateCampaign = () => {
  console.log('campaign', campaign)
  isCampaignCreating.value = true
  createCampaign.submit(
    { ...campaign, activity_list: JSON.stringify(campaign.activity_list) },
    {
      onSuccess(data) {
        isCampaignCreating.value = false
        router.push({ name: 'Campaign', params: { campaignId: data.name } })
      },
      onError(err) {
        isCampaignCreating.value = false
        $dialog({
          title: __('Error'),
          message: err.message,
          actions: [
            {
              label: __('OK'),
              theme: 'red',
              variant: 'solid',
              async onClick(close) {
                close()
              },
            },
          ],
        })
      },
    },
  )
}

const breadcrumbs = computed(() => {
  let items = [{ label: __('Campaigns'), route: { name: 'Campaigns' } }]

  items.push({
    label: __('New Campaign'),
    route: {
      name: 'Create Campaign',
    },
  })
  return items
})
</script>
