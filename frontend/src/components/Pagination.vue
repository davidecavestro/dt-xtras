<template>
  <div class="flex items-center justify-between px-4 py-3 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
    <div class="flex items-center">
      <span class="text-sm text-gray-700 dark:text-gray-300">
        Showing
        <span class="font-medium">{{ startItem }}</span>
        to
        <span class="font-medium">{{ endItem }}</span>
        of
        <span class="font-medium">{{ totalItems }}</span>
        results
      </span>
    </div>
    
    <div class="flex items-center space-x-2">
      <!-- Page size selector -->
      <div class="flex items-center space-x-2">
        <label class="text-sm text-gray-700 dark:text-gray-300">Show:</label>
        <select
          :value="pageSize"
          @change="handlePageSizeChange"
          class="rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
        >
          <option v-for="size in pageSizeOptions" :key="size" :value="size">
            {{ size }}
          </option>
        </select>
      </div>

      <!-- Navigation buttons -->
      <div class="flex items-center space-x-1">
        <button
          @click="goToFirstPage"
          :disabled="currentPage === 1"
          class="relative inline-flex items-center px-2 py-1 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ChevronsLeft class="w-4 h-4" />
        </button>
        
        <button
          @click="goToPreviousPage"
          :disabled="currentPage === 1"
          class="relative inline-flex items-center px-2 py-1 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ChevronLeft class="w-4 h-4" />
        </button>

        <!-- Page numbers -->
        <div class="flex items-center space-x-1">
          <button
            v-for="page in visiblePages"
            :key="page"
            @click="goToPage(page)"
            :class="[
              'relative inline-flex items-center px-3 py-1 rounded-md text-sm font-medium',
              page === currentPage
                ? 'z-10 bg-blue-50 dark:bg-blue-900/30 border-blue-500 text-blue-600 dark:text-blue-200'
                : 'border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-600'
            ]"
          >
            {{ page }}
          </button>
        </div>

        <button
          @click="goToNextPage"
          :disabled="currentPage === totalPages"
          class="relative inline-flex items-center px-2 py-1 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ChevronRight class="w-4 h-4" />
        </button>
        
        <button
          @click="goToLastPage"
          :disabled="currentPage === totalPages"
          class="relative inline-flex items-center px-2 py-1 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ChevronsRight class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { 
  ChevronLeft, 
  ChevronRight, 
  ChevronsLeft, 
  ChevronsRight 
} from 'lucide-vue-next'

export default {
  name: 'Pagination',
  components: {
    ChevronLeft,
    ChevronRight,
    ChevronsLeft,
    ChevronsRight
  },
  props: {
    currentPage: {
      type: Number,
      required: true,
      default: 1
    },
    pageSize: {
      type: Number,
      required: true,
      default: 20
    },
    totalItems: {
      type: Number,
      required: true,
      default: 0
    },
    pageSizeOptions: {
      type: Array,
      default: () => [10, 20, 50, 100]
    },
    maxVisiblePages: {
      type: Number,
      default: 5
    }
  },
  emits: ['page-change', 'page-size-change'],
  setup(props, { emit }) {
    const totalPages = computed(() => {
      return Math.ceil(props.totalItems / props.pageSize) || 1
    })

    const startItem = computed(() => {
      if (props.totalItems === 0) return 0
      return (props.currentPage - 1) * props.pageSize + 1
    })

    const endItem = computed(() => {
      const end = props.currentPage * props.pageSize
      return Math.min(end, props.totalItems)
    })

    const visiblePages = computed(() => {
      const total = totalPages.value
      const current = props.currentPage
      const maxVisible = props.maxVisiblePages
      
      if (total <= maxVisible) {
        return Array.from({ length: total }, (_, i) => i + 1)
      }

      let start = Math.max(1, current - Math.floor(maxVisible / 2))
      let end = Math.min(total, start + maxVisible - 1)

      if (end - start < maxVisible - 1) {
        start = Math.max(1, end - maxVisible + 1)
      }

      return Array.from({ length: end - start + 1 }, (_, i) => start + i)
    })

    const goToPage = (page) => {
      if (page >= 1 && page <= totalPages.value && page !== props.currentPage) {
        emit('page-change', page)
      }
    }

    const goToFirstPage = () => goToPage(1)
    const goToLastPage = () => goToPage(totalPages.value)
    const goToPreviousPage = () => goToPage(props.currentPage - 1)
    const goToNextPage = () => goToPage(props.currentPage + 1)

    const handlePageSizeChange = (event) => {
      const newPageSize = parseInt(event.target.value)
      emit('page-size-change', newPageSize)
    }

    return {
      totalPages,
      startItem,
      endItem,
      visiblePages,
      goToPage,
      goToFirstPage,
      goToLastPage,
      goToPreviousPage,
      goToNextPage,
      handlePageSizeChange
    }
  }
}
</script>
