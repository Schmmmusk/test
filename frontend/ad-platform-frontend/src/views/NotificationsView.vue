<script setup>
import { onMounted, ref } from 'vue'
import { getNotifications } from '../api'
import { formatTime } from '../utils/format'

const READ_KEY = 'notification_read_ids'

const list = ref([])
const loading = ref(false)
const detailVisible = ref(false)
const detail = ref(null)

function readIds() {
  try {
    return new Set(JSON.parse(localStorage.getItem(READ_KEY) || '[]'))
  } catch {
    return new Set()
  }
}

function isRead(row) {
  return Boolean(row.is_read) || readIds().has(row.notice_id)
}

function unreadCount() {
  return list.value.filter((n) => !isRead(n)).length
}

function openDetail(row) {
  detail.value = row
  detailVisible.value = true
  const ids = readIds()
  ids.add(row.notice_id)
  localStorage.setItem(READ_KEY, JSON.stringify([...ids]))
}

async function load() {
  loading.value = true
  try {
    list.value = await getNotifications()
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
      <h2>站内信</h2>
      <el-tag v-if="unreadCount() > 0" type="danger" round>{{ unreadCount() }} 条未读</el-tag>
    </div>
    <el-card>
      <el-table :data="list" v-loading="loading" stripe border @row-click="openDetail" style="cursor: pointer">
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <span v-if="isRead(row)" class="read">已读</span>
            <el-badge v-else value="新" type="danger" />
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" width="160" />
        <el-table-column prop="content" label="内容" min-width="320" show-overflow-tooltip />
        <el-table-column label="时间" width="180">
          <template #default="{ row }">{{ formatTime(row.create_time) }}</template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && list.length === 0" description="暂无站内信" />
    </el-card>
    <p class="tip">提示：点击任意一行查看完整内容。后端暂未提供标记已读接口，已读状态在本地保存。</p>

    <el-dialog v-model="detailVisible" title="站内信详情" width="520px">
      <template v-if="detail">
        <div class="detail-title">{{ detail.title }}</div>
        <div class="detail-time">{{ formatTime(detail.create_time) }}</div>
        <el-divider />
        <div class="detail-content">{{ detail.content }}</div>
      </template>
      <template #footer>
        <el-button type="primary" @click="detailVisible = false">知道了</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.read { color: #909399; }
.tip { color: #909399; font-size: 13px; margin-top: 12px; }
.detail-title { font-size: 17px; font-weight: 500; color: #303133; }
.detail-time { margin-top: 6px; color: #909399; font-size: 13px; }
.detail-content { white-space: pre-wrap; line-height: 1.7; color: #606266; }
</style>
