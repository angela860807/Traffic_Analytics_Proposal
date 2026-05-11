import { createRouter, createWebHistory } from 'vue-router'
import MainView          from '@/views/MainView.vue'
import UsageView         from '@/views/UsageView.vue'
import IntroView         from '@/views/IntroView.vue'
import SupportView       from '@/views/SupportView.vue'
import LoginView         from '@/views/LoginView.vue'
import SignupView        from '@/views/SignupView.vue'
import RoadDashboardView from '@/views/RoadDashboardView.vue'
import { useAuth }       from '@/composables/useAuth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',              component: MainView          },
    { path: '/sub',           redirect: '/sub/usage'       },
    { path: '/sub/usage',     component: UsageView         },
    { path: '/sub/intro',     component: IntroView         },
    { path: '/sub/support',   component: SupportView       },
    { path: '/login',         component: LoginView         },
    { path: '/signup',        component: SignupView        },
    { path: '/dashboard',     component: RoadDashboardView },
  ],
  scrollBehavior: () => ({ top: 0 })
})

router.beforeEach((to) => {
  if (to.path === '/dashboard') {
    const { isLoggedIn, isAdmin } = useAuth()
    if (!isLoggedIn.value) return '/login'
    if (!isAdmin.value)    return '/'
  }
})

export default router
