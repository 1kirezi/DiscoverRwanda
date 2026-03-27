import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '../services/api'

interface User {
  id: number
  email: string
  full_name: string
  role: 'student' | 'business' | 'faculty' | 'admin'
  avatar_url?: string
  verification_status: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (data: { email: string; password: string; full_name: string; role: string }) => Promise<void>
  logout: () => void
  setUser: (user: User) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (email, password) => {
        const { data } = await api.post('/auth/login', { email, password })
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
        set({ user: data.user, token: data.access_token, isAuthenticated: true })
      },

      register: async (payload) => {
        const { data } = await api.post('/auth/register', payload)
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
        set({ user: data.user, token: data.access_token, isAuthenticated: true })
      },

      logout: () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        set({ user: null, token: null, isAuthenticated: false })
      },

      setUser: (user) => set({ user }),
    }),
    { name: 'auth-store', partialize: (s) => ({ user: s.user, token: s.token, isAuthenticated: s.isAuthenticated }) }
  )
)
