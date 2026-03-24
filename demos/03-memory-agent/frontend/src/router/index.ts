/**
 * Vue Router 配置
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { Router } from 'vue-router'

// 路由配置
const routes = [
  {
    path: '/auth',
    name: 'Auth',
    component: () => import('@/components/AuthPage.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/auth'
  }
]

// 创建路由
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()

  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !authStore.isAuthenticated()) {
    // 需要认证但未登录，跳转到登录页
    next('/auth')
  } else if (!requiresAuth && authStore.isAuthenticated() && to.path === '/auth') {
    // 已登录但访问登录页，跳转到首页
    next('/')
  } else {
    next()
  }
})

export default router
