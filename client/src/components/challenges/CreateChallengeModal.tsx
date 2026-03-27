import { useForm } from 'react-hook-form'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../services/api'
import { Modal } from '../common/UI'
import { useState } from 'react'

const SKILL_SUGGESTIONS = ['Python', 'React', 'MySQL', 'REST APIs', 'Data Analysis', 'Figma', 'Digital Marketing', 'SQL', 'Node.js', 'Machine Learning']

export default function CreateChallengeModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const qc = useQueryClient()
  const [skills, setSkills] = useState<string[]>([])
  const [skillInput, setSkillInput] = useState('')
  const { register, handleSubmit, reset, formState: { isSubmitting, errors } } = useForm()

  const mutation = useMutation({
    mutationFn: (data: any) => api.post('/challenges', { ...data, required_skills: skills }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['challenges'] }); reset(); setSkills([]); onClose() },
  })

  const addSkill = (s: string) => {
    if (s && !skills.includes(s)) setSkills([...skills, s])
    setSkillInput('')
  }
  const removeSkill = (s: string) => setSkills(skills.filter(x => x !== s))

  return (
    <Modal open={open} onClose={onClose} title="Post a new challenge">
      <form onSubmit={handleSubmit(d => mutation.mutate(d))} className="space-y-4">
        {mutation.isError && (
          <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg">
            {(mutation.error as any)?.response?.data?.detail || 'Failed to post challenge'}
          </div>
        )}

        <div>
          <label className="label">Challenge title *</label>
          <input {...register('title', { required: true })} className="input" placeholder="e.g. Build a mobile booking app" />
        </div>

        <div>
          <label className="label">Description *</label>
          <textarea {...register('description', { required: true })} rows={3} className="input resize-none"
            placeholder="Describe the digital challenge your business is facing..." />
        </div>

        <div>
          <label className="label">Problem statement</label>
          <textarea {...register('problem_statement')} rows={2} className="input resize-none"
            placeholder="What specific problem needs solving?" />
        </div>

        <div>
          <label className="label">Success criteria</label>
          <textarea {...register('success_criteria')} rows={2} className="input resize-none"
            placeholder="How will you evaluate the solution?" />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label">Category</label>
            <select {...register('category')} className="input">
              <option value="">Select category</option>
              <option value="booking_system">Booking System</option>
              <option value="digital_payments">Digital Payments</option>
              <option value="data_analytics">Data Analytics</option>
              <option value="mobile_app">Mobile App</option>
              <option value="website">Website</option>
              <option value="marketing">Digital Marketing</option>
            </select>
          </div>
          <div>
            <label className="label">Difficulty</label>
            <select {...register('difficulty_level')} className="input">
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label">Timeline (weeks)</label>
            <input {...register('estimated_weeks')} type="number" min={2} max={52} defaultValue={8} className="input" />
          </div>
          <div>
            <label className="label">Max team size</label>
            <input {...register('max_team_size')} type="number" min={1} max={8} defaultValue={4} className="input" />
          </div>
        </div>

        <div>
          <label className="label">Required skills</label>
          <div className="flex flex-wrap gap-2 mb-2">
            {skills.map(s => (
              <span key={s} className="badge badge-green cursor-pointer" onClick={() => removeSkill(s)}>
                {s} ✕
              </span>
            ))}
          </div>
          <div className="flex gap-2">
            <input value={skillInput} onChange={e => setSkillInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addSkill(skillInput) } }}
              placeholder="Add a skill and press Enter" className="input flex-1" />
          </div>
          <div className="flex flex-wrap gap-1.5 mt-2">
            {SKILL_SUGGESTIONS.filter(s => !skills.includes(s)).map(s => (
              <button key={s} type="button" onClick={() => addSkill(s)}
                className="text-xs px-2.5 py-1 rounded-full bg-gray-100 text-gray-600 hover:bg-brand-50 hover:text-brand-600 transition">
                + {s}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <input type="checkbox" {...register('is_remote')} id="remote" className="w-4 h-4 text-brand-400 rounded" defaultChecked />
          <label htmlFor="remote" className="text-sm text-gray-700">Remote collaboration OK</label>
        </div>

        <div className="flex gap-3 pt-2">
          <button type="button" onClick={onClose} className="btn-secondary flex-1">Cancel</button>
          <button type="submit" disabled={isSubmitting || mutation.isPending} className="btn-primary flex-1">
            {mutation.isPending ? 'Posting...' : 'Post challenge'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
