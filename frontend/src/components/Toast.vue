<template>
  <transition
    enter-active-class="transform ease-out duration-300 transition"
    enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
    enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
    leave-active-class="transition ease-in duration-100"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="show"
      :class="[
        'min-w-80 max-w-md w-full shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden',
        'bg-white dark:bg-gray-800',
        type === 'success' ? 'border-l-4 border-green-400' : 'border-l-4 border-red-400'
      ]"
    >
      <div class="p-4">
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <!-- Success Icon -->
            <svg
              v-if="type === 'success'"
              class="h-6 w-6 text-green-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <!-- Error Icon -->
            <svg
              v-else
              class="h-6 w-6 text-red-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <div class="ml-3 flex-1 pt-0.5">
            <p
              :class="[
                'text-sm font-medium break-words',
                type === 'success' ? 'text-green-900 dark:text-green-100' : 'text-red-900 dark:text-red-100'
              ]"
            >
              {{ title }}
            </p>
            <p
              v-if="message"
              :class="[
                'mt-1 text-sm break-words',
                type === 'success' ? 'text-green-700 dark:text-green-200' : 'text-red-700 dark:text-red-200'
              ]"
            >
              {{ message }}
            </p>
          </div>
          <div class="ml-4 flex-shrink-0 flex">
            <button
              @click="close"
              class="rounded-md inline-flex text-gray-400 hover:text-gray-500 dark:text-gray-500 dark:hover:text-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:focus:ring-offset-gray-800"
            >
              <span class="sr-only">Close</span>
              <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fill-rule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clip-rule="evenodd"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'Toast',
  props: {
    type: {
      type: String,
      default: 'success',
      validator: (value) => ['success', 'error'].includes(value)
    },
    title: {
      type: String,
      required: true
    },
    message: {
      type: String,
      default: ''
    },
    duration: {
      type: Number,
      default: 3000
    }
  },
  setup(props) {
    const show = ref(false)
    let timeoutId = null

    const close = () => {
      show.value = false
      if (timeoutId) {
        clearTimeout(timeoutId)
        timeoutId = null
      }
    }

    onMounted(() => {
      show.value = true
      if (props.duration > 0) {
        timeoutId = setTimeout(() => {
          close()
        }, props.duration)
      }
    })

    return {
      show,
      close
    }
  }
}
</script>
