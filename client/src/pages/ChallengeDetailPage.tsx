import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'
import { useAuthStore } from '../store/auth'
import api from '../services/api'
import { PageLoader, SkillChip, DifficultyBadge, StatusBadge, Modal } from '../components/common/UI'
import { useState } from 'react'
import { useForm } from 'react-hook-form'

export default function ChallengeDetailPage() {
  const { id } = useParams()
  const { user } = useAuthStore()
  const qc = useQueryClient()
  const [showCreateTeam, setShowCreateTeam] = useState(false)
  const [joiningTeamId, setJoiningTeamId] = useState<number | null>(null)
  const { register, handleSubmit, reset } = useForm()

  const { data: challenge, isLoading } = useQuery({
    queryKey: ['challenge', id],
    queryFn: () => api.get(`/challenges/${id}`).then(r => r.data),
  })

  const { data: teams } = useQuery({
    queryKey: ['teams', id],
    queryFn: () => api.get(`/challenges/${id}/teams`).then(r => r.data),
  })

  const createTeamMutation = useMutation({
    mutationFn: (data: any) => api.post(`/challenges/${id}/teams`, { challenge_id: Number(id), ...data }),
    onSuccess: (res) => {
      qc.invalidateQueries({ queryKey: ['teams', id] })
      setShowCreateTeam(false)
      reset()
    },
  })

  const joinTeamMutation = useMutation({
    mutationFn: (teamId: number) => api.post(`/challenges/${id}/teams/${teamId}/join`, {}),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['teams', id] }); setJoiningTeamId(null) },
  })

  if (isLoading) return <PageLoader />
  if (!challenge) return <div className="text-gray-500">Challenge not found</div>

  const isStudent = user?.role === 'student'
  const isFaculty = user?.role === 'faculty'
  const isAdmin = user?.role === 'admin'
  const userTeam = teams?.find((t: any) => t.members?.some((m: any) => m.user_id === user?.id))

  return (
    <div className="max-w-4xl space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 text-sm text-gray-500 mb-3">
          <Link to="/challenges" className="hover:text-brand-600">Challenges</Link>
          <span>/</span>
          <span className="text-gray-900">{challenge.title}</span>
        </div>
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">{challenge.title}</h1>
            {challenge.business_name && (
              <p className="text-gray-500 mt-1">by {challenge.business_name}</p>
            )}
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <StatusBadge status={challenge.status} />
            {isAdmin && challenge.status === 'submitted' && (
              <div className="flex gap-2">
                <button onClick={() => api.post(`/challenges/${id}/review`, { action: 'approve' }).then(() => qc.invalidateQueries({ queryKey: ['challenge', id] }))}
                  className="btn btn-sm bg-brand-400 text-white hover:bg-brand-600">Approve</button>
                <button onClick={() => api.post(`/challenges/${id}/review`, { action: 'reject' }).then(() => qc.invalidateQueries({ queryKey: ['challenge', id] }))}
                  className="btn btn-sm bg-red-100 text-red-700 hover:bg-red-200">Reject</button>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Main content */}
        <div className="lg:col-span-2 space-y-6">
          <div className="card card-body">
            <h3 className="font-semibold mb-3">About this challenge</h3>
            <p className="text-gray-600 leading-relaxed">{challenge.description}</p>
          </div>

          {challenge.problem_statement && (
            <div className="card card-body">
              <h3 className="font-semibold mb-2">Problem statement</h3>
              <p className="text-gray-600 leading-relaxed">{challenge.problem_statement}</p>
            </div>
          )}

          {challenge.success_criteria && (
            <div className="card card-body">
              <h3 className="font-semibold mb-2">Success criteria</h3>
              <p className="text-gray-600 leading-relaxed">{challenge.success_criteria}</p>
            </div>
          )}

          {/* Teams */}
          <div className="card">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-50">
              <h3 className="font-semibold">Teams ({teams?.length || 0})</h3>
              {(isStudent || isFaculty) && !userTeam && challenge.status === 'active' && (
                <button onClick={() => setShowCreateTeam(true)} className="btn-primary btn-sm">
                  {isFaculty ? '+ Create team (Faculty)' : '+ Create team'}
                </button>
              )}
            </div>
            <div className="divide-y divide-gray-50">
              {teams?.map((team: any) => {
                const isMember = team.members?.some((m: any) => m.user_id === user?.id)
                const isFull = team.members?.length >= team.max_members
                return (
                  <div key={team.id} className="px-6 py-4">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <p className="font-medium text-gray-900">{team.name}</p>
                        <p className="text-xs text-gray-500">{team.members?.length}/{team.max_members} members · {team.formation_type.replace('_', ' ')}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        {isMember && team.project && (
                          <Link to={`/projects/${team.project?.id || 1}`} className="btn btn-sm bg-brand-50 text-brand-600 hover:bg-brand-100">
                            Open workspace
                          </Link>
                        )}
                        {isStudent && !isMember && !userTeam && !isFull && (
                          <button onClick={() => joinTeamMutation.mutate(team.id)}
                            disabled={joinTeamMutation.isPending}
                            className="btn-primary btn-sm">
                            Join team
                          </button>
                        )}
                        {isFull && !isMember && <span className="text-xs text-gray-400">Full</span>}
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {team.members?.map((m: any) => (
                        <div key={m.user_id} className="flex items-center gap-1.5 bg-gray-50 px-2.5 py-1 rounded-full">
                          <div className="w-4 h-4 rounded-full bg-brand-100 flex items-center justify-center text-brand-600 text-xs font-bold">
                            {m.name?.[0]}
                          </div>
                          <span className="text-xs text-gray-700">{m.name}</span>
                          {m.role === 'lead' && <span className="text-xs text-amber-600">★</span>}
                        </div>
                      ))}
                    </div>
                    {team.disciplines_represented?.length > 1 && (
                      <p className="text-xs text-brand-600 mt-2">✓ Interdisciplinary team</p>
                    )}
                  </div>
                )
              })}
              {(!teams || teams.length === 0) && (
                <div className="px-6 py-8 text-center text-sm text-gray-400">
                  No teams yet. {isStudent && 'Be the first to create one!'}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <div className="card card-body space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Difficulty</span>
              <DifficultyBadge level={challenge.difficulty_level} />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Timeline</span>
              <span className="text-sm font-medium">{challenge.estimated_weeks} weeks</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Team size</span>
              <span className="text-sm font-medium">Up to {challenge.max_team_size}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Location</span>
              <span className="text-sm font-medium">{challenge.is_remote ? '🌐 Remote' : challenge.location || 'On-site'}</span>
            </div>
            {challenge.deadline && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Deadline</span>
                <span className="text-sm font-medium">{new Date(challenge.deadline).toLocaleDateString()}</span>
              </div>
            )}
          </div>

          <div className="card card-body">
            <h4 className="text-sm font-semibold mb-3">Required skills</h4>
            <div className="flex flex-wrap gap-1.5">
              {challenge.required_skills?.map((s: string) => <SkillChip key={s} skill={s} />)}
            </div>
          </div>
        </div>
      </div>

      {/* Create team modal */}
      <Modal
        open={showCreateTeam}
        onClose={() => setShowCreateTeam(false)}
        title={isFaculty ? 'Create a new team (Faculty)' : 'Create a new team'}
      >
        <form onSubmit={handleSubmit(d => createTeamMutation.mutate(d))} className="space-y-4">
          <div>
            <label className="label">Team name *</label>
            <input {...register('name', { required: true })} className="input" placeholder="e.g. TechPioneers" />
          </div>
          <div>
            <label className="label">Formation type</label>
            <select {...register('formation_type')} className="input">
              <option value="self_organized">Self-organized</option>
              <option value="instructor_assigned">Instructor assigned</option>
            </select>
          </div>
          <p className="text-xs text-gray-500">Note: Teams must include students from at least 2 academic disciplines (BR 7).</p>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={() => setShowCreateTeam(false)} className="btn-secondary flex-1">Cancel</button>
            <button type="submit" disabled={createTeamMutation.isPending} className="btn-primary flex-1">
              {createTeamMutation.isPending ? 'Creating...' : 'Create team'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
