<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
    <nav class="bg-white dark:bg-gray-800 shadow-sm border-b dark:border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-semibold text-gray-900 dark:text-white">dt-xtras</h1>
          </div>
          <div class="flex items-center space-x-4">
            <router-link
              to="/"
              class="px-3 py-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700"
              :class="{ 'bg-gray-200 dark:bg-gray-700': $route.path === '/' }"
            >
              Dashboard
            </router-link>
            <router-link
              to="/projects"
              class="px-3 py-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700"
              :class="{ 'bg-gray-200 dark:bg-gray-700': $route.path === '/projects' }"
            >
              Projects
            </router-link>
            <router-link
              to="/tags"
              class="px-3 py-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700"
              :class="{ 'bg-gray-200 dark:bg-gray-700': $route.path === '/tags' }"
            >
              Tag Manager
            </router-link>

            <router-link
              to="/taxonomies"
              class="px-3 py-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700"
              :class="{ 'bg-gray-200 dark:bg-gray-700': $route.path === '/taxonomies' }"
            >
              Taxonomy Editor
            </router-link>

            <!-- Authentication status -->
            <div class="flex items-center space-x-2">
              <div v-if="isAuthenticated" class="flex items-center space-x-2">
                <span class="text-sm text-gray-600 dark:text-gray-400">
                  {{ currentUser }}
                </span>
                <button
                  @click="handleLogout"
                  class="px-3 py-2 rounded-md text-sm font-medium text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200 hover:bg-red-100 dark:hover:bg-red-900"
                >
                  Logout
                </button>
              </div>
              <router-link
                v-else
                to="/login"
                class="px-3 py-2 rounded-md text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 hover:bg-blue-100 dark:hover:bg-blue-900"
              >
                Login
              </router-link>
            </div>

            <button
              @click="toggleDarkMode"
              class="p-2 rounded-md text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
              title="Toggle dark mode"
            >
              <svg v-if="isDark" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <router-view />
    </main>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import authService from './services/auth'

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    const isDark = ref(false)
    const isAuthenticated = ref(false)
    const currentUser = ref('')

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
        console.error('Logout error:', error)
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
      // Check for saved theme preference or default to light mode
      const savedTheme = localStorage.getItem('theme')
      isDark.value = savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)
      updateTheme()

      // Check authentication status
      checkAuth()
    })

    // Watch for route changes to update auth state
    watch(() => router.currentRoute.value, () => {
      checkAuth()
    })

    return {
      isDark,
      isAuthenticated,
      currentUser,
      handleLogout,
      toggleDarkMode,
      checkAuth
    }
  }
}
</script>
