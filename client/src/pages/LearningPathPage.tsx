import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, Link } from 'react-router-dom'
import api from '../services/api'
import { PageLoader, ProgressBar } from '../components/common/UI'
import { useState } from 'react'
import { useAuthStore } from '../store/auth'

export default function LearningPathPage() {
  const { id } = useParams()
  const { user } = useAuthStore()
  const qc = useQueryClient()
  const [activeLesson, setActiveLesson] = useState<any>(null)
  const [lessonData, setLessonData] = useState<any>(null)
  const [quizAnswers, setQuizAnswers] = useState<Record<number, number>>({})
  const [quizResult, setQuizResult] = useState<any>(null)

  const { data: path, isLoading } = useQuery({
    queryKey: ['learning-path', id],
    queryFn: () => api.get(`/learning/paths/${id}`).then(r => r.data),
  })

  const enrollMutation = useMutation({
    mutationFn: () => api.post(`/learning/paths/${id}/enroll`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['learning-path', id] }),
  })

  const openLesson = async (lesson: any) => {
    setActiveLesson(lesson)
    setQuizAnswers({})
    setQuizResult(null)
    const data = await api.get(`/learning/lessons/${lesson.id}`).then(r => r.data)
    setLessonData(data)
  }

  const completeMutation = useMutation({
    mutationFn: (lessonId: number) => api.post(`/learning/lessons/${lessonId}/complete`, {
      lesson_id: lessonId,
      quiz_answers: Object.entries(quizAnswers).map(([quiz_id, selected_index]) => ({
        quiz_id: Number(quiz_id), selected_index
      }))
    }),
    onSuccess: (res) => {
      setQuizResult(res.data)
      qc.invalidateQueries({ queryKey: ['learning-path', id] })
    },
  })

  if (isLoading) return <PageLoader />
  if (!path) return <div className="text-gray-500">Path not found</div>

  return (
    <div className="max-w-5xl space-y-6">
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <Link to="/learning" className="hover:text-brand-600">Learning</Link>
        <span>/</span>
        <span className="text-gray-900">{path.title}</span>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Sidebar — modules */}
        <div className="lg:col-span-1 space-y-3">
          <div className="card card-body">
            <h2 className="font-semibold mb-1">{path.title}</h2>
            <p className="text-sm text-gray-500 mb-3">{path.description}</p>
            {path.is_enrolled ? (
              <div>
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Progress</span><span>{path.progress}%</span>
                </div>
                <ProgressBar value={path.progress} />
              </div>
            ) : user?.role === 'student' ? (
              <button onClick={() => enrollMutation.mutate()} disabled={enrollMutation.isPending}
                className="btn-primary w-full btn-sm">
                {enrollMutation.isPending ? 'Enrolling...' : 'Enroll now'}
              </button>
            ) : null}
          </div>

          {path.modules?.map((module: any) => (
            <div key={module.id} className="card overflow-hidden">
              <div className="px-4 py-3 bg-gray-50 border-b border-gray-100">
                <p className="text-sm font-semibold text-gray-800">{module.title}</p>
              </div>
              <div className="divide-y divide-gray-50">
                {module.lessons?.map((lesson: any) => (
                  <button key={lesson.id}
                    onClick={() => openLesson(lesson)}
                    className={`w-full text-left px-4 py-3 flex items-center gap-3 hover:bg-gray-50 transition
                      ${activeLesson?.id === lesson.id ? 'bg-brand-50' : ''}`}>
                    <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0
                      ${lesson.is_completed ? 'border-brand-400 bg-brand-400' : 'border-gray-300'}`}>
                      {lesson.is_completed && <span className="text-white text-xs">✓</span>}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-900 truncate">{lesson.title}</p>
                      <p className="text-xs text-gray-400">{lesson.estimated_minutes}min</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Main — lesson content */}
        <div className="lg:col-span-2">
          {!activeLesson ? (
            <div className="card card-body text-center py-16 text-gray-400">
              <div className="text-3xl mb-3">👈</div>
              <p>Select a lesson to get started</p>
            </div>
          ) : (
            <div className="card card-body space-y-6">
              <h2 className="text-xl font-semibold">{lessonData?.title || activeLesson.title}</h2>

              {/* Content */}
              {lessonData ? (
                <>
                  {lessonData.video_url && (
                    <div className="aspect-video bg-gray-100 rounded-xl overflow-hidden">
                      <iframe src={lessonData.video_url} className="w-full h-full" allowFullScreen />
                    </div>
                  )}
                  <div className="prose prose-sm max-w-none text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {lessonData.content}
                  </div>

                  {/* Quiz */}
                  {lessonData.quizzes?.length > 0 && !quizResult && (
                    <div className="border-t border-gray-100 pt-5">
                      <h3 className="font-semibold mb-4">Knowledge check</h3>
                      <div className="space-y-5">
                        {lessonData.quizzes.map((q: any) => (
                          <div key={q.id}>
                            <p className="text-sm font-medium text-gray-900 mb-3">{q.question}</p>
                            <div className="space-y-2">
                              {q.options.map((opt: string, idx: number) => (
                                <label key={idx}
                                  className={`flex items-center gap-3 p-3 rounded-xl border-2 cursor-pointer transition
                                    ${quizAnswers[q.id] === idx ? 'border-brand-400 bg-brand-50' : 'border-gray-100 hover:border-gray-200'}`}>
                                  <input type="radio" name={`quiz_${q.id}`}
                                    onChange={() => setQuizAnswers(prev => ({ ...prev, [q.id]: idx }))}
                                    className="sr-only" />
                                  <div className={`w-4 h-4 rounded-full border-2 flex-shrink-0
                                    ${quizAnswers[q.id] === idx ? 'border-brand-400 bg-brand-400' : 'border-gray-300'}`} />
                                  <span className="text-sm text-gray-700">{opt}</span>
                                </label>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Quiz result */}
                  {quizResult && (
                    <div className={`p-4 rounded-xl border ${quizResult.badge_awarded ? 'bg-brand-50 border-brand-200' : 'bg-gray-50 border-gray-200'}`}>
                      <p className="font-semibold text-gray-900">{quizResult.message}</p>
                      {quizResult.badge_awarded && (
                        <p className="text-sm text-brand-600 mt-1">🏅 Badge awarded: {quizResult.badge_awarded}</p>
                      )}
                      {quizResult.percent_complete !== undefined && (
                        <p className="text-sm text-gray-500 mt-1">Path progress: {quizResult.percent_complete}%</p>
                      )}
                    </div>
                  )}

                  {/* Complete button */}
                  {path.is_enrolled && !activeLesson.is_completed && !quizResult && (
                    <button
                      onClick={() => completeMutation.mutate(activeLesson.id)}
                      disabled={completeMutation.isPending || (lessonData.quizzes?.length > 0 && Object.keys(quizAnswers).length < lessonData.quizzes.length)}
                      className="btn-primary w-full">
                      {completeMutation.isPending ? 'Saving...' : 'Mark as complete'}
                    </button>
                  )}
                  {activeLesson.is_completed && !quizResult && (
                    <p className="text-center text-sm text-brand-600 font-medium">✓ Lesson completed</p>
                  )}
                </>
              ) : (
                <div className="flex justify-center py-8"><div className="w-6 h-6 border-2 border-brand-200 border-t-brand-400 rounded-full animate-spin" /></div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
