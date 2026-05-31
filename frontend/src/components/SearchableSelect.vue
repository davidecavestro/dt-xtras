<template>
  <div class="relative">
    <label v-if="label" :for="id" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
      {{ label }}
    </label>

    <!-- Selected value shown as a clearable chip -->
    <div
      v-if="modelValue"
      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white flex items-center justify-between gap-2"
    >
      <span class="truncate" :title="selectedLabel">{{ selectedLabel }}</span>
      <button
        type="button"
        @click="clear"
        class="text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 text-lg leading-none shrink-0 cursor-pointer"
        :title="label ? `Clear ${label}` : 'Clear'"
      >
        ×
      </button>
    </div>

    <!-- Searchable input + results -->
    <template v-else>
      <input
        :id="id"
        ref="inputRef"
        v-model="query"
        @focus="open = true"
        @blur="open = false"
        @keydown.down.prevent="onArrow(1)"
        @keydown.up.prevent="onArrow(-1)"
        @keydown.enter.prevent="onEnter"
        @keydown.esc="open = false"
        type="text"
        role="combobox"
        :aria-expanded="open && visibleOptions.length > 0"
        aria-autocomplete="list"
        :placeholder="placeholder"
        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <!-- @mousedown.prevent on options keeps the input focused so the click
           registers before the blur closes the menu. -->
      <ul
        v-if="open && visibleOptions.length"
        ref="listRef"
        role="listbox"
        class="absolute z-20 mt-1 w-full max-h-60 overflow-auto rounded-md border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 shadow-lg"
      >
        <li
          v-for="(opt, index) in visibleOptions"
          :key="opt.value"
          role="option"
          :aria-selected="index === activeIndex"
          @mousedown.prevent="select(opt.value)"
          @mousemove="activeIndex = index"
          :class="[
            'px-3 py-2 cursor-pointer text-sm flex items-center justify-between gap-2',
            index === activeIndex ? 'bg-gray-100 dark:bg-gray-600' : 'hover:bg-gray-100 dark:hover:bg-gray-600'
          ]"
          :title="opt.label"
        >
          <span class="truncate">{{ opt.label }}</span>
          <span v-if="opt.hint != null" class="text-xs text-gray-500 dark:text-gray-400 shrink-0">{{ opt.hint }}</span>
        </li>
        <li v-if="truncated" class="px-3 py-1.5 text-xs text-gray-400 dark:text-gray-500 italic">
          Refine your search to see more…
        </li>
      </ul>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'

// A lightweight searchable single-select. Options may be plain strings or
// objects; for objects, labelKey/valueKey/hintKey select the fields. Filtering
// is client-side (the caller provides the full list) and capped at `limit` so
// the menu stays light even with hundreds of options.
const props = defineProps({
  modelValue: { type: String, default: '' },
  options: { type: Array, default: () => [] },
  labelKey: { type: String, default: 'name' },
  valueKey: { type: String, default: 'name' },
  hintKey: { type: String, default: null },
  placeholder: { type: String, default: 'Search…' },
  label: { type: String, default: '' },
  id: { type: String, default: null },
  limit: { type: Number, default: 50 }
})
const emit = defineEmits(['update:modelValue'])

const query = ref('')
const open = ref(false)
const activeIndex = ref(-1)
const listRef = ref(null)

const normalizedOptions = computed(() =>
  (props.options || []).map(o =>
    o !== null && typeof o === 'object'
      ? { value: o[props.valueKey], label: o[props.labelKey], hint: props.hintKey ? o[props.hintKey] : null }
      : { value: o, label: o, hint: null }
  )
)

const matching = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return normalizedOptions.value
  return normalizedOptions.value.filter(o => String(o.label).toLowerCase().includes(q))
})
const visibleOptions = computed(() => matching.value.slice(0, props.limit))
const truncated = computed(() => matching.value.length > props.limit)

const selectedLabel = computed(() => {
  const found = normalizedOptions.value.find(o => o.value === props.modelValue)
  return found ? found.label : props.modelValue
})

const select = (value) => {
  emit('update:modelValue', value)
  query.value = ''
  open.value = false
}
const clear = () => {
  emit('update:modelValue', '')
  query.value = ''
}

// Keyboard navigation: arrows move the highlight, Enter selects it, Esc closes.
// Reset the highlight to the first match as the query/options change.
watch([query, visibleOptions], () => {
  activeIndex.value = visibleOptions.value.length ? 0 : -1
})

const scrollActiveIntoView = () => {
  nextTick(() => {
    const el = listRef.value?.children?.[activeIndex.value]
    if (el && typeof el.scrollIntoView === 'function') el.scrollIntoView({ block: 'nearest' })
  })
}

const onArrow = (delta) => {
  open.value = true
  const count = visibleOptions.value.length
  if (!count) return
  // Clamp; from -1 (nothing highlighted), ArrowDown lands on the first option.
  activeIndex.value = Math.min(Math.max(activeIndex.value + delta, 0), count - 1)
  scrollActiveIntoView()
}

const onEnter = () => {
  if (open.value && activeIndex.value >= 0 && activeIndex.value < visibleOptions.value.length) {
    select(visibleOptions.value[activeIndex.value].value)
  }
}
</script>
