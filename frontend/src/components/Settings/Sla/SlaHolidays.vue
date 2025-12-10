<template>
  <div class="rounded-md border px-2 border-gray-300 text-sm">
    <div
      class="grid p-2 px-4 items-center"
      :style="{
        gridTemplateColumns: getGridTemplateColumnsForTable(columns),
      }"
      v-if="slaData.support_and_resolution?.length !== 0"
    >
      <div
        v-for="column in columns"
        :key="column.key"
        class="text-gray-600 overflow-hidden whitespace-nowrap text-ellipsis"
        :class="{
          'ml-2': column.key === 'workday',
        }"
      >
        {{ column.label }}
        <span v-if="column.isRequired" class="text-red-500">*</span>
      </div>
    </div>
    <hr v-if="slaData.support_and_resolution?.length !== 0" />
    <SlaWorkDaysListItem
      v-for="(row, index) in slaData.support_and_resolution"
      :key="index + row.workday + row.id"
      :row="row"
      :columns="columns"
      :isLast="index === slaData.support_and_resolution.length - 1"
    />
    <div
      v-for="(row, index) in slaData.support_and_resolution"
      :key="index + row.workday + row.id"
      :row="row"
    >
      <div
        class="grid gap-2 py-3.5 px-4 items-center"
        :style="{
          gridTemplateColumns: getGridTemplateColumnsForTable(props.columns),
        }"
      >
        <div
          v-for="column in props.columns"
          :key="column.key"
          class="w-full overflow-hidden whitespace-nowrap text-ellipsis"
        >
          <div v-if="column.key === 'start_time' || column.key === 'end_time'">
            {{ formatTime(props.row[column.key]) }}
          </div>
          <div v-else class="ml-2">
            <select
              class="w-full h-7 text-base hover:bg-surface-gray-3 rounded-md p-0 pl-2 pr-5 bg-transparent -ml-2 border-0 text-ink-gray-8 focus-visible:!ring-0 bg-none truncate"
              v-model="props.row[column.key]"
            >
              <option
                v-for="option in workDayOptions"
                :key="option.value"
                :value="option.value"
              >
                {{ option.label }}
              </option>
            </select>
          </div>
        </div>
        <div class="flex justify-end">
          <Dropdown placement="right" :options="dropdownOptions">
            <Button
              icon="more-horizontal"
              variant="ghost"
              @click="isConfirmingDelete = false"
            />
          </Dropdown>
        </div>
      </div>
      <hr v-if="!(index === slaData.support_and_resolution.length - 1)" />
      <WorkDayModal
        v-model="dialog"
        :workDaysList="slaData.support_and_resolution"
      />
    </div>
    <div
      v-if="slaData.support_and_resolution?.length === 0"
      class="text-center p-4 text-gray-600"
    >
      No workdays in the list
    </div>
  </div>
  <div class="flex items-center justify-between mt-2.5">
    <Button
      v-if="slaData.support_and_resolution.length < 7"
      variant="subtle"
      label="Add row"
      @click="addWorkDay"
      icon-left="plus"
    />
    <ErrorMessage :message="slaDataErrors.support_and_resolution" />
  </div>
</template>

<script setup>
import { Button, Dropdown, ErrorMessage, NestedPopover } from 'frappe-ui'
import { getGridTemplateColumnsForTable } from '../../../utils'

const columns = [
  {
    label: 'Day',
    key: 'workday',
    isRequired: true,
  },
  {
    label: 'Start time',
    key: 'start_time',
    isRequired: true,
  },
  {
    label: 'End time',
    key: 'end_time',
    isRequired: true,
  },
]
</script>
