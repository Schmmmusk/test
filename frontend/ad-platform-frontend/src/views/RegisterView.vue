<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '../api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const form = reactive({ phone: '', password: '', nickname: '' })

async function submit() {
  if (!/^\d{11}$/.test(form.phone)) {
    ElMessage.warning('请输入 11 位手机号')
    return
  }
  if (form.password.length < 6) {
    ElMessage.warning('密码长度不能少于 6 位')
    return
  }
  loading.value = true
  try {
    await register(form)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
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
      <p class="subtitle">注册账号</p>
      <el-form :model="form" label-width="70px" @keyup.enter="submit">
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="请输入 11 位手机号" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="至少 6 位" show-password />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="form.nickname" placeholder="选填" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" class="submit" @click="submit">注册</el-button>
        </el-form-item>
      </el-form>
      <div class="footer">
        已有账号？<router-link to="/login">返回登录</router-link>
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
