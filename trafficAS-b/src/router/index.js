import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

/* 라우트 lazy loading — 메인 페이지 방문자는 대시보드/ECharts/Leaflet 코드를 받지 않음 */
const MainView          = () => import('@/views/MainView.vue')
const UsageView         = () => import('@/views/UsageView.vue')
const IntroView         = () => import('@/views/IntroView.vue')
const SupportView       = () => import('@/views/SupportView.vue')
const LoginView         = () => import('@/views/LoginView.vue')
const SignupView        = () => import('@/views/SignupView.vue')
const RoadDashboardView = () => import('@/views/RoadDashboardView.vue')

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
