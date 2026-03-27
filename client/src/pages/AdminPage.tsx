import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { PageLoader } from '../components/common/UI'

export default function AdminPage() {
  const [tab, setTab] = useState('overview')
  const qc = useQueryClient()

  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['admin-analytics'],
    queryFn: () => api.get('/admin/analytics').then(r => r.data),
  })
  const { data: pending } = useQuery({
    queryKey: ['pending-challenges'],
    queryFn: () => api.get('/admin/challenges/pending').then(r => r.data),
  })
  const { data: verifications } = useQuery({
    queryKey: ['verifications'],
    queryFn: () => api.get('/admin/verifications').then(r => r.data),
  })
  const { data: users } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => api.get('/admin/users').then(r => r.data),
    enabled: tab === 'users',
  })

  const approveMutation = useMutation({
    mutationFn: (id: number) => api.post(`/challenges/${id}/review`, { action: 'approve' }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['pending-challenges'] }),
  })
  const rejectMutation = useMutation({
    mutationFn: (id: number) => api.post(`/challenges/${id}/review`, { action: 'reject' }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['pending-challenges'] }),
  })
  const verifMutation = useMutation({
    mutationFn: ({ id, action }: { id: number; action: string }) =>
      api.put(`/admin/verifications/${id}?action=${action}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['verifications'] })
      qc.invalidateQueries({ queryKey: ['admin-analytics'] })
    },
  })

  const TABS = [
    ['overview', 'Overview'],
    ['challenges', `Pending (${pending?.length ?? 0})`],
    ['verifications', `Verifications (${verifications?.length ?? 0})`],
    ['users', 'Users'],
  ]

  if (analyticsLoading) return <PageLoader />

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Admin dashboard</h1>

      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-gray-100 rounded-xl w-fit overflow-x-auto">
        {TABS.map(([v, l]) => (
          <button key={v} onClick={() => setTab(v)}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition whitespace-nowrap
              ${tab === v ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}>
            {l}
          </button>
        ))}
      </div>

      {/* Overview */}
      {tab === 'overview' && analytics && (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              ['Total users', analytics.users.total, '👥'],
              ['Students', analytics.users.students, '🎓'],
              ['Businesses', analytics.users.businesses, '🏨'],
              ['Faculty', analytics.users.faculty, '👨‍🏫'],
            ].map(([label, value, icon]) => (
              <div key={label as string} className="card card-body flex items-center gap-3">
                <span className="text-2xl">{icon}</span>
                <div>
                  <p className="text-xl font-bold text-gray-900">{value}</p>
                  <p className="text-xs text-gray-500">{label}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              ['Active challenges', analytics.challenges.active, '🏆'],
              ['Total projects', analytics.projects.active_projects, '🗂️'],
              ['Badges awarded', analytics.learning.badges_awarded, '🏅'],
              ['Mentor sessions', analytics.learning.mentor_sessions, '🤝'],
            ].map(([label, value, icon]) => (
              <div key={label as string} className="card card-body flex items-center gap-3">
                <span className="text-2xl">{icon}</span>
                <div>
                  <p className="text-xl font-bold text-gray-900">{value}</p>
                  <p className="text-xs text-gray-500">{label}</p>
                </div>
              </div>
            ))}
          </div>
          {analytics.users.pending_verifications > 0 && (
            <div className="p-4 bg-amber-50 border border-amber-100 rounded-xl flex items-center justify-between">
              <div className="flex items-center gap-3 text-sm text-amber-800">
                <span className="text-xl">⚠️</span>
                <span>{analytics.users.pending_verifications} business verification(s) awaiting review</span>
              </div>
              <button onClick={() => setTab('verifications')}
                className="btn btn-sm bg-amber-100 text-amber-800 hover:bg-amber-200">
                Review now
              </button>
            </div>
          )}
        </>
      )}

      {/* Pending challenges */}
      {tab === 'challenges' && (
        <div className="card overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100">
            <h3 className="font-semibold">Challenges pending review</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="table w-full">
              <thead>
                <tr><th>Title</th><th>Business</th><th>Category</th><th>Submitted</th><th>Actions</th></tr>
              </thead>
              <tbody>
                {pending?.map((c: any) => (
                  <tr key={c.id}>
                    <td>
                      <Link to={`/challenges/${c.id}`} className="text-brand-600 hover:underline font-medium">
                        {c.title}
                      </Link>
                    </td>
                    <td className="text-gray-500">{c.business_owner}</td>
                    <td className="text-gray-500">{c.category || '—'}</td>
                    <td className="text-gray-400 text-xs whitespace-nowrap">
                      {new Date(c.submitted_at).toLocaleDateString()}
                    </td>
                    <td>
                      <div className="flex gap-2">
                        <button
                          onClick={() => approveMutation.mutate(c.id)}
                          disabled={approveMutation.isPending}
                          className="btn btn-sm bg-brand-50 text-brand-600 hover:bg-brand-100">
                          Approve
                        </button>
                        <button
                          onClick={() => rejectMutation.mutate(c.id)}
                          disabled={rejectMutation.isPending}
                          className="btn btn-sm bg-red-50 text-red-600 hover:bg-red-100">
                          Reject
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!pending?.length && (
              <div className="px-6 py-10 text-center text-gray-400 text-sm">
                No challenges pending review 🎉
              </div>
            )}
          </div>
        </div>
      )}

      {/* Business verifications */}
      {tab === 'verifications' && (
        <div className="card overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100">
            <h3 className="font-semibold">Business verifications</h3>
          </div>
          <div className="divide-y divide-gray-50">
            {verifications?.map((v: any) => (
              <div key={v.id} className="px-6 py-4 flex items-center justify-between gap-4">
                <div>
                  <p className="font-medium text-gray-900">{v.business_name || v.full_name}</p>
                  <p className="text-sm text-gray-500">{v.email}</p>
                  {v.documents?.length > 0 && (
                    <p className="text-xs text-brand-600 mt-1">
                      {v.documents.length} document(s) submitted
                    </p>
                  )}
                </div>
                <div className="flex gap-2 flex-shrink-0">
                  <button
                    onClick={() => verifMutation.mutate({ id: v.id, action: 'approve' })}
                    disabled={verifMutation.isPending}
                    className="btn btn-sm bg-brand-50 text-brand-600 hover:bg-brand-100">
                    Approve
                  </button>
                  <button
                    onClick={() => verifMutation.mutate({ id: v.id, action: 'reject' })}
                    disabled={verifMutation.isPending}
                    className="btn btn-sm bg-red-50 text-red-600 hover:bg-red-100">
                    Reject
                  </button>
                </div>
              </div>
            ))}
            {!verifications?.length && (
              <div className="px-6 py-10 text-center text-gray-400 text-sm">
                No pending verifications 🎉
              </div>
            )}
          </div>
        </div>
      )}

      {/* Users */}
      {tab === 'users' && (
        <div className="card overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100">
            <h3 className="font-semibold">All users ({users?.length ?? 0})</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="table w-full">
              <thead>
                <tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th><th>Joined</th></tr>
              </thead>
              <tbody>
                {users?.map((u: any) => (
                  <tr key={u.id}>
                    <td className="font-medium">{u.full_name}</td>
                    <td className="text-gray-500 text-xs">{u.email}</td>
                    <td>
                      <span className="badge badge-gray capitalize">{u.role}</span>
                    </td>
                    <td>
                      {u.is_active
                        ? <span className="badge badge-green">Active</span>
                        : <span className="badge badge-red">Inactive</span>}
                    </td>
                    <td className="text-gray-400 text-xs whitespace-nowrap">
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!users && <div className="px-6 py-10 text-center"><div className="w-6 h-6 border-2 border-brand-200 border-t-brand-400 rounded-full animate-spin mx-auto" /></div>}
          </div>
        </div>
      )}
    </div>
  )
}
