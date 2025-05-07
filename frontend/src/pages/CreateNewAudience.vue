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
      <div class="mt-4">
        <Filter v-model="list" :doctype="'CRM Lead'" @update="updateFilter" />
      </div>
    </div>
  </div>
</template>

<script setup>
import Icon from '@/components/Icon.vue'
import { ref, computed } from 'vue'
import CampaignLayoutHeader from '@/components/CampaignLayoutHeader.vue'
import { Breadcrumbs, Button } from 'frappe-ui'
import Filter from '@/components/Filter.vue'

const isAudienceCreating = ref(false)

const breadcrumbs = computed(() => {
  let items = [
    { label: __('Audiences'), route: { name: 'Audiences' } },
    { label: __('New Audience') },
  ]
  return items
})
</script>
