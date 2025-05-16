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
          v-model="campaign.data.status"
          class="w-24"
        />
      <Button
        :label="__('Delete')"
        @click="() => deleteCampaign(props.campaignId)"
      />
      <Button
        :label="__('Save')"
        variant="solid"
        @click="onCampaignSave"
        :loading="isCampaignSaving"
      />
    </template>
  </CampaignLayoutHeader>
  <div v-if="campaign.data">
    <div class="mt-3 gap-4 px-2 sm:px-5">
      <div class="text-lg font-medium">{{ __('Details') }}</div>
      <div class="mt-4">
      <div class="flex gap-4">
        <FormControl
        :type="'text'"
        :placeholder="__('Name')"
        :label="__('Name')"
        class="w-full"
        v-model="campaign.data.campaign_name"
        />
        <FormControl
        :type="'text'"
        :placeholder="__('Subject')"
        :label="__('Subject')"
        class="w-full"
        v-model="campaign.data.subject"
        />
      </div>
      <div class="flex gap-4 mt-4">
        <FormControl
        :type="'text'"
        :placeholder="__('Sender Name')"
        :label="__('Sender Name')"
        class="w-full"
        v-model="campaign.data.sender_name"
        />
        <FormControl
        :type="'text'"
        :placeholder="__('Sender Email')"
        :label="__('Sender Email')"
        class="w-full"
        v-model="campaign.data.sender_email"
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
          v-model="campaign.data.audience"
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
        v-if="campaign.data.activity_list?.length > 0"
        class="mt-4 flex items-center gap-4"
      >
        <label class="w-48 text-base text-ink-gray-7">{{ __('Date') }}</label>
        <label class="w-52 text-base text-ink-gray-7">{{ __('Email') }}</label>
        <label class="w-24 text-base text-ink-gray-7">{{ __('Status') }}</label>
      </div>
      <div
        v-for="(activity, index) in campaign.data.activity_list"
        :key="index"
        class="group mt-4 flex items-center gap-4"
      >
        <FormControl type="date" v-model="activity.date" class="w-48" />
        <div class="w-52">
          <Autocomplete
            :options="emailTemplatesList"
            v-model="activity.activity.data"
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
        <div class="w-24 text-base text-ink-gray-7">{{ activity.status }}</div>
        <Button
          class="hidden text-ink-red-4 group-hover:flex"
          variant="ghost"
          icon="trash-2"
          @click="deleteActivity(index)"
        />
      </div>
      <div
        v-if="campaign.data.activity_list?.length == 0"
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
      <div v-if="campaign.data.activity_list?.length > 0" class="mt-6">
        <Button
          :label="__('Add Activity')"
          variant="subtle"
          @click="addActivity"
        />
      </div>
    </div>
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
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { globalStore } from '@/stores/global'
import { getMeta } from '@/stores/meta'
import ErrorPage from '@/components/ErrorPage.vue'
import Grid from '@/components/Controls/Grid.vue'

const props = defineProps({
  campaignId: {
    type: String,
    required: true,
  },
})

const { $dialog, $socket } = globalStore()
const errorTitle = ref('')
const errorMessage = ref('')
const route = useRoute()
const router = useRouter()
const { doctypeMeta } = getMeta('CRM Campaign')
const emailTemplatesList = ref([])

const campaign = createResource({
  url: 'crm.fcrm.doctype.crm_campaign.api.get_campaign',
  params: { name: props.campaignId },
  cache: ['campaign', props.campaignId],
  transform: (data) => {
    data.activity_list = JSON.parse(data.activity_list)
    return data
  },
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

createResource({
  url: 'crm.api.doc.get_data',
  params: {
    doctype: 'Email Template',
    filters: {},
    order_by: 'modified desc',
  },
  onSuccess(data) {
    emailTemplatesList.value = data.data.map((item) => {
      return {
        label: item.name,
        value: item.name,
        subject: item.subject,
      }
    })
  },
}).fetch()

const onCampaignSave = () => {
  createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: 'CRM Campaign',
      name: props.campaignId,
      fieldname: {
        ...campaign.data,
        activity_list: JSON.stringify(campaign.data.activity_list),
      },
    },
    auto: true,
    onSuccess: () => {
      campaign.reload()
      createToast({
        title: __('Campaign updated'),
        icon: 'check',
        iconClasses: 'text-ink-green-3',
      })
    },
    onError: (err) => {
      createToast({
        title: __('Error updating campaign'),
        text: __(err.messages?.[0]),
        icon: 'x',
        iconClasses: 'text-ink-red-4',
      })
    },
  })
}

const addActivity = () => {
  campaign.data.activity_list.push({
    date: '',
    activity: {
      type: 'email',
      data: '',
    },
    status: 'Pending',
  })
}

const deleteActivity = (index) => {
  campaign.data.activity_list.splice(index, 1)
}

const addEmailTemplate = () => {
  window.open('/app/email-template', '_blank')
}
onMounted(() => {
  if (campaign.data) return
  campaign.fetch()
})

const title = computed(() => {
  let t = doctypeMeta['CRM Campaign']?.title_field || 'name'
  return campaign.data?.[t] || props.campaignId
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
</script>
