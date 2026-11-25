<script setup>
import { onMounted, ref, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getReport } from '../api'
import { formatMoney } from '../utils/format'

const loading = ref(false)
const report = ref({ ad_count: 0, impression_count: 0, click_count: 0, total_spent: '0.00' })
const chartEl = ref(null)
let chart = null

async function load() {
  loading.value = true
  try {
    report.value = await getReport()
    await nextTick()
    renderChart()
  } catch {
    // 统一由拦截器提示
  } finally {
    loading.value = false
  }
}

function renderChart() {
  if (!chartEl.value) return
  if (!chart) chart = echarts.init(chartEl.value)
  chart.setOption({
    title: { text: '投放数据概览', left: 'center', textStyle: { fontSize: 16, fontWeight: 500 } },
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0, data: ['曝光次数', '点击次数'] },
    grid: { left: '12%', right: '10%', bottom: '18%', top: '18%' },
    xAxis: { type: 'category', data: ['累计'] },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      { name: '曝光次数', type: 'bar', data: [report.value.impression_count], itemStyle: { color: '#409eff' }, barWidth: 50 },
      { name: '点击次数', type: 'bar', data: [report.value.click_count], itemStyle: { color: '#67c23a' }, barWidth: 50 }
    ]
  })
}

onMounted(load)
</script>

<template>
  <div class="page" v-loading="loading">
    <div class="page-header">
      <h2>数据报表</h2>
    </div>
    <el-row :gutter="16">
      <el-col :span="6">
        <el-card><div class="stat"><div class="label">广告数量</div><div class="value">{{ report.ad_count }}</div></div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card><div class="stat"><div class="label">曝光次数</div><div class="value">{{ report.impression_count }}</div></div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card><div class="stat"><div class="label">点击次数</div><div class="value">{{ report.click_count }}</div></div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card><div class="stat"><div class="label">总消耗</div><div class="value money">¥{{ formatMoney(report.total_spent) }}</div></div></el-card>
      </el-col>
    </el-row>
    <el-card class="chart-card">
      <div ref="chartEl" class="chart"></div>
    </el-card>
  </div>
</template>

<style scoped>
.stat .label { color: #909399; font-size: 14px; }
.stat .value { margin-top: 8px; font-size: 26px; font-weight: 500; color: #303133; }
.chart-card { margin-top: 20px; }
.chart { height: 360px; width: 100%; }
</style>
