import { ref } from 'vue'
import { validateConditions } from '../../../utils'

const defaultAssignmentDays = [
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday',
]

export const assignmentRuleData = ref({
  assignCondition: '',
  unassignCondition: '',
  assignConditionJson: [],
  unassignConditionJson: [],
  rule: 'Round Robin',
  priority: 1,
  users: [],
  disabled: false,
  description: '',
  name: '',
  assignmentRuleName: '',
  assignmentDays: defaultAssignmentDays,
  documentType: 'CRM Lead',
})

export const validateAssignmentRule = (key, skipConditionCheck = false) => {
  const validateField = (field) => {
    if (key && field !== key) return

    switch (field) {
      case 'assignmentRuleName':
        if (assignmentRuleData.value.assignmentRuleName?.length == 0) {
          assignmentRuleErrors.value.assignmentRuleName = 'Name is required'
        } else {
          assignmentRuleErrors.value.assignmentRuleName = ''
        }
        break
      case 'description':
        assignmentRuleErrors.value.description =
          assignmentRuleData.value.description?.length > 0
            ? ''
            : 'Description is required'
        break
      case 'assignCondition':
        if (skipConditionCheck) {
          break
        }
        assignmentRuleErrors.value.assignCondition =
          assignmentRuleData.value.assignConditionJson?.length > 0
            ? ''
            : 'Assign condition is required'

        if (!validateConditions(assignmentRuleData.value.assignConditionJson)) {
          assignmentRuleErrors.value.assignConditionError =
            'Assign conditions are invalid'
        } else {
          assignmentRuleErrors.value.assignConditionError = ''
        }

        break
      case 'unassignCondition':
        if (skipConditionCheck) {
          break
        }
        if (
          assignmentRuleData.value.unassignConditionJson?.length > 0 &&
          !validateConditions(assignmentRuleData.value.unassignConditionJson)
        ) {
          assignmentRuleErrors.value.unassignConditionError =
            'Unassign conditions are invalid'
        } else {
          assignmentRuleErrors.value.unassignConditionError = ''
        }
        break
      case 'users':
        assignmentRuleErrors.value.users =
          assignmentRuleData.value.users?.length > 0 ? '' : 'Users are required'
        break
      case 'assignmentDays':
        assignmentRuleErrors.value.assignmentDays =
          assignmentRuleData.value.assignmentDays?.length > 0
            ? ''
            : 'Assignment days are required'
        break
      default:
        break
    }
  }

  if (key) {
    validateField(key)
  } else {
    Object.keys(assignmentRuleErrors.value).forEach(validateField)
  }

  return assignmentRuleErrors.value
}

export const resetAssignmentRuleData = () => {
  assignmentRuleData.value = {
    assignCondition: '',
    unassignCondition: '',
    assignConditionJson: [],
    unassignConditionJson: [],
    rule: 'Round Robin',
    priority: 1,
    users: [],
    disabled: false,
    description: '',
    name: '',
    assignmentRuleName: '',
    assignmentDays: defaultAssignmentDays,
    documentType: 'CRM Lead',
  }
}

export const assignmentRuleErrors = ref({
  assignmentRuleName: '',
  assignCondition: '',
  assignConditionError: '',
  unassignConditionError: '',
  users: '',
  description: '',
  assignmentDays: '',
})

export const resetAssignmentRuleErrors = () => {
  Object.keys(assignmentRuleErrors.value).forEach((key) => {
    assignmentRuleErrors.value[key] = ''
  })
}
