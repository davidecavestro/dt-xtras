import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Dashboard from './components/Dashboard.vue'
import TaxonomyEditor from './components/TaxonomyEditor.vue'

import './style.css'

const routes = [
  { path: '/', component: Dashboard },
  { path: '/taxonomies', component: TaxonomyEditor }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

createApp(App).use(router).mount('#app')
