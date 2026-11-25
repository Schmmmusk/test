<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPendingAds, passAd, rejectAd } from '../api'
import { formatMoney, formatTime } from '../utils/format'

const list = ref([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    list.value = await getPendingAds()
  } catch {
    // 统一由拦截器提示
  } finally {
    loading.value = false
  }
}

async function doPass(row) {
  try {
    await passAd(row.ad_id)
    ElMessage.success('审核通过')
    load()
  } catch {
    // 统一由拦截器提示
  }
}

async function doReject(row) {
  try {
    const { value } = await ElMessageBox.prompt('请输入驳回原因', '审核驳回', {
      confirmButtonText: '确认驳回',
      cancelButtonText: '取消',
      inputPlaceholder: '例如：素材违规'
    })
    if (!value || !value.trim()) {
      ElMessage.warning('驳回必须填写原因')
      return
    }
    await rejectAd(row.ad_id, value.trim())
    ElMessage.success('已驳回')
    load()
  } catch (e) {
    if (e !== 'cancel' && e?.message !== 'cancel') {
      // 请求错误由拦截器提示
    }
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h2>审核管理</h2>
      <el-tag type="warning" round>待审核 {{ list.length }} 条</el-tag>
    </div>
    <el-card>
      <el-table :data="list" v-loading="loading" stripe border>
        <el-table-column prop="ad_id" label="ID" width="70" />
        <el-table-column prop="title" label="标题" min-width="140" />
        <el-table-column prop="content" label="文案" min-width="180" show-overflow-tooltip />
        <el-table-column label="日预算" width="110">
          <template #default="{ row }"><span class="money">¥{{ formatMoney(row.daily_budget) }}</span></template>
        </el-table-column>
        <el-table-column label="提交时间" width="180">
          <template #default="{ row }">{{ formatTime(row.submit_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="success" size="small" @click="doPass(row)">通过</el-button>
            <el-button type="danger" size="small" @click="doReject(row)">驳回</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && list.length === 0" description="暂无待审核广告" />
    </el-card>
  </div>
</template>
