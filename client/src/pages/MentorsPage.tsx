import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import api from '../services/api'
import { PageLoader, EmptyState, Modal } from '../components/common/UI'

export default function MentorsPage() {
  const [showBook, setShowBook] = useState<any>(null)
  const { register, handleSubmit, reset } = useForm()

  const { data: mentors, isLoading } = useQuery({
    queryKey: ['mentors'],
    queryFn: () => api.get('/mentors').then(r => r.data),
  })

  const bookMutation = useMutation({
    mutationFn: (data: any) => api.post('/mentors/sessions/book', data),
    onSuccess: () => { setShowBook(null); reset() },
  })

  if (isLoading) return <PageLoader />

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Industry mentors</h1>

      <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
        {mentors?.map((m: any) => (
          <div key={m.id} className="card card-body flex flex-col gap-3">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-brand-100 flex items-center justify-center text-brand-600 text-xl font-bold flex-shrink-0">
                {m.name?.[0]}
              </div>
              <div>
                <p className="font-semibold text-gray-900">{m.name}</p>
                <p className="text-sm text-gray-500">{m.job_title} @ {m.company}</p>
              </div>
            </div>

            {m.bio && <p className="text-sm text-gray-600 line-clamp-3">{m.bio}</p>}

            <div className="flex flex-wrap gap-1.5">
              {(m.expertise_areas || []).map((e: string) => (
                <span key={e} className="badge badge-green">{e}</span>
              ))}
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-gray-50">
              <div className="flex items-center gap-1 text-amber-500 text-sm">
                ★ <span className="font-medium">{m.rating || '—'}</span>
                <span className="text-gray-400 text-xs ml-1">({m.total_sessions} sessions)</span>
              </div>
              <button onClick={() => setShowBook(m)} className="btn-primary btn-sm">Book session</button>
            </div>
          </div>
        ))}
        {!mentors?.length && (
          <div className="col-span-full">
            <EmptyState icon="🤝" title="No mentors available yet"
              description="Industry mentors will appear here once they register." />
          </div>
        )}
      </div>

      {/* Book session modal */}
      <Modal open={!!showBook} onClose={() => { setShowBook(null); reset() }}
        title={`Book a session with ${showBook?.name}`}>
        <form onSubmit={handleSubmit(d => bookMutation.mutate({ ...d, mentor_id: showBook?.user_id }))}
          className="space-y-4">
          {bookMutation.isError && (
            <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg">
              {(bookMutation.error as any)?.response?.data?.detail || 'Booking failed'}
            </div>
          )}
          {bookMutation.isSuccess && (
            <div className="p-3 bg-brand-50 text-brand-700 text-sm rounded-lg">Session booked successfully!</div>
          )}
          <div>
            <label className="label">Date & time *</label>
            <input type="datetime-local" {...register('scheduled_at', { required: true })} className="input" />
          </div>
          <div>
            <label className="label">Duration</label>
            <select {...register('duration_minutes')} className="input">
              <option value="30">30 minutes</option>
              <option value="60">60 minutes</option>
              <option value="90">90 minutes</option>
            </select>
          </div>
          <div>
            <label className="label">Session objectives</label>
            <textarea {...register('objectives')} rows={3} className="input resize-none"
              placeholder="What do you want to learn or discuss?" />
          </div>
          <div>
            <label className="label">Meeting URL (optional)</label>
            <input {...register('meeting_url')} className="input" placeholder="https://meet.google.com/..." />
          </div>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={() => { setShowBook(null); reset() }} className="btn-secondary flex-1">
              Cancel
            </button>
            <button type="submit" disabled={bookMutation.isPending} className="btn-primary flex-1">
              {bookMutation.isPending ? 'Booking...' : 'Confirm booking'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
