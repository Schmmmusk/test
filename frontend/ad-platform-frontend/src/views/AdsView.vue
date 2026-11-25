<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getMyAds } from '../api'
import { formatStatus, formatMoney, formatTime } from '../utils/format'

const router = useRouter()
const list = ref([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    list.value = await getMyAds()
  } catch {
    // 统一由拦截器提示
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h2>我的广告</h2>
      <el-button type="primary" @click="router.push('/ads/new')">新建广告</el-button>
    </div>
    <el-card>
      <el-table :data="list" v-loading="loading" stripe border>
        <el-table-column prop="ad_id" label="ID" width="70" />
        <el-table-column prop="title" label="标题" min-width="140" />
        <el-table-column prop="content" label="文案" min-width="160" show-overflow-tooltip />
        <el-table-column label="日预算" width="110">
          <template #default="{ row }"><span class="money">¥{{ formatMoney(row.daily_budget) }}</span></template>
        </el-table-column>
        <el-table-column label="已消耗" width="110">
          <template #default="{ row }"><span class="money">¥{{ formatMoney(row.spent) }}</span></template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="formatStatus(row.status).type">{{ formatStatus(row.status).label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="提交时间" width="160">
          <template #default="{ row }">{{ formatTime(row.submit_time) }}</template>
        </el-table-column>
        <el-table-column label="驳回原因" min-width="160">
          <template #default="{ row }">
            <span :class="{ 'reject-reason': row.reject_reason }">{{ row.reject_reason || '-' }}</span>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && list.length === 0" description="暂无广告，点击右上角新建" />
    </el-card>
  </div>
</template>

<style scoped>
.reject-reason { color: #f56c6c; }
</style>
