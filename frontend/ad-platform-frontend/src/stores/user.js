import { defineStore } from 'pinia'

const readUser = () => {
  try {
    return JSON.parse(localStorage.getItem('user') || 'null')
  } catch {
    return null
  }
}

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: readUser()
  }),
  getters: {
    isAdmin: (state) => Boolean(state.user?.is_admin),
    isLoggedIn: (state) => Boolean(state.token)
  },
  actions: {
    setLogin(token, user) {
      this.token = token
      this.user = user
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
    },
    updateBalance(balance) {
      if (this.user) {
        this.user = { ...this.user, balance }
        localStorage.setItem('user', JSON.stringify(this.user))
      }
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})
