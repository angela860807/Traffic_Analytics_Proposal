import { createRouter, createWebHistory } from 'vue-router'
import MainView    from '@/views/MainView.vue'
import UsageView   from '@/views/UsageView.vue'
import IntroView   from '@/views/IntroView.vue'
import SupportView from '@/views/SupportView.vue'
import LoginView   from '@/views/LoginView.vue'
import SignupView  from '@/views/SignupView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',             component: MainView    },
    { path: '/sub',          redirect: '/sub/usage' },
    { path: '/sub/usage',    component: UsageView   },
    { path: '/sub/intro',    component: IntroView   },
    { path: '/sub/support',  component: SupportView },
    { path: '/login',        component: LoginView   },
    { path: '/signup',       component: SignupView  },
  ],
  scrollBehavior: () => ({ top: 0 })
})
