import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { PageLoader } from '../components/common/UI'

export default function PortfolioPage() {
  const { data: portfolio, isLoading } = useQuery({
    queryKey: ['portfolio'],
    queryFn: () => api.get('/users/me/portfolio').then(r => r.data),
  })

  if (isLoading) return <PageLoader />
  if (!portfolio) return null

  const { user, profile, projects, badges, completed_learning_paths, stats } = portfolio

  return (
    <div className="max-w-3xl space-y-6">
      <h1 className="text-2xl font-semibold">My portfolio</h1>

      {/* Profile hero */}
      <div className="card card-body flex flex-col sm:flex-row items-center gap-5">
        <div className="w-20 h-20 rounded-full bg-brand-100 flex items-center justify-center text-brand-600 text-3xl font-bold flex-shrink-0">
          {user?.full_name?.[0]}
        </div>
        <div className="flex-1 text-center sm:text-left">
          <h2 className="text-xl font-semibold">{user?.full_name}</h2>
          <p className="text-gray-500 mt-0.5">
            {profile?.academic_program}
            {profile?.year_of_study ? ` · Year ${profile.year_of_study}` : ''}
          </p>
          {profile?.portfolio_summary && (
            <p className="text-sm text-gray-600 mt-2 max-w-md">{profile.portfolio_summary}</p>
          )}
          <div className="flex gap-4 mt-2 justify-center sm:justify-start">
            {profile?.linkedin_url && (
              <a href={profile.linkedin_url} target="_blank" rel="noreferrer"
                className="text-sm text-brand-600 hover:underline font-medium">LinkedIn ↗</a>
            )}
            {profile?.github_url && (
              <a href={profile.github_url} target="_blank" rel="noreferrer"
                className="text-sm text-brand-600 hover:underline font-medium">GitHub ↗</a>
            )}
          </div>
        </div>
        <div className="grid grid-cols-3 gap-3 text-center flex-shrink-0">
          {[
            ['Projects', stats?.total_projects ?? 0],
            ['Badges', stats?.total_badges ?? 0],
            ['Skills', stats?.skills_count ?? 0],
          ].map(([l, v]) => (
            <div key={l} className="bg-gray-50 rounded-xl px-4 py-3">
              <p className="text-xl font-bold text-gray-900">{v}</p>
              <p className="text-xs text-gray-500 mt-0.5">{l}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Skills */}
      {profile?.skills_inventory?.length > 0 && (
        <div className="card card-body">
          <h3 className="font-semibold mb-3">Skills</h3>
          <div className="flex flex-wrap gap-2">
            {profile.skills_inventory.map((s: string) => (
              <span key={s} className="badge badge-green">{s}</span>
            ))}
          </div>
        </div>
      )}

      {/* Projects */}
      {projects?.length > 0 && (
        <div className="card overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-50">
            <h3 className="font-semibold">Projects</h3>
          </div>
          <div className="divide-y divide-gray-50">
            {projects.map((p: any) => (
              <Link key={p.project_id} to={`/projects/${p.project_id}`}
                className="px-6 py-4 hover:bg-gray-50 transition block">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900">{p.title}</p>
                    <p className="text-sm text-gray-500 mt-0.5">{p.challenge_title}</p>
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {(p.tech_stack || []).map((t: string) => (
                        <span key={t} className="badge badge-gray">{t}</span>
                      ))}
                    </div>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <span className="text-xs text-gray-400 capitalize">{p.role_in_team}</span>
                    <p className="text-xs text-gray-400 mt-1">
                      {p.start_date ? new Date(p.start_date).toLocaleDateString() : ''}
                    </p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Badges */}
      {badges?.length > 0 && (
        <div className="card card-body">
          <h3 className="font-semibold mb-4">Earned badges</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {badges.map((b: any, i: number) => (
              <div key={i}
                className="flex items-center gap-3 p-3 rounded-xl border border-gray-100 bg-gray-50">
                <div className="w-10 h-10 rounded-full flex items-center justify-center text-xl flex-shrink-0"
                  style={{ background: (b.color || '#1D9E75') + '22' }}>
                  🏅
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{b.name}</p>
                  <p className="text-xs text-gray-400 truncate">{b.awarded_for}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Completed paths */}
      {completed_learning_paths?.length > 0 && (
        <div className="card card-body">
          <h3 className="font-semibold mb-3">Completed learning paths</h3>
          <div className="space-y-2">
            {completed_learning_paths.map((p: any) => (
              <div key={p.path_id} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                <span className="text-sm text-gray-700">📚 {p.title}</span>
                <span className="text-xs text-brand-600 font-medium">✓ Completed</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty state */}
      {!projects?.length && !badges?.length && !completed_learning_paths?.length && (
        <div className="card card-body text-center py-16">
          <div className="text-4xl mb-4">🚀</div>
          <h3 className="font-semibold text-gray-800 mb-2">Your portfolio is empty</h3>
          <p className="text-sm text-gray-500 max-w-xs mx-auto">
            Join a challenge team, complete learning paths, and earn badges to populate your portfolio.
          </p>
        </div>
      )}
    </div>
  )
}
