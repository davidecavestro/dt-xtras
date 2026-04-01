import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Dashboard from './components/Dashboard.vue'
import TaxonomyEditor from './components/TaxonomyEditor.vue'
import TaxonomyVisualization from './components/TaxonomyVisualization.vue'
import TagManager from './components/TagManager.vue'
import TagBulkActions from './components/TagBulkActions.vue'
import ProjectsList from './components/ProjectsList.vue'
import ProjectsGrid from './components/ProjectsGrid.vue'
import Projects from './components/Projects.vue'
import ProjectBulkActions from './components/ProjectCleanup.vue'
import VulnerabilitiesList from './components/VulnerabilitiesList.vue'
import Login from './components/Login.vue'
import authService from './services/auth'

import './style.css'

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
    path: '/dependency-graph',
    component: TaxonomyVisualization,
    meta: { requiresAuth: true }
  },
  {
    path: '/taxonomy-builder',
    component: TaxonomyEditor,
    meta: { requiresAuth: true }
  },
  {
    path: '/tags',
    component: TagManager,
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
    name: 'Projects',
    component: Projects,
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
    path: '/cleanup',
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
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !authService.isAuthenticated()) {
    next('/login')
  } else if (to.path === '/login' && authService.isAuthenticated()) {
    next('/')
  } else {
    next()
  }
})

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.mount('#app')
