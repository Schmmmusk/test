export const statusMap = {
  pending: { label: '待审核', type: 'warning' },
  approved: { label: '已通过', type: 'success' },
  rejected: { label: '已驳回', type: 'danger' },
  paused: { label: '已暂停', type: 'info' }
}

export const formatStatus = (status) => statusMap[status] || { label: status, type: 'info' }

export const toNumber = (value) => {
  const n = Number(value)
  return Number.isFinite(n) ? n : 0
}

export const formatMoney = (value) => Number(value || 0).toFixed(2)

export const formatTime = (value) => {
  if (!value) return '-'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return value
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}
