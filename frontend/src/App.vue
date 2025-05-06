<template>
  <Layout v-if="session().isLoggedIn">
    <router-view />
  </Layout>
  <Dialogs />
  <Toasts />
</template>

<script setup>
import { Dialogs } from '@/utils/dialogs'
import { sessionStore as session } from '@/stores/session'
import { setTheme } from '@/stores/theme'
import { Toasts, setConfig } from 'frappe-ui'
import { computed, defineAsyncComponent, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const MobileLayout = defineAsyncComponent(
  () => import('./components/Layouts/MobileLayout.vue'),
)
const DesktopLayout = defineAsyncComponent(
  () => import('./components/Layouts/DesktopLayout.vue'),
)
const CampaignLayout = defineAsyncComponent(
  () => import('./components/Layouts/CampaignLayout.vue'),
)

const Layout = computed(() => {
  if (route.path.includes('/campaigns')) {
    return CampaignLayout
  }
  if (window.innerWidth < 640) {
    return MobileLayout
  } else {
    return DesktopLayout
  }
})

onMounted(() => setTheme())

setConfig('systemTimezone', window.timezone?.system || null)
setConfig('localTimezone', window.timezone?.user || null)
</script>
