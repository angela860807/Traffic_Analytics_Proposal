import { createRouter, createWebHistory } from 'vue-router'
import MainView from '@/views/MainView.vue'
import SubView  from '@/views/SubView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',    component: MainView },
    { path: '/sub', component: SubView  },
  ],
  scrollBehavior: () => ({ top: 0 })
})
