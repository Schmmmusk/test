<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessageBox } from 'element-plus'
import { Document, Wallet, Bell, DataAnalysis, Checked } from '@element-plus/icons-vue'
import { formatMoney } from '../utils/format'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const title = computed(() => route.meta.title || '互联网广告平台')

const menus = computed(() => {
  const items = [
    { path: '/ads', title: '我的广告', icon: Document },
    { path: '/recharge', title: '账户充值', icon: Wallet },
    { path: '/notifications', title: '站内信', icon: Bell },
    { path: '/report', title: '数据报表', icon: DataAnalysis }
  ]
  if (userStore.isAdmin) {
    items.push({ path: '/audit', title: '审核管理', icon: Checked })
  }
  return items
})

async function logout() {
  try {
    await ElMessageBox.confirm('确定退出登录吗？', '提示', { type: 'warning' })
    userStore.logout()
    router.push('/login')
  } catch {
    // 用户取消
  }
}
</script>

<template>
  <el-container class="layout">
    <el-aside width="210px" class="aside">
      <div class="brand">互联网广告平台</div>
      <el-menu :default-active="route.path" router background-color="#304156" text-color="#bfcbd9" active-text-color="#409eff">
        <el-menu-item v-for="m in menus" :key="m.path" :index="m.path">
          <el-icon><component :is="m.icon" /></el-icon>
          <span>{{ m.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span class="header-title">{{ title }}</span>
        <div class="header-user">
          <span class="balance money">余额：¥{{ formatMoney(userStore.user?.balance) }}</span>
          <span class="nickname">{{ userStore.user?.nickname || userStore.user?.phone }}</span>
          <el-button text type="primary" @click="logout">退出</el-button>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout { min-height: 100vh; }
.aside { background: #304156; }
.brand {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 17px;
  font-weight: 500;
  border-bottom: 1px solid #3d4d63;
}
.el-menu { border-right: none; }
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}
.header-title { font-size: 18px; font-weight: 500; }
.header-user { display: flex; align-items: center; gap: 16px; }
.balance { color: #606266; }
.nickname { color: #303133; }
.main { background: #f5f7fa; padding: 0; }
</style>
