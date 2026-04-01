import { useTheme } from 'frappe-ui'
import { computed } from 'vue'

export function useChartTheme() {
  const { currentTheme } = useTheme()

  const isDark = computed(() => {
    if (currentTheme.value === 'dark') return true
    if (currentTheme.value === 'system') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    return false
  })

  const chartColors = computed(() => ({
    tooltip: {
      backgroundColor: isDark.value ? '#1f2937' : '#ffffff',
      borderColor: isDark.value ? '#374151' : '#E5E7EB',
      textColor: isDark.value ? '#f3f4f6' : '#111827',
    },
    text: {
      primary: isDark.value ? '#f3f4f6' : '#111827',
      secondary: isDark.value ? '#9ca3af' : '#6b7280',
      tertiary: isDark.value ? '#6b7280' : '#9ca3af',
    },
    axis: {
      line: isDark.value ? '#374151' : '#E5E7EB',
      label: isDark.value ? '#9ca3af' : '#6b7280',
      splitLine: isDark.value ? '#374151' : '#E5E7EB',
    },
    legend: {
      text: isDark.value ? '#d1d5db' : '#374151',
    },
    grid: {
      background: isDark.value ? '#111827' : '#ffffff',
    },
    border: {
      bar: isDark.value ? '#1f2937' : '#ffffff',
      line: isDark.value ? '#4b5563' : '#E5E7EB',
    },
    background: {
      bar: isDark.value ? '#374151' : '#F4F5F6',
    },
  }))

  return {
    isDark,
    chartColors,
  }
}
