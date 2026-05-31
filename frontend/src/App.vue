<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors flex">
    <!-- Mobile Sidebar Backdrop -->
    <div
      v-if="sidebarOpen && !isLargeScreen"
      @click="closeSidebarOnMobile"
      class="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
    ></div>

    <!-- Sidebar -->
    <div v-if="$route.path !== '/login'" :class="[
      'fixed inset-y-0 left-0 bg-white dark:bg-gray-800 shadow-lg transform transition-all duration-300 ease-in-out overflow-hidden',
      { 'translate-x-0': sidebarOpen, '-translate-x-full': !sidebarOpen && !isLargeScreen },
      { 'lg:w-64': sidebarOpen, 'lg:w-16': !sidebarOpen },
      { 'z-50': sidebarOpen, 'z-30': !sidebarOpen }
    ]">
      <!-- Sidebar Header -->
      <div class="flex items-center justify-between h-16 px-4 border-b border-gray-200 dark:border-gray-700">
        <div :class="[
          'flex items-center flex-1 min-w-0',
          { 'pl-2': !sidebarOpen }
        ]">
          <div @click="toggleSidebar" class="cursor-pointer">
            <LogoWithText
              :size="sidebarOpen ? 'medium' : 'small'"
              :variant="isDark ? 'dark' : 'default'"
              :showText="sidebarOpen"
            />
          </div>
        </div>
        <button
          @click="toggleSidebar"
          class="lg:hidden p-2 rounded-md text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer hover:shadow-md transition-all"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Navigation -->
      <nav :class="[
        'flex-1 px-4 py-6 space-y-2',
        { 'px-2': !sidebarOpen }
      ]">
        <router-link
          to="/"
          class="flex items-center text-sm font-medium rounded-md transition-all duration-200 cursor-pointer"
          :class="[
            $route.path === '/'
              ? 'bg-blue-100 text-blue-700 dark:bg-gray-700 dark:text-blue-300 shadow-md'
              : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-md',
            sidebarOpen ? 'px-3' : 'px-2 justify-center'
          ]"
          @click="closeSidebarOnMobile"
        >
          <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
          </svg>
          <span :class="{ 'lg:hidden': !sidebarOpen, 'ml-3': sidebarOpen }">Dashboard</span>
        </router-link>

        <router-link
          to="/projects"
          class="flex items-center text-sm font-medium rounded-md transition-all duration-200 cursor-pointer"
          :class="[
            $route.path.startsWith('/projects')
              ? 'bg-blue-100 text-blue-700 dark:bg-gray-700 dark:text-blue-300 shadow-md'
              : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-md',
            sidebarOpen ? 'px-3' : 'px-2 justify-center'
          ]"
          @click="closeSidebarOnMobile"
        >
          <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
          </svg>
          <span :class="{ 'lg:hidden': !sidebarOpen, 'ml-3': sidebarOpen }">Project Center</span>
        </router-link>

        <router-link
          to="/tags"
          class="flex items-center text-sm font-medium rounded-md transition-all duration-200 cursor-pointer"
          :class="[
            $route.path === '/tags'
              ? 'bg-blue-100 text-blue-700 dark:bg-gray-700 dark:text-blue-300 shadow-md'
              : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-md',
            sidebarOpen ? 'px-3' : 'px-2 justify-center'
          ]"
          @click="closeSidebarOnMobile"
        >
          <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
          </svg>
          <span :class="{ 'lg:hidden': !sidebarOpen, 'ml-3': sidebarOpen }">Tag Center</span>
        </router-link>

        <router-link
          to="/tags-graph"
          class="flex items-center text-sm font-medium rounded-md transition-all duration-200 cursor-pointer"
          :class="[
            $route.path === '/tags-graph'
              ? 'bg-gray-700 dark:bg-gray-700 dark:text-blue-300 shadow-md'
              : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-md',
            sidebarOpen ? 'px-3' : 'px-2 justify-center'
          ]"
          @click="closeSidebarOnMobile"
        >
          <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002 2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2 2z"></path>
          </svg>
          <span :class="{ 'lg:hidden': !sidebarOpen, 'ml-3': sidebarOpen }">Tags Graph</span>
        </router-link>

        <router-link
          to="/taxonomies"
          class="flex items-center text-sm font-medium rounded-md transition-all duration-200 cursor-pointer"
          :class="[
            $route.path === '/taxonomies'
              ? 'bg-gray-700 dark:bg-gray-700 dark:text-blue-300 shadow-md'
              : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-md',
            sidebarOpen ? 'px-3' : 'px-2 justify-center'
          ]"
          @click="closeSidebarOnMobile"
        >
          <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7a4 4 0 00-4 4h7M4 6h16"></path>
          </svg>
          <span :class="{ 'lg:hidden': !sidebarOpen, 'ml-3': sidebarOpen }">Taxonomy Center</span>
        </router-link>

        <router-link
          to="/tag-bulk-actions"
          class="flex items-center text-sm font-medium rounded-md transition-all duration-200 cursor-pointer"
          :class="[
            $route.path === '/tag-bulk-actions'
              ? 'bg-blue-100 text-blue-700 dark:bg-gray-700 dark:text-blue-300 shadow-md'
              : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-md',
            sidebarOpen ? 'px-3' : 'px-2 justify-center'
          ]"
          @click="closeSidebarOnMobile"
        >
          <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
          </svg>
          <span :class="{ 'lg:hidden': !sidebarOpen, 'ml-3': sidebarOpen }">Tag Bulk Actions</span>
        </router-link>

        <router-link
          to="/project-bulk-actions"
          class="flex items-center text-sm font-medium rounded-md transition-all duration-200 cursor-pointer"
          :class="[
            $route.path === '/project-bulk-actions'
              ? 'bg-blue-100 text-blue-700 dark:bg-gray-700 dark:text-blue-300 shadow-md'
              : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-md',
            sidebarOpen ? 'px-3' : 'px-2 justify-center'
          ]"
          @click="closeSidebarOnMobile"
        >
          <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path>
          </svg>
          <span :class="{ 'lg:hidden': !sidebarOpen, 'ml-3': sidebarOpen }">Project Bulk Actions</span>
        </router-link>

      </nav>

      <!-- User Section -->
      <div :class="[
        'border-t border-gray-200 dark:border-gray-700 px-4 py-4',
        { 'lg:hidden': !sidebarOpen }
      ]">
        <div class="flex items-center justify-between">
          <div v-if="isAuthenticated" class="flex items-center space-x-3">
            <div class="shrink-0">
              <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                <span class="text-white text-sm font-medium">
                  {{ currentUser.charAt(0).toUpperCase() }}
                </span>
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 dark:text-white truncate">
                {{ currentUser }}
              </p>
              <button
                @click="handleLogout"
                class="text-xs text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200 cursor-pointer hover:underline transition-all"
              >
                Logout
              </button>
            </div>
          </div>
          <router-link
            v-else
            to="/login"
            class="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 hover:bg-blue-100 dark:hover:bg-blue-900 rounded-md transition-all duration-200 cursor-pointer hover:shadow-md"
            @click="closeSidebarOnMobile"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path>
            </svg>
            <span>Login</span>
          </router-link>
        </div>
      </div>

      <!-- Theme Toggle -->
      <div :class="[
        'border-t border-gray-200 dark:border-gray-700 px-4 py-4',
        { 'lg:hidden': !sidebarOpen }
      ]">
        <button
          @click="toggleDarkMode"
          class="w-full flex items-center justify-center px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 transition-all duration-200 cursor-pointer hover:shadow-md"
        >
          <svg v-if="isDark" class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>
          </svg>
          <svg v-else class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
          </svg>
          {{ isDark ? 'Light Mode' : 'Dark Mode' }}
        </button>
      </div>

      <!-- Bottom Toggle Handle (always visible) -->
      <div class="hidden lg:flex fixed bottom-0 left-0 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 z-50" :class="sidebarOpen ? 'w-64' : 'w-16'">
        <button
          @click="toggleSidebar"
          class="w-full flex items-center justify-center p-3 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200 cursor-pointer hover:shadow-md"
          :title="sidebarOpen ? 'Collapse Sidebar' : 'Expand Sidebar'"
        >
          <svg v-if="sidebarOpen" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7"></path>
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
          </svg>
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div :class="['flex-1 transition-all duration-300 ease-in-out z-10', sidebarOpen ? 'ml-64 lg:ml-64' : 'ml-16 lg:ml-16']">
      <!-- Mobile Header -->
      <header v-if="$route.path !== '/login'" class="lg:hidden bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center">
          <button
            @click="toggleSidebar"
            class="p-2 rounded-md text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer hover:shadow-md transition-all"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
            </svg>
          </button>
          <div @click="toggleSidebar" class="cursor-pointer">
            <LogoWithText
              size="small"
              :variant="isDark ? 'dark' : 'default'"
            />
          </div>
        </div>
      </header>

      <!-- Main Content Area -->
      <main class="flex-1 overflow-auto">
        <div class="py-6 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
          <router-view />
        </div>
      </main>
    </div>

    <!-- Toast Container -->
    <ToastContainer />
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import authService from './services/auth'
import { getConfig } from './config.js'
import LogoWithText from './components/LogoWithText.vue'
import ToastContainer from './components/ToastContainer.vue'
import { createLogger } from './utils/logger'

export default {
  name: 'App',
  components: {
    LogoWithText,
    ToastContainer
  },
  setup() {
    const logger = createLogger('app')
    const router = useRouter()
    const isDark = ref(false)
    const isAuthenticated = ref(false)
    const currentUser = ref('')
    const sidebarOpen = ref(true) // Start with sidebar open
    const screenWidth = ref(window.innerWidth)

    // Computed properties
    const isLargeScreen = computed(() => screenWidth.value >= 1024)

    // Update screen width on window resize
    const updateScreenWidth = () => {
      screenWidth.value = window.innerWidth
    }

    onMounted(() => {
      window.addEventListener('resize', updateScreenWidth)
    })

    onUnmounted(() => {
      window.removeEventListener('resize', updateScreenWidth)
    })

    const checkAuth = () => {
      isAuthenticated.value = authService.isAuthenticated()
      // Extract username from stored token or use default
      if (isAuthenticated.value) {
        currentUser.value = authService.getUsername() || 'Unknown User'
      } else {
        currentUser.value = ''
      }
    }

    const handleLogout = async () => {
      try {
        // Call backend logout endpoint to invalidate token
        await authService.logout()
      } catch (error) {
        logger.error('Logout error:', error)
      } finally {
        // Always clear local auth state
        authService.logout()
        isAuthenticated.value = false
        currentUser.value = ''
        router.push('/login')
      }
    }

    const toggleDarkMode = () => {
      isDark.value = !isDark.value
      updateTheme()
    }

    const toggleSidebar = () => {
      sidebarOpen.value = !sidebarOpen.value
    }

    const closeSidebarOnMobile = () => {
      if (window.innerWidth < 1024) {
        sidebarOpen.value = false
      }
    }

    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        // On desktop, keep sidebar state as is (don't auto-close)
      } else {
        // On mobile, close sidebar
        sidebarOpen.value = false
      }
    }

    const updateTheme = () => {
      if (isDark.value) {
        document.documentElement.classList.add('dark')
        localStorage.setItem('theme', 'dark')
      } else {
        document.documentElement.classList.remove('dark')
        localStorage.setItem('theme', 'light')
      }
    }

    onMounted(() => {
      // Configuration is now loaded synchronously from script tag
      logger.info('Configuration loaded:', getConfig())

      // Check for saved theme preference or default to light mode
      const savedTheme = localStorage.getItem('theme')
      isDark.value = savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)
      updateTheme()

      // Check authentication status after config is loaded
      checkAuth()

      // Close sidebar on window resize
      window.addEventListener('resize', handleResize)
    })

    // Watch for route changes to update auth state
    watch(() => router.currentRoute.value, () => {
      checkAuth()
      // Close sidebar on route change on mobile
      closeSidebarOnMobile()
    })

    return {
      isDark,
      isAuthenticated,
      currentUser,
      sidebarOpen,
      screenWidth,
      isLargeScreen,
      handleLogout,
      toggleDarkMode,
      toggleSidebar,
      closeSidebarOnMobile,
      handleResize,
      checkAuth
    }
  }
}
</script>
