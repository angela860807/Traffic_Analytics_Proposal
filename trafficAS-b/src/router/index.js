import { createRouter, createWebHistory } from 'vue-router'
import MainView      from '@/views/MainView.vue'
import UsageView     from '@/views/UsageView.vue'
import IntroView     from '@/views/IntroView.vue'
import SupportView   from '@/views/SupportView.vue'
import LoginView     from '@/views/LoginView.vue'
import SignupView    from '@/views/SignupView.vue'
import DashboardView from '@/views/DashboardView.vue'
import { useAuth }   from '@/composables/useAuth'

const ControlView   = () => import('@/views/admin/ControlView.vue')
const ReviewView    = () => import('@/views/admin/ReviewView.vue')
const AnalyticsView = () => import('@/views/admin/AnalyticsView.vue')
const OpsView       = () => import('@/views/admin/OpsView.vue')
const SuperView     = () => import('@/views/admin/SuperView.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',            component: MainView      },
    { path: '/home',        component: MainView      },
    { path: '/sub',         redirect: '/sub/usage'   },
    { path: '/sub/usage',   component: UsageView     },
    { path: '/sub/intro',   component: IntroView     },
    { path: '/sub/support', component: SupportView   },
    { path: '/login',       component: LoginView     },
    { path: '/signup',      component: SignupView    },
    { path: '/dashboard',   component: DashboardView },
    { path: '/admin',           redirect: '/admin/super'     },
    { path: '/admin/reports',   redirect: '/admin/super'     },
    { path: '/admin/control',   component: ControlView       },
    { path: '/admin/review',    component: ReviewView        },
    { path: '/admin/analytics', component: AnalyticsView     },
    { path: '/admin/ops',       component: OpsView           },
    { path: '/admin/super',     component: SuperView         },
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
