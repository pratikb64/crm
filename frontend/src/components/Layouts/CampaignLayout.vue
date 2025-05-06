<template>
  <div class="flex h-screen w-screen">
    <div class="h-full border-r bg-surface-menu-bar">
      <CampaignAppSidebar />
    </div>
    <div class="flex-1 flex flex-col h-full overflow-auto bg-surface-white">
      <CampaignAppHeader />
      <slot />
    </div>
  </div>
</template>
<script setup>
import CampaignAppSidebar from '@/components/Layouts/CampaignAppSidebar.vue'
import CampaignAppHeader from '@/components/Layouts/CampaignAppHeader.vue'
</script>
