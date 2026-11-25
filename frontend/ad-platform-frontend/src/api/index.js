import request from './request'

export const register = (data) => request.post('/api/register', data)
export const login = (data) => request.post('/api/login', data)

export const getMyAds = () => request.get('/api/client/ads')
export const createAd = (data) => request.post('/api/ads', data)

export const getPendingAds = () => request.get('/api/audit/pending')
export const passAd = (id) => request.post(`/api/audit/${id}/pass`)
export const rejectAd = (id, reason) => request.post(`/api/audit/${id}/reject`, { reason })

export const recharge = (data) => request.post('/api/recharge', data)
export const getRecharges = () => request.get('/api/recharges')

export const getNotifications = () => request.get('/api/notifications')
export const getReport = () => request.get('/api/report')
