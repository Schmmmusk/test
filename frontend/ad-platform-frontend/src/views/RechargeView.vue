<script setup>
import { onMounted, reactive, ref } from 'vue'
import { recharge, getRecharges } from '../api'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'
import { formatMoney, formatTime } from '../utils/format'

const userStore = useUserStore()
const loading = ref(false)
const listLoading = ref(false)
const list = ref([])
const form = reactive({ amount: null, order_no: '' })

function genOrderNo() {
  const d = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  return `ORD${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}${Math.floor(Math.random() * 900 + 100)}`
}

async function loadList() {
  listLoading.value = true
  try {
    list.value = await getRecharges()
  } catch {
    // 统一由拦截器提示
  } finally {
    listLoading.value = false
  }
}

async function submit() {
  const amount = Number(form.amount)
  if (!form.amount || !Number.isFinite(amount) || amount <= 0) {
    ElMessage.warning('请填写有效的充值金额')
    return
  }
  if (!form.order_no.trim()) {
    ElMessage.warning('请填写订单号')
    return
  }
  loading.value = true
  try {
    const res = await recharge({ amount: amount.toFixed(2), order_no: form.order_no.trim() })
    userStore.updateBalance(res.balance)
    ElMessage.success(`充值成功，当前余额 ¥${formatMoney(res.balance)}`)
    form.amount = null
    form.order_no = ''
    loadList()
  } catch {
    // 统一由拦截器提示
  } finally {
    loading.value = false
  }
}

onMounted(loadList)
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h2>账户充值</h2>
      <div class="balance">当前余额：<span class="money">¥{{ formatMoney(userStore.user?.balance) }}</span></div>
    </div>
    <el-card class="form-card">
      <el-form :model="form" label-width="100px" @keyup.enter="submit">
        <el-form-item label="充值金额" required>
          <el-input-number v-model="form.amount" :min="0.01" :precision="2" :step="100" controls-position="right" />
          <span class="hint">元</span>
        </el-form-item>
        <el-form-item label="订单号" required>
          <el-input v-model="form.order_no" placeholder="全局唯一">
            <template #append>
              <el-button @click="form.order_no = genOrderNo()">生成</el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="submit">确认充值</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="list-card">
      <h3>充值流水</h3>
      <el-table :data="list" v-loading="listLoading" stripe border>
        <el-table-column prop="recharge_id" label="ID" width="80" />
        <el-table-column label="金额" width="130">
          <template #default="{ row }"><span class="money">¥{{ formatMoney(row.amount) }}</span></template>
        </el-table-column>
        <el-table-column prop="order_no" label="订单号" min-width="200" />
        <el-table-column label="充值时间" width="180">
          <template #default="{ row }">{{ formatTime(row.recharge_time) }}</template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!listLoading && list.length === 0" description="暂无充值记录" />
    </el-card>
  </div>
</template>

<style scoped>
.form-card { max-width: 680px; margin-bottom: 20px; }
.list-card h3 { margin: 0 0 16px; font-size: 16px; font-weight: 500; }
.hint { margin-left: 10px; color: #909399; }
.balance { color: #606266; }
</style>
