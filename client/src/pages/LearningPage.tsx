import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { PageLoader, ProgressBar, EmptyState } from '../components/common/UI'
import { useAuthStore } from '../store/auth'

const DOMAIN_ICONS: Record<string, string> = {
  fundamentals: '⚡', digital_payments: '💳', data_analytics: '📊',
  booking_system: '📅', mobile_app: '📱', marketing: '📣',
}
const DIFFICULTY_COLOR: Record<string, string> = {
  beginner: 'text-brand-600 bg-brand-50',
  intermediate: 'text-amber-700 bg-amber-50',
  advanced: 'text-red-600 bg-red-50',
}

export default function LearningPage() {
  const { user } = useAuthStore()
  const qc = useQueryClient()
  const [tab, setTab] = useState('all')

  const { data: paths, isLoading } = useQuery({
    queryKey: ['learning-paths'],
    queryFn: () => api.get('/learning/paths').then(r => r.data),
  })
  const { data: recommended } = useQuery({
    queryKey: ['recommended-paths'],
    queryFn: () => api.get('/learning/paths/recommended').then(r => r.data),
    enabled: user?.role === 'student',
  })
  const enrollMutation = useMutation({
    mutationFn: (pathId: number) => api.post(`/learning/paths/${pathId}/enroll`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['learning-paths'] }),
  })

  if (isLoading) return <PageLoader />

  const enrolled = paths?.filter((p: any) => p.is_enrolled) || []
  const displayedPaths = tab === 'enrolled' ? enrolled : (paths || [])

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Learning paths</h1>

      {recommended && recommended.length > 0 && (
        <div className="p-4 bg-brand-50 rounded-2xl border border-brand-100">
          <p className="text-sm font-semibold text-brand-800 mb-3">✨ Recommended for you</p>
          <div className="flex gap-3 overflow-x-auto pb-1">
            {recommended.map((p: any) => (
              <Link key={p.id} to={`/learning/paths/${p.id}`}
                className="flex-shrink-0 bg-white rounded-xl px-4 py-3 border border-brand-100 hover:border-brand-400 transition w-52">
                <div className="text-xl mb-1">{DOMAIN_ICONS[p.domain] || '📚'}</div>
                <p className="text-sm font-medium text-gray-900 line-clamp-2">{p.title}</p>
                <p className="text-xs text-gray-500 mt-1">{p.estimated_hours}h · {p.difficulty}</p>
              </Link>
            ))}
          </div>
        </div>
      )}

      <div className="flex gap-1 p-1 bg-gray-100 rounded-xl w-fit">
        {[['all', 'All paths'], ['enrolled', `Enrolled (${enrolled.length})`]].map(([v, l]) => (
          <button key={v} onClick={() => setTab(v)}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition
              ${tab === v ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}>
            {l}
          </button>
        ))}
      </div>

      <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
        {displayedPaths.map((path: any) => (
          <div key={path.id} className="card card-body flex flex-col gap-3">
            <div className="flex items-start justify-between">
              <div className="w-12 h-12 rounded-xl bg-brand-50 flex items-center justify-center text-2xl">
                {DOMAIN_ICONS[path.domain] || '📚'}
              </div>
              <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${DIFFICULTY_COLOR[path.difficulty] || 'text-gray-600 bg-gray-100'}`}>
                {path.difficulty}
              </span>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">{path.title}</h3>
              <p className="text-sm text-gray-500 mt-1 line-clamp-2">{path.description}</p>
            </div>
            <div className="flex items-center gap-3 text-xs text-gray-500">
              <span>⏱ {path.estimated_hours}h</span>
              <span>📦 {path.modules_count} modules</span>
            </div>
            {path.is_enrolled && (
              <div>
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Progress</span><span>{path.progress}%</span>
                </div>
                <ProgressBar value={path.progress} />
                {path.is_completed && <p className="text-xs text-brand-600 font-medium mt-1">✓ Completed</p>}
              </div>
            )}
            <div className="flex gap-2 mt-auto pt-2">
              <Link to={`/learning/paths/${path.id}`} className="btn-secondary btn-sm flex-1 text-center">
                {path.is_enrolled ? 'Continue' : 'Preview'}
              </Link>
              {!path.is_enrolled && user?.role === 'student' && (
                <button onClick={() => enrollMutation.mutate(path.id)} disabled={enrollMutation.isPending}
                  className="btn-primary btn-sm flex-1">
                  Enroll
                </button>
              )}
            </div>
          </div>
        ))}
        {displayedPaths.length === 0 && (
          <div className="col-span-full">
            <EmptyState icon="📚" title="No learning paths yet"
              description={tab === 'enrolled' ? 'Enroll in a path to start learning.' : 'No paths available yet.'} />
          </div>
        )}
      </div>
    </div>
  )
}
