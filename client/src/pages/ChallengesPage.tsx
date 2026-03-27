import { useQuery } from '@tanstack/react-query'
import { Link, useSearchParams } from 'react-router-dom'
import { useAuthStore } from '../store/auth'
import api from '../services/api'
import { PageLoader, SkillChip, DifficultyBadge, StatusBadge, EmptyState, ScoreRing } from '../components/common/UI'
import { useState } from 'react'
import CreateChallengeModal from '../components/challenges/CreateChallengeModal'

function ChallengeCard({ challenge, matchScore }: { challenge: any; matchScore?: number }) {
  return (
    <Link to={`/challenges/${challenge.id}`}
      className="card card-body hover:shadow-md transition-all duration-200 block group">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 group-hover:text-brand-600 transition-colors truncate">
            {challenge.title}
          </h3>
          {challenge.business_name && (
            <p className="text-xs text-gray-400 mt-0.5">{challenge.business_name}</p>
          )}
        </div>
        {matchScore !== undefined && <ScoreRing score={matchScore} />}
      </div>

      <p className="text-sm text-gray-600 line-clamp-2 mb-4">{challenge.description}</p>

      <div className="flex flex-wrap gap-1.5 mb-4">
        {(challenge.required_skills || []).slice(0, 4).map((s: string) => (
          <SkillChip key={s} skill={s} />
        ))}
        {(challenge.required_skills || []).length > 4 && (
          <span className="badge badge-gray">+{challenge.required_skills.length - 4}</span>
        )}
      </div>

      <div className="flex items-center justify-between pt-3 border-t border-gray-50">
        <div className="flex items-center gap-3">
          <DifficultyBadge level={challenge.difficulty_level} />
          <span className="text-xs text-gray-400">{challenge.estimated_weeks}w</span>
          {challenge.is_remote && <span className="text-xs text-gray-400">🌐 Remote</span>}
        </div>
        <StatusBadge status={challenge.status} />
      </div>
    </Link>
  )
}

export default function ChallengesPage() {
  const { user } = useAuthStore()
  const [searchParams, setSearchParams] = useSearchParams()
  const tab = searchParams.get('tab') || 'all'
  const [search, setSearch] = useState('')
  const [difficulty, setDifficulty] = useState('')
  const [showCreate, setShowCreate] = useState(false)

  const { data: challenges, isLoading } = useQuery({
    queryKey: ['challenges', search, difficulty],
    queryFn: () => api.get('/challenges', { params: { search: search || undefined, difficulty: difficulty || undefined } }).then(r => r.data),
  })

  const { data: matches, isLoading: matchLoading } = useQuery({
    queryKey: ['matches'],
    queryFn: () => api.get('/challenges/matched').then(r => r.data),
    enabled: user?.role === 'student',
  })

  const isStudent = user?.role === 'student'
  const isBusiness = user?.role === 'business'

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Challenges</h1>
        {isBusiness && (
          <button onClick={() => setShowCreate(true)} className="btn-primary">+ Post challenge</button>
        )}
      </div>

      {/* Tabs */}
      {isStudent && (
        <div className="flex gap-1 p-1 bg-gray-100 rounded-xl w-fit">
          {[['all', 'All challenges'], ['matched', 'My matches']].map(([value, label]) => (
            <button key={value}
              onClick={() => setSearchParams({ tab: value })}
              className={`px-4 py-2 text-sm font-medium rounded-lg transition
                ${tab === value ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}>
              {label}
            </button>
          ))}
        </div>
      )}

      {/* Filters */}
      {tab === 'all' && (
        <div className="flex gap-3 flex-wrap">
          <input value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Search challenges..." className="input max-w-xs" />
          <select value={difficulty} onChange={e => setDifficulty(e.target.value)} className="input w-auto">
            <option value="">All difficulties</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>
      )}

      {/* Content */}
      {tab === 'matched' ? (
        matchLoading ? <PageLoader /> : (
          <div className="space-y-4">
            {matches?.length === 0 && (
              <EmptyState icon="🎯" title="No matches yet"
                description="Complete your student profile with skills and interests to get matched with challenges." />
            )}
            {matches?.map((m: any) => (
              <div key={m.challenge.id}>
                <div className="mb-1 px-1 flex items-center gap-2 text-xs text-gray-500">
                  <span>Skills {m.score_breakdown.skills}%</span>
                  <span>·</span>
                  <span>Program {m.score_breakdown.program}%</span>
                  <span>·</span>
                  <span>Availability {m.score_breakdown.availability}%</span>
                </div>
                <ChallengeCard challenge={m.challenge} matchScore={m.match_score} />
              </div>
            ))}
          </div>
        )
      ) : (
        isLoading ? <PageLoader /> : (
          <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
            {challenges?.map((c: any) => <ChallengeCard key={c.id} challenge={c} />)}
            {challenges?.length === 0 && (
              <div className="col-span-full">
                <EmptyState icon="🏆" title="No challenges found" description="Try adjusting your search or filters." />
              </div>
            )}
          </div>
        )
      )}

      <CreateChallengeModal open={showCreate} onClose={() => setShowCreate(false)} />
    </div>
  )
}
