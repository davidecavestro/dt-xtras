import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Dashboard from './components/Dashboard.vue'
import TaxonomyCenter from './components/TaxonomyCenter.vue'
import TagsGraph from './components/TagsGraph.vue'
import TagCenter from './components/TagCenter.vue'
import TagBulkActions from './components/TagBulkActions.vue'
import ProjectsList from './components/ProjectsList.vue'
import ProjectsGrid from './components/ProjectsGrid.vue'
import ProjectCenter from './components/ProjectCenter.vue'
import ProjectBulkActions from './components/ProjectBulkActions.vue'
import VulnerabilitiesList from './components/VulnerabilitiesList.vue'
import Login from './components/Login.vue'
import authService from './services/auth'
import { createLogger } from './utils/logger'

import './style.css'

const logger = createLogger('router')

const routes = [
  {
    path: '/login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/tags-graph',
    component: TagsGraph,
    meta: { requiresAuth: true }
  },
  {
    path: '/taxonomies',
    component: TaxonomyCenter,
    meta: { requiresAuth: true }
  },
  {
    path: '/tags',
    component: TagCenter,
    meta: { requiresAuth: true }
  },
  {
    path: '/tag-bulk-actions',
    name: 'TagBulkActions',
    component: TagBulkActions,
    meta: { requiresAuth: true }
  },
  {
    path: '/projects',
    name: 'ProjectCenter',
    component: ProjectCenter,
    meta: { requiresAuth: true }
  },
  {
    path: '/projects-list',
    redirect: '/projects'
  },
  {
    path: '/projects-grid',
    redirect: '/projects'
  },
  {
    path: '/project-bulk-actions',
    name: 'ProjectBulkActions',
    component: ProjectBulkActions,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard for authentication
router.beforeEach((to, from) => {
  try {
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

    if (requiresAuth && !authService.isAuthenticated()) {
      return '/login'
    } else {
      return true
    }
  } catch (error) {
    logger.error('Navigation guard error:', error)
    return false
  }
})

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.mount('#app')
