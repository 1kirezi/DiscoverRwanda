import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuthStore } from '../store/auth'
import { useState } from 'react'

export default function LoginPage() {
  const { t } = useTranslation()
  const { login } = useAuthStore()
  const navigate = useNavigate()
  const [error, setError] = useState('')
  const { register, handleSubmit, formState: { isSubmitting } } = useForm<{ email: string; password: string }>()

  const onSubmit = async (data: { email: string; password: string }) => {
    try {
      setError('')
      await login(data.email, data.password)
      navigate('/dashboard')
    } catch {
      setError('Invalid email or password')
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Left — brand panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-brand-400 flex-col items-center justify-center p-12 text-white">
        <div className="max-w-sm text-center">
          <div className="w-20 h-20 rounded-2xl bg-white/20 flex items-center justify-center text-4xl mx-auto mb-8">🌍</div>
          <h1 className="text-3xl font-bold mb-4">Discover Rwanda</h1>
          <p className="text-brand-100 text-lg leading-relaxed">
            Connecting students with Africa's tourism technology challenges. Build real solutions. Earn real credentials.
          </p>
          <div className="mt-10 grid grid-cols-3 gap-4 text-center">
            {[['50+', 'Challenges'], ['200+', 'Students'], ['30+', 'Partners']].map(([n, l]) => (
              <div key={l} className="bg-white/10 rounded-xl p-4">
                <div className="text-2xl font-bold">{n}</div>
                <div className="text-xs text-brand-100 mt-1">{l}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right — form */}
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-sm">
          <div className="lg:hidden flex items-center gap-2 mb-8">
            <div className="w-8 h-8 rounded-lg bg-brand-400 flex items-center justify-center text-white font-bold text-sm">DR</div>
            <span className="font-semibold">Discover Rwanda</span>
          </div>

          <h2 className="text-2xl font-semibold text-gray-900 mb-2">{t('auth.loginTitle')}</h2>
          <p className="text-gray-500 text-sm mb-8">{t('auth.noAccount')} <Link to="/register" className="text-brand-600 font-medium hover:underline">{t('auth.register')}</Link></p>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {error && <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg border border-red-100">{error}</div>}

            <div>
              <label className="label">{t('auth.email')}</label>
              <input {...register('email', { required: true })} type="email" className="input" placeholder="you@example.com" autoComplete="email" />
            </div>
            <div>
              <label className="label">{t('auth.password')}</label>
              <input {...register('password', { required: true })} type="password" className="input" placeholder="••••••••" autoComplete="current-password" />
            </div>

            <button type="submit" disabled={isSubmitting} className="btn-primary w-full btn-lg mt-2">
              {isSubmitting ? 'Signing in...' : t('auth.login')}
            </button>
          </form>

        </div>
      </div>
    </div>
  )
}
