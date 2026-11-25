<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { login } from '../api'
import { useUserStore } from '../stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const loading = ref(false)
const form = reactive({ phone: '', password: '' })

async function submit() {
  loading.value = true
  try {
    const res = await login(form)
    userStore.setLogin(res.token, res.user)
    router.push(route.query.redirect || '/ads')
  } catch {
    // 错误信息由响应拦截器统一提示
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <el-card class="auth-card">
      <h2 class="title">互联网广告平台</h2>
      <p class="subtitle">账号登录</p>
      <el-form :model="form" label-width="70px" @keyup.enter="submit">
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="请输入手机号" autocomplete="username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password autocomplete="current-password" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" class="submit" @click="submit">登录</el-button>
        </el-form-item>
      </el-form>
      <div class="footer">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
}
.auth-card { width: 400px; }
.title { margin: 0; text-align: center; font-size: 22px; font-weight: 500; }
.subtitle { margin: 6px 0 24px; text-align: center; color: #909399; }
.submit { width: 100%; }
.footer { text-align: center; color: #606266; font-size: 14px; }
</style>
