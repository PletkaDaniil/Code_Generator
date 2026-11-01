import { createRouter, createWebHistory } from 'vue-router'
import PublicView from './views/PublicView.vue'
import SecureView from './views/SecureView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: PublicView },
    { path: '/secure', component: SecureView },
  ],
})