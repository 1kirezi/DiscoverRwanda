import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../store/auth'
import api from '../services/api'
import { PageLoader, ProgressBar, StatusBadge } from '../components/common/UI'

function StatCard({ label, value, icon, color = 'brand' }: { label: string; value: any; icon: string; color?: string }) {
  return (
    <div className="card card-body flex items-center gap-4">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-xl
        ${color === 'brand' ? 'bg-brand-50' : color === 'purple' ? 'bg-purple-50' : color === 'amber' ? 'bg-amber-50' : 'bg-blue-50'}`}>
        {icon}
      </div>
      <div>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <p className="text-sm text-gray-500">{label}</p>
      </div>
    </div>
  )
}

function StudentDashboard({ user }: { user: any }) {
  const { data: portfolio } = useQuery({ queryKey: ['portfolio'], queryFn: () => api.get('/users/me/portfolio').then(r => r.data) })
  const { data: matches } = useQuery({ queryKey: ['matches'], queryFn: () => api.get('/challenges/matched').then(r => r.data) })
  const { data: badges } = useQuery({ queryKey: ['my-badges'], queryFn: () => api.get('/learning/badges/mine').then(r => r.data) })
  const { data: paths } = useQuery({ queryKey: ['learning-paths'], queryFn: () => api.get('/learning/paths').then(r => r.data) })

  const enrolled = paths?.filter((p: any) => p.is_enrolled) || []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Welcome back, {user.full_name.split(' ')[0]} 👋</h1>
        <p className="text-gray-500 mt-1">Here's what's happening on your platform today.</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Active projects" value={portfolio?.stats?.total_projects ?? 0} icon="🗂️" />
        <StatCard label="Badges earned" value={portfolio?.stats?.total_badges ?? 0} icon="🏅" color="purple" />
        <StatCard label="Paths completed" value={portfolio?.stats?.completed_paths ?? 0} icon="📚" color="amber" />
        <StatCard label="Skills" value={portfolio?.stats?.skills_count ?? 0} icon="⚡" color="blue" />
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Top challenge matches */}
        <div className="card">
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-50">
            <h3 className="font-semibold">Top challenge matches</h3>
            <Link to="/challenges?tab=matched" className="text-sm text-brand-600 hover:underline">View all</Link>
          </div>
          <div className="divide-y divide-gray-50">
            {matches?.slice(0, 4).map((m: any) => (
              <Link key={m.challenge.id} to={`/challenges/${m.challenge.id}`}
                className="flex items-center justify-between px-6 py-3 hover:bg-gray-50 transition">
                <div className="flex-1 min-w-0 mr-3">
                  <p className="text-sm font-medium text-gray-900 truncate">{m.challenge.title}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{m.challenge.category} · {m.challenge.estimated_weeks}w</p>
                </div>
                <div className="text-right flex-shrink-0">
                  <div className="text-sm font-semibold" style={{ color: m.match_score >= 70 ? '#1D9E75' : m.match_score >= 40 ? '#EF9F27' : '#E24B4A' }}>
                    {Math.round(m.match_score)}%
                  </div>
                  <div className="text-xs text-gray-400">match</div>
                </div>
              </Link>
            ))}
            {(!matches || matches.length === 0) && (
              <div className="px-6 py-8 text-center text-sm text-gray-400">
                Complete your profile to get matched with challenges
              </div>
            )}
          </div>
        </div>

        {/* Learning progress */}
        <div className="card">
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-50">
            <h3 className="font-semibold">Learning progress</h3>
            <Link to="/learning" className="text-sm text-brand-600 hover:underline">View all</Link>
          </div>
          <div className="divide-y divide-gray-50">
            {enrolled.slice(0, 4).map((p: any) => (
              <Link key={p.id} to={`/learning/paths/${p.id}`}
                className="px-6 py-3 hover:bg-gray-50 transition block">
                <div className="flex items-center justify-between mb-1.5">
                  <p className="text-sm font-medium text-gray-900 truncate">{p.title}</p>
                  <span className="text-xs text-gray-500 ml-2">{p.progress}%</span>
                </div>
                <ProgressBar value={p.progress} />
              </Link>
            ))}
            {enrolled.length === 0 && (
              <div className="px-6 py-8 text-center text-sm text-gray-400">
                <Link to="/learning" className="text-brand-600 hover:underline">Browse learning paths</Link> to get started
              </div>
            )}
          </div>
        </div>

        {/* Recent badges */}
        {badges && badges.length > 0 && (
          <div className="card">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-50">
              <h3 className="font-semibold">Recent badges</h3>
              <Link to="/portfolio" className="text-sm text-brand-600 hover:underline">View portfolio</Link>
            </div>
            <div className="px-6 py-4 flex flex-wrap gap-3">
              {badges.slice(0, 6).map((b: any) => (
                <div key={b.id} className="flex items-center gap-2 bg-gray-50 rounded-xl px-3 py-2">
                  <div className="w-6 h-6 rounded-full flex items-center justify-center text-sm"
                    style={{ background: b.color + '22', color: b.color }}>🏅</div>
                  <span className="text-xs font-medium text-gray-700">{b.name}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Active projects */}
        {portfolio?.projects?.length > 0 && (
          <div className="card">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-50">
              <h3 className="font-semibold">Active projects</h3>
            </div>
            <div className="divide-y divide-gray-50">
              {portfolio.projects.map((p: any) => (
                <Link key={p.project_id} to={`/projects/${p.project_id}`}
                  className="flex items-center justify-between px-6 py-3 hover:bg-gray-50 transition">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{p.title}</p>
                    <p className="text-xs text-gray-500">{p.challenge_title}</p>
                  </div>
                  <StatusBadge status={p.status} />
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function BusinessDashboard({ user }: { user: any }) {
  const { data: challenges } = useQuery({
    queryKey: ['my-challenges'],
    queryFn: () => api.get('/challenges').then(r => r.data.filter((c: any) => c.business_id === user.id))
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Welcome, {user.full_name.split(' ')[0]} 👋</h1>
          <p className="text-gray-500 mt-1">Manage your challenges and student collaborations.</p>
        </div>
        <Link to="/challenges" className="btn-primary">+ Post challenge</Link>
      </div>

      {user.verification_status === 'pending' && (
        <div className="p-4 bg-amber-50 border border-amber-100 rounded-xl text-sm text-amber-800 flex items-center gap-3">
          <span className="text-xl">⏳</span>
          <div>
            <p className="font-medium">Verification pending</p>
            <p className="text-amber-600">Your business account is under review. You can post challenges once approved.</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        <StatCard label="Total challenges" value={challenges?.length ?? 0} icon="🏆" />
        <StatCard label="Active" value={challenges?.filter((c: any) => c.status === 'active').length ?? 0} icon="✅" color="purple" />
        <StatCard label="Under review" value={challenges?.filter((c: any) => c.status === 'submitted').length ?? 0} icon="⏳" color="amber" />
      </div>

      <div className="card">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-50">
          <h3 className="font-semibold">Your challenges</h3>
          <Link to="/challenges" className="text-sm text-brand-600 hover:underline">View all</Link>
        </div>
        <table className="table w-full">
          <thead>
            <tr><th>Title</th><th>Status</th><th>Category</th><th>Teams</th></tr>
          </thead>
          <tbody>
            {challenges?.map((c: any) => (
              <tr key={c.id}>
                <td><Link to={`/challenges/${c.id}`} className="text-brand-600 hover:underline font-medium">{c.title}</Link></td>
                <td><StatusBadge status={c.status} /></td>
                <td className="text-gray-500">{c.category || '—'}</td>
                <td className="text-gray-500">{c.applications_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {!challenges?.length && (
          <div className="px-6 py-10 text-center text-sm text-gray-400">
            No challenges yet. <Link to="/challenges" className="text-brand-600 hover:underline">Post your first challenge</Link>
          </div>
        )}
      </div>
    </div>
  )
}

function AdminDashboard() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['admin-analytics'],
    queryFn: () => api.get('/admin/analytics').then(r => r.data)
  })

  if (isLoading) return <PageLoader />

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Platform Overview</h1>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total users" value={analytics?.users?.total} icon="👥" />
        <StatCard label="Students" value={analytics?.users?.students} icon="🎓" color="purple" />
        <StatCard label="Active challenges" value={analytics?.challenges?.active} icon="🏆" color="amber" />
        <StatCard label="Pending review" value={analytics?.challenges?.pending_review} icon="⏳" color="blue" />
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Projects" value={analytics?.projects?.active_projects} icon="🗂️" />
        <StatCard label="Completed" value={analytics?.projects?.completed} icon="✅" color="purple" />
        <StatCard label="Badges awarded" value={analytics?.learning?.badges_awarded} icon="🏅" color="amber" />
        <StatCard label="Mentor sessions" value={analytics?.learning?.mentor_sessions} icon="🤝" color="blue" />
      </div>
      {analytics?.users?.pending_verifications > 0 && (
        <div className="p-4 bg-amber-50 border border-amber-100 rounded-xl flex items-center justify-between">
          <div className="flex items-center gap-3 text-sm text-amber-800">
            <span className="text-xl">⚠️</span>
            <span>{analytics.users.pending_verifications} business verification(s) pending review</span>
          </div>
          <Link to="/admin" className="btn btn-sm bg-amber-100 text-amber-800 hover:bg-amber-200">Review now</Link>
        </div>
      )}
    </div>
  )
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  if (!user) return <PageLoader />

  if (user.role === 'student') return <StudentDashboard user={user} />
  if (user.role === 'business') return <BusinessDashboard user={user} />
  if (user.role === 'admin') return <AdminDashboard />
  return <StudentDashboard user={user} />
}
