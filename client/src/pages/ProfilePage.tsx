import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import api from '../services/api'
import { PageLoader } from '../components/common/UI'
import { useAuthStore } from '../store/auth'
import { useState } from 'react'

export default function ProfilePage() {
  const { user, setUser } = useAuthStore()
  const qc = useQueryClient()
  const [saved, setSaved] = useState(false)

  const { data: profile, isLoading } = useQuery({
    queryKey: ['my-student-profile'],
    queryFn: () => api.get('/users/me/portfolio').then(r => r.data.profile),
    enabled: user?.role === 'student',
  })

  const { register: regBase, handleSubmit: subBase, formState: { isSubmitting: baseSubmitting } } = useForm({
    values: { full_name: user?.full_name ?? '', bio: user?.bio ?? '' },
  })

  const { register: regStudent, handleSubmit: subStudent, formState: { isSubmitting: studentSubmitting } } = useForm({
    values: {
      academic_program: profile?.academic_program ?? '',
      year_of_study: profile?.year_of_study ?? '',
      availability_hours_per_week: profile?.availability_hours_per_week ?? 10,
      linkedin_url: profile?.linkedin_url ?? '',
      github_url: profile?.github_url ?? '',
      portfolio_summary: profile?.portfolio_summary ?? '',
    },
  })

  const updateUser = useMutation({
    mutationFn: (data: any) => api.put('/users/me', data),
    onSuccess: (res) => {
      setUser(res.data)
      qc.invalidateQueries({ queryKey: ['my-student-profile'] })
      setSaved(true)
      setTimeout(() => setSaved(false), 2500)
    },
  })

  const updateProfile = useMutation({
    mutationFn: (data: any) => api.put('/users/me/student-profile', data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['my-student-profile'] })
      setSaved(true)
      setTimeout(() => setSaved(false), 2500)
    },
  })

  if (isLoading && user?.role === 'student') return <PageLoader />

  return (
    <div className="max-w-xl space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Profile settings</h1>
        {saved && (
          <span className="text-sm text-brand-600 font-medium bg-brand-50 px-3 py-1 rounded-full">
            ✓ Saved
          </span>
        )}
      </div>

      {/* Avatar + role badge */}
      <div className="card card-body flex items-center gap-4">
        <div className="w-16 h-16 rounded-full bg-brand-100 flex items-center justify-center text-brand-600 text-2xl font-bold flex-shrink-0">
          {user?.full_name?.[0]?.toUpperCase()}
        </div>
        <div>
          <p className="font-semibold text-gray-900">{user?.full_name}</p>
          <p className="text-sm text-gray-500">{user?.email}</p>
          <span className="badge badge-green capitalize mt-1">{user?.role}</span>
        </div>
      </div>

      {/* Basic info */}
      <div className="card card-body">
        <h3 className="font-semibold mb-4">Basic info</h3>
        <form onSubmit={subBase(d => updateUser.mutate(d))} className="space-y-4">
          <div>
            <label className="label">Full name</label>
            <input {...regBase('full_name', { required: true })} className="input" />
          </div>
          <div>
            <label className="label">Bio</label>
            <textarea {...regBase('bio')} rows={3} className="input resize-none"
              placeholder="Tell others about yourself..." />
          </div>
          <button type="submit" disabled={baseSubmitting || updateUser.isPending} className="btn-primary">
            {updateUser.isPending ? 'Saving...' : 'Save changes'}
          </button>
        </form>
      </div>

      {/* Student profile */}
      {user?.role === 'student' && (
        <div className="card card-body">
          <h3 className="font-semibold mb-4">Student profile</h3>
          <form onSubmit={subStudent(d => updateProfile.mutate(d))} className="space-y-4">
            <div>
              <label className="label">Academic program</label>
              <input {...regStudent('academic_program')} className="input"
                placeholder="e.g. Computer Science" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">Year of study</label>
                <input {...regStudent('year_of_study')} type="number" min={1} max={6} className="input" />
              </div>
              <div>
                <label className="label">Hours/week available</label>
                <input {...regStudent('availability_hours_per_week')} type="number" min={1} max={80} className="input" />
              </div>
            </div>
            <div>
              <label className="label">LinkedIn URL</label>
              <input {...regStudent('linkedin_url')} className="input"
                placeholder="https://linkedin.com/in/yourname" />
            </div>
            <div>
              <label className="label">GitHub URL</label>
              <input {...regStudent('github_url')} className="input"
                placeholder="https://github.com/yourname" />
            </div>
            <div>
              <label className="label">Portfolio summary</label>
              <textarea {...regStudent('portfolio_summary')} rows={4} className="input resize-none"
                placeholder="A short summary of your background, interests, and goals..." />
            </div>
            <button type="submit" disabled={studentSubmitting || updateProfile.isPending} className="btn-primary">
              {updateProfile.isPending ? 'Saving...' : 'Update student profile'}
            </button>
          </form>
        </div>
      )}

      {/* Business verification */}
      {user?.role === 'business' && user?.verification_status === 'pending' && (
        <div className="p-4 bg-amber-50 border border-amber-100 rounded-xl">
          <p className="text-sm font-medium text-amber-800">⏳ Verification pending</p>
          <p className="text-xs text-amber-600 mt-1">
            Your business account is under review. You'll receive access once approved.
          </p>
        </div>
      )}
    </div>
  )
}
