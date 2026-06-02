<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 overflow-y-auto"
    aria-labelledby="modal-title"
    role="dialog"
    aria-modal="true"
  >
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- Backdrop -->
      <div
        class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
        aria-hidden="true"
        @click="onBackdropClick"
      ></div>
      <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

      <!-- Modal panel -->
      <div
        class="relative z-10 inline-block align-bottom bg-white dark:bg-gray-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full"
        :class="sizeClasses"
      >
        <!-- Header with icon and title -->
        <div class="bg-white dark:bg-gray-800 px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <div class="sm:flex sm:items-start">
            <!-- Icon -->
            <div
              v-if="icon"
              class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full sm:mx-0 sm:h-10 sm:w-10"
              :class="iconBgClass"
            >
              <component :is="icon" class="h-6 w-6" :class="iconClass" />
            </div>

            <!-- Content -->
            <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left flex-1">
              <h3
                v-if="title"
                class="text-lg leading-6 font-medium text-gray-900 dark:text-white"
                id="modal-title"
              >
                {{ title }}
              </h3>

              <div class="mt-2">
                <p v-if="message" class="text-sm text-gray-500 dark:text-gray-400">
                  {{ message }}
                </p>

                <!-- Item list -->
                <div v-if="items && items.length > 0" class="mt-3 max-h-32 overflow-y-auto">
                  <p v-if="itemsLabel" class="text-xs text-gray-500 dark:text-gray-400 mb-2">
                    {{ itemsLabel }}
                  </p>
                  <ul class="text-sm text-gray-600 dark:text-gray-400">
                    <li v-for="(item, index) in items" :key="index" class="py-1">
                      • {{ item }}
                    </li>
                  </ul>
                </div>

                <!-- Slot for custom content (forms, etc.) -->
                <slot name="content"></slot>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer with actions -->
        <div class="bg-gray-50 dark:bg-gray-700 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
          <!-- Primary action -->
          <button
            v-if="confirmText"
            @click="onConfirm"
            type="button"
            :disabled="confirmDisabled || loading"
            class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 text-base font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 sm:ml-3 sm:w-auto sm:text-sm cursor-pointer hover:shadow-md transition-all"
            :class="confirmButtonClass"
          >
            <RefreshCw v-if="loading" class="mr-2 h-4 w-4 animate-spin" />
            {{ confirmText }}
          </button>

          <!-- Cancel action -->
          <button
            v-if="cancelText"
            @click="onCancel"
            type="button"
            class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 dark:border-gray-600 shadow-sm px-4 py-2 bg-white dark:bg-gray-800 text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm cursor-pointer hover:shadow-md transition-all"
          >
            {{ cancelText }}
          </button>

          <!-- Custom actions slot -->
          <slot name="actions"></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { RefreshCw } from '@lucide/vue'

export default {
  name: 'Modal',
  components: {
    RefreshCw
  },
  props: {
    show: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: ''
    },
    message: {
      type: String,
      default: ''
    },
    icon: {
      type: [Object, Function],
      default: null
    },
    iconColor: {
      type: String,
      default: 'red', // red, green, yellow, blue, purple, gray
      validator: (value) => ['red', 'green', 'yellow', 'blue', 'purple', 'gray'].includes(value)
    },
    items: {
      type: Array,
      default: () => []
    },
    itemsLabel: {
      type: String,
      default: ''
    },
    confirmText: {
      type: String,
      default: 'Confirm'
    },
    cancelText: {
      type: String,
      default: 'Cancel'
    },
    confirmDisabled: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    },
    size: {
      type: String,
      default: 'md', // sm, md, lg
      validator: (value) => ['sm', 'md', 'lg'].includes(value)
    },
    closeOnBackdrop: {
      type: Boolean,
      default: true
    }
  },
  emits: ['confirm', 'cancel', 'close'],
  setup(props, { emit }) {
    const sizeClasses = computed(() => {
      const sizes = {
        sm: 'sm:max-w-sm',
        md: 'sm:max-w-lg',
        lg: 'sm:max-w-2xl'
      }
      return sizes[props.size] || sizes.md
    })

    const iconBgClass = computed(() => {
      const classes = {
        red: 'bg-red-100 dark:bg-red-900',
        green: 'bg-green-100 dark:bg-green-900',
        yellow: 'bg-yellow-100 dark:bg-yellow-900',
        blue: 'bg-blue-100 dark:bg-blue-900',
        purple: 'bg-purple-100 dark:bg-purple-900',
        gray: 'bg-gray-100 dark:bg-gray-900'
      }
      return classes[props.iconColor]
    })

    const iconClass = computed(() => {
      const classes = {
        red: 'text-red-600 dark:text-red-400',
        green: 'text-green-600 dark:text-green-400',
        yellow: 'text-yellow-600 dark:text-yellow-400',
        blue: 'text-blue-600 dark:text-blue-400',
        purple: 'text-purple-600 dark:text-purple-400',
        gray: 'text-gray-600 dark:text-gray-400'
      }
      return classes[props.iconColor]
    })

    const confirmButtonClass = computed(() => {
      const baseClasses = 'text-white'
      const colorClasses = {
        red: 'bg-red-600 hover:bg-red-700 focus:ring-red-500',
        green: 'bg-green-600 hover:bg-green-700 focus:ring-green-500',
        yellow: 'bg-yellow-600 hover:bg-yellow-700 focus:ring-yellow-500',
        blue: 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500',
        purple: 'bg-purple-600 hover:bg-purple-700 focus:ring-purple-500',
        gray: 'bg-gray-600 hover:bg-gray-700 focus:ring-gray-500'
      }
      const disabledClass = (props.confirmDisabled || props.loading) ? ' opacity-50 cursor-not-allowed' : ''
      return `${baseClasses} ${colorClasses[props.iconColor]}${disabledClass}`
    })

    const onConfirm = () => {
      emit('confirm')
    }

    const onCancel = () => {
      emit('cancel')
      emit('close')
    }

    const onBackdropClick = () => {
      if (props.closeOnBackdrop) {
        emit('close')
      }
    }

    return {
      sizeClasses,
      iconBgClass,
      iconClass,
      confirmButtonClass,
      onConfirm,
      onCancel,
      onBackdropClick
    }
  }
}
</script>
