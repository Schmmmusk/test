import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'
import MainLayout from '../layouts/MainLayout.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import AdsView from '../views/AdsView.vue'
import AdCreateView from '../views/AdCreateView.vue'
import RechargeView from '../views/RechargeView.vue'
import NotificationsView from '../views/NotificationsView.vue'
import ReportView from '../views/ReportView.vue'
import AuditView from '../views/AuditView.vue'

const routes = [
  { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
  { path: '/register', name: 'register', component: RegisterView, meta: { public: true } },
  {
    path: '/',
    component: MainLayout,
    redirect: '/ads',
    children: [
      { path: 'ads', name: 'ads', component: AdsView, meta: { title: '我的广告' } },
      { path: 'ads/new', name: 'ad-create', component: AdCreateView, meta: { title: '新建广告' } },
      { path: 'recharge', name: 'recharge', component: RechargeView, meta: { title: '账户充值' } },
      { path: 'notifications', name: 'notifications', component: NotificationsView, meta: { title: '站内信' } },
      { path: 'report', name: 'report', component: ReportView, meta: { title: '数据报表' } },
      { path: 'audit', name: 'audit', component: AuditView, meta: { title: '审核管理', admin: true } }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  const userStore = useUserStore()
  if (to.meta.public) {
    if (userStore.isLoggedIn && to.path === '/login') return '/ads'
    return true
  }
  if (!userStore.isLoggedIn) return { path: '/login', query: { redirect: to.fullPath } }
  if (to.meta.admin && !userStore.isAdmin) return '/ads'
  return true
})

export default router
