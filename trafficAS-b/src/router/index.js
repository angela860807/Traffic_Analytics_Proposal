import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const MainView          = () => import('@/views/MainView.vue')
const IntroView         = () => import('@/views/IntroView.vue')
const SupportView       = () => import('@/views/SupportView.vue')
const LoginView         = () => import('@/views/LoginView.vue')
const SignupView        = () => import('@/views/SignupView.vue')

const ControlView   = () => import('@/views/admin/ControlView.vue')
const ReviewView    = () => import('@/views/admin/ReviewView.vue')
const AnalyticsView = () => import('@/views/admin/AnalyticsView.vue')
const OpsView       = () => import('@/views/admin/OpsView.vue')
const SuperView     = () => import('@/views/admin/SuperView.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',              component: MainView          },
    { path: '/sub',           redirect: '/sub/intro'       },
    { path: '/sub/intro',     component: IntroView         },
    { path: '/sub/support',   component: SupportView       },
    { path: '/login',         component: LoginView         },
    { path: '/signup',        component: SignupView        },
    { path: '/admin',         redirect: '/admin/super'     },
    { path: '/admin/reports',   redirect: '/admin/super'    },
    { path: '/admin/control',   component: ControlView   },
    { path: '/admin/review',    component: ReviewView    },
    { path: '/admin/analytics', component: AnalyticsView },
    { path: '/admin/ops',       component: OpsView       },
    { path: '/admin/super',     component: SuperView     },
  ],
  scrollBehavior: () => ({ top: 0 })
})

router.beforeEach((to) => {
  const protectedPaths = ['/admin']
  if (protectedPaths.some(p => to.path.startsWith(p))) {
    const { isLoggedIn, isAdmin } = useAuth()
    if (!isLoggedIn.value) return '/login'
    if (!isAdmin.value)    return '/'
  }
})

export default router
