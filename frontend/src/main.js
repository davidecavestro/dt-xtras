import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Dashboard from './components/Dashboard.vue'
import TaxonomyEditor from './components/TaxonomyEditor.vue'
import TaxonomyTreeView from './components/TaxonomyTreeView.vue'
import TagManager from './components/TagManager.vue'
import ProjectsList from './components/ProjectsList.vue'
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
    path: '/taxonomies',
    component: TaxonomyEditor,
    meta: { requiresAuth: true }
  },
  {
    path: '/taxonomy-view',
    component: TaxonomyTreeView,
    meta: { requiresAuth: true }
  },
  {
    path: '/tags',
    component: TagManager,
    meta: { requiresAuth: true }
  },
  {
    path: '/projects',
    component: ProjectsList,
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
