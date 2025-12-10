import { ref } from 'vue'
import { validateConditions } from '../../../utils'

export const slaData = ref({
  name: 'asd',
  sla_name: '',
  apply_on: 'Lead',
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
  loading: false,
})

export const slaDataErrors = ref({
  service_level: '',
  description: '',
  enabled: '',
  default_sla: '',
  apply_sla_for_resolution: '',
  priorities: '',
  holiday_list: '',
  default_priority: '',
  start_date: '',
  end_date: '',
  support_and_resolution: '',
  condition: '',
})

export const resetSlaDataErrors = () => {
  slaDataErrors.value = {
    service_level: '',
    description: '',
    enabled: '',
    default_sla: '',
    apply_sla_for_resolution: '',
    priorities: '',
    holiday_list: '',
    default_priority: '',
    start_date: '',
    end_date: '',
    support_and_resolution: '',
    condition: '',
  }
}

export function validateSlaData(key, skipConditionCheck = false) {
  // Reset all errors
  resetSlaDataErrors()

  const validateField = (field) => {
    if (key && field !== key) return

    switch (field) {
      case 'service_level':
        if (!slaData.value.service_level?.trim()) {
          slaDataErrors.value.service_level = 'SLA policy name is required'
        } else {
          slaDataErrors.value.service_level = ''
        }
        break
      case 'priorities':
        if (
          !Array.isArray(slaData.value.priorities) ||
          slaData.value.priorities.length === 0
        ) {
          slaDataErrors.value.priorities = 'At least one priority is required'
        } else {
          const prioritiesError = []
          slaData.value.priorities.forEach((priority, index) => {
            const priorityNum = index + 1
            if (!priority.priority?.trim()) {
              prioritiesError.push(
                `Priority ${priorityNum}: Priority name is required`,
              )
            }
            if (
              !priority.first_response_time ||
              priority.first_response_time == 0
            ) {
              prioritiesError.push(
                `Priority ${priorityNum}: Response time is required`,
              )
            }
          })

          // Check for duplicate priorities
          const priorityNames = slaData.value.priorities
            .map((p) => p.priority?.trim().toLowerCase())
            .filter(Boolean)
          const uniquePriorities = new Set(priorityNames)

          if (priorityNames.length !== uniquePriorities.size) {
            prioritiesError.push('Priorities must be unique')
          }

          if (prioritiesError.length > 0) {
            slaDataErrors.value.priorities = prioritiesError.join(', ')
          } else {
            slaDataErrors.value.priorities = ''
          }

          const hasDefaultPriority = slaData.value.priorities.some((p) =>
            Boolean(p.default_priority),
          )
          if (!hasDefaultPriority) {
            slaDataErrors.value.default_priority =
              'At least one default priority is required'
          } else {
            slaDataErrors.value.default_priority = ''
          }
        }
        break
      case 'holiday_list':
        if (!slaData.value.holiday_list) {
          slaDataErrors.value.holiday_list = 'Holiday list is required'
        } else {
          slaDataErrors.value.holiday_list = ''
        }
        break
      case 'start_date':
        if (
          new Date(slaData.value.end_date) < new Date(slaData.value.start_date)
        ) {
          slaDataErrors.value.start_date = 'Start date cannot be after end date'
        } else {
          slaDataErrors.value.start_date = ''
        }
        break
      case 'end_date':
        if (
          slaData.value.end_date &&
          new Date(slaData.value.end_date) < new Date(slaData.value.start_date)
        ) {
          slaDataErrors.value.end_date = 'End date cannot be before start date'
        } else {
          slaDataErrors.value.end_date = ''
        }
        break
      case 'condition':
        if (skipConditionCheck) {
          break
        }
        if (
          slaData.value.condition_json.length > 0 &&
          !validateConditions(slaData.value.condition_json)
        ) {
          slaDataErrors.value.condition = 'Valid conditions are required'
        } else {
          slaDataErrors.value.condition = ''
        }
        break
      case 'support_and_resolution':
        const validWorkdays = slaData.value.support_and_resolution?.filter(
          (day) =>
            day.workday &&
            day.workday.trim() !== '' &&
            day.start_time &&
            day.end_time &&
            day.start_time.trim() !== '' &&
            day.end_time.trim() !== '',
        )

        if (!validWorkdays?.length) {
          slaDataErrors.value.support_and_resolution =
            'At least one valid workday with workday, start time, and end time is required'
        } else {
          // Check for duplicate workdays
          const workdayMap = new Map()
          const duplicateWorkdays = []

          for (const day of validWorkdays) {
            if (workdayMap.has(day.workday)) {
              duplicateWorkdays.push(day.workday)
            } else {
              workdayMap.set(day.workday, true)
            }
          }

          if (duplicateWorkdays.length > 0) {
            slaDataErrors.value.support_and_resolution = `Duplicate workday found: ${duplicateWorkdays.join(
              ', ',
            )}. Each workday should be unique.`
            return slaDataErrors.value
          } else {
            slaDataErrors.value.support_and_resolution = ''
          }

          const invalidTimeRanges = []
          for (const day of validWorkdays) {
            const startTimeStr = day.start_time.trim()
            const endTimeStr = day.end_time.trim()

            const parseTime = (timeStr) => {
              const [hours, minutes] = timeStr.split(':').map(Number)
              const date = new Date()
              date.setHours(hours, minutes || 0, 0, 0)
              return date
            }

            try {
              const startTime = parseTime(startTimeStr)
              const endTime = parseTime(endTimeStr)

              if (startTime >= endTime) {
                invalidTimeRanges.push(
                  `${day.workday} (${startTimeStr} - ${endTimeStr})`,
                )
              }
            } catch (error) {
              // If time parsing fails, mark as invalid
              invalidTimeRanges.push(`${day.workday} (Invalid time format)`)
            }
          }

          if (invalidTimeRanges.length > 0) {
            slaDataErrors.value.support_and_resolution = `End time must be after start time for: ${invalidTimeRanges.join(
              ', ',
            )}`
          } else {
            slaDataErrors.value.support_and_resolution = ''
          }
        }
        break

      default:
        break
    }
  }

  if (key) {
    validateField(key)
  } else {
    Object.keys(slaDataErrors.value).forEach(validateField)
  }

  return slaDataErrors.value
}
