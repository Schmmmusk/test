<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { createAd } from '../api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const form = reactive({
  title: '',
  content: '',
  image_url: '',
  landing_url: '',
  daily_budget: null
})

async function submit() {
  if (!form.title.trim()) {
    ElMessage.warning('请填写广告标题')
    return
  }
  const budget = Number(form.daily_budget)
  if (!form.daily_budget || !Number.isFinite(budget) || budget <= 0) {
    ElMessage.warning('请填写有效的日预算')
    return
  }
  loading.value = true
  try {
    await createAd({
      title: form.title.trim(),
      content: form.content,
      image_url: form.image_url,
      landing_url: form.landing_url,
      daily_budget: budget.toFixed(2)
    })
    ElMessage.success('广告已提交审核')
    router.push('/ads')
  } catch {
    // 统一由拦截器提示
  } finally {
    loading.value = false
  }
}

function cancel() {
  router.push('/ads')
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h2>新建广告</h2>
    </div>
    <el-card class="form-card">
      <el-form :model="form" label-width="100px">
        <el-form-item label="广告标题" required>
          <el-input v-model="form.title" placeholder="请输入广告标题" maxlength="100" />
        </el-form-item>
        <el-form-item label="广告文案">
          <el-input v-model="form.content" type="textarea" :rows="3" placeholder="请输入广告文案" />
        </el-form-item>
        <el-form-item label="图片地址">
          <el-input v-model="form.image_url" placeholder="完整图片 URL，选填" />
        </el-form-item>
        <el-form-item label="落地页地址">
          <el-input v-model="form.landing_url" placeholder="完整落地页 URL，选填" />
        </el-form-item>
        <el-form-item label="日预算" required>
          <el-input-number v-model="form.daily_budget" :min="0.01" :precision="2" :step="10" controls-position="right" />
          <span class="hint">元 / 天</span>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="submit">提交审核</el-button>
          <el-button @click="cancel">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.form-card { max-width: 680px; }
.hint { margin-left: 10px; color: #909399; }
</style>
