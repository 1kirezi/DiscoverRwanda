import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuthStore } from '../store/auth'
import { useState } from 'react'

const ROLES = [
  { value: 'student', label: '🎓 Student', desc: 'Join teams and solve real challenges' },
  { value: 'business', label: '🏨 Tourism Business', desc: 'Post challenges and get student solutions' },
  { value: 'faculty', label: '👨‍🏫 Faculty / Staff', desc: 'Advise and guide student teams' },
]

export default function RegisterPage() {
  const { t } = useTranslation()
  const { register: registerUser } = useAuthStore()
  const navigate = useNavigate()
  const [error, setError] = useState('')
  const { register, handleSubmit, watch, setValue, formState: { isSubmitting, errors } } = useForm<{
    email: string; password: string; full_name: string; role: string
  }>({ defaultValues: { role: 'student' } })

  const selectedRole = watch('role')

  const onSubmit = async (data: any) => {
    try {
      setError('')
      await registerUser(data)
      navigate('/dashboard')
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Registration failed')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-gray-50">
      <div className="w-full max-w-md">
        <div className="flex items-center gap-2 mb-8">
          <div className="w-8 h-8 rounded-lg bg-brand-400 flex items-center justify-center text-white font-bold text-sm">DR</div>
          <span className="font-semibold">Discover Rwanda</span>
        </div>

        <div className="card card-body">
          <h2 className="text-2xl font-semibold mb-1">{t('auth.registerTitle')}</h2>
          <p className="text-gray-500 text-sm mb-6">
            {t('auth.hasAccount')} <Link to="/login" className="text-brand-600 font-medium hover:underline">{t('auth.login')}</Link>
          </p>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {error && <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg border border-red-100">{error}</div>}

            <div>
              <label className="label">{t('auth.fullName')}</label>
              <input {...register('full_name', { required: 'Name is required' })} className="input" placeholder="Your full name" />
              {errors.full_name && <p className="text-red-500 text-xs mt-1">{errors.full_name.message}</p>}
            </div>

            <div>
              <label className="label">{t('auth.email')}</label>
              <input {...register('email', { required: true })} type="email" className="input" placeholder="you@example.com" />
            </div>

            <div>
              <label className="label">{t('auth.password')}</label>
              <input {...register('password', { required: true, minLength: { value: 8, message: 'Min 8 characters' } })}
                type="password" className="input" placeholder="Min 8 characters" />
              {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password.message}</p>}
            </div>

            <div>
              <label className="label">{t('auth.role')}</label>
              <div className="space-y-2">
                {ROLES.map(r => (
                  <label key={r.value}
                    className={`flex items-center gap-3 p-3 rounded-xl border-2 cursor-pointer transition
                      ${selectedRole === r.value ? 'border-brand-400 bg-brand-50' : 'border-gray-100 hover:border-gray-200'}`}>
                    <input type="radio" value={r.value} {...register('role')} className="sr-only" />
                    <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center flex-shrink-0
                      ${selectedRole === r.value ? 'border-brand-400 bg-brand-400' : 'border-gray-300'}`}>
                      {selectedRole === r.value && <div className="w-2 h-2 rounded-full bg-white" />}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{r.label}</p>
                      <p className="text-xs text-gray-500">{r.desc}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <button type="submit" disabled={isSubmitting} className="btn-primary w-full btn-lg">
              {isSubmitting ? 'Creating account...' : t('auth.register')}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
