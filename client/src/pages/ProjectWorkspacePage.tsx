import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'
import { useAuthStore } from '../store/auth'
import api from '../services/api'
import { PageLoader, StatusBadge, Modal } from '../components/common/UI'
import { useState, useEffect, useRef } from 'react'
import { useForm } from 'react-hook-form'

const TASK_COLUMNS = [
  { key: 'todo', label: 'To Do', color: '#888780' },
  { key: 'in_progress', label: 'In Progress', color: '#EF9F27' },
  { key: 'in_review', label: 'In Review', color: '#7F77DD' },
  { key: 'done', label: 'Done', color: '#1D9E75' },
]

/** Same origin as the page so Vite's `/ws` proxy forwards to the API (see vite.config.ts). */
function projectChatWebSocketUrl(projectId: string | undefined, token: string | null) {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const q = token ? `?token=${encodeURIComponent(token)}` : ''
  return `${proto}//${window.location.host}/ws/projects/${projectId}${q}`
}

function TaskCard({ task, onStatusChange, onDelete }: { task: any; onStatusChange: (id: number, s: string) => void; onDelete: (id: number) => void }) {
  const priorityColor: Record<string, string> = { high: 'text-red-500', medium: 'text-amber-500', low: 'text-gray-400' }
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-3 shadow-sm group">
      <p className="text-sm font-medium text-gray-900 mb-2">{task.title}</p>
      {task.description && <p className="text-xs text-gray-500 mb-2 line-clamp-2">{task.description}</p>}
      <div className="flex items-center justify-between">
        <span className={`text-xs font-medium ${priorityColor[task.priority] || 'text-gray-400'}`}>
          {task.priority}
        </span>
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition">
          <select value={task.status}
            onChange={e => onStatusChange(task.id, e.target.value)}
            className="text-xs border border-gray-200 rounded px-1 py-0.5 text-gray-600">
            {TASK_COLUMNS.map(c => <option key={c.key} value={c.key}>{c.label}</option>)}
          </select>
          <button onClick={() => onDelete(task.id)} className="text-xs text-red-400 hover:text-red-600 px-1">✕</button>
        </div>
      </div>
    </div>
  )
}

export default function ProjectWorkspacePage() {
  const { id } = useParams()
  const { user } = useAuthStore()
  const qc = useQueryClient()
  const [activeTab, setActiveTab] = useState<'board' | 'milestones' | 'chat' | 'files'>('board')
  const [showAddTask, setShowAddTask] = useState(false)
  const [showAddMilestone, setShowAddMilestone] = useState(false)
  const [chatInput, setChatInput] = useState('')
  const [wsMessages, setWsMessages] = useState<any[]>([])
  const [onlineUsers, setOnlineUsers] = useState<any[]>([])
  const wsRef = useRef<WebSocket | null>(null)
  const chatEndRef = useRef<HTMLDivElement>(null)
  const { register: regTask, handleSubmit: subTask, reset: resetTask } = useForm()
  const { register: regMs, handleSubmit: subMs, reset: resetMs } = useForm()

  const { data: project, isLoading } = useQuery({
    queryKey: ['project', id],
    queryFn: () => api.get(`/projects/${id}`).then(r => r.data),
  })
  const { data: tasks } = useQuery({
    queryKey: ['tasks', id],
    queryFn: () => api.get(`/projects/${id}/tasks`).then(r => r.data),
  })
  const { data: milestones } = useQuery({
    queryKey: ['milestones', id],
    queryFn: () => api.get(`/projects/${id}/milestones`).then(r => r.data),
  })
  const { data: messages } = useQuery({
    queryKey: ['messages', id],
    queryFn: () => api.get(`/projects/${id}/messages`).then(r => r.data),
  })

  // WebSocket chat connection
  useEffect(() => {
    if (activeTab !== 'chat') return
    const token = localStorage.getItem('access_token')
    const ws = new WebSocket(projectChatWebSocketUrl(id, token))
    wsRef.current = ws
    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data)
      if (msg.type === 'message') setWsMessages(prev => [...prev, msg])
      if (msg.type === 'user_joined' || msg.type === 'user_left') setOnlineUsers(msg.online_users || [])
    }
    return () => ws.close()
  }, [id, activeTab])

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [wsMessages, messages])

  const addTaskMutation = useMutation({
    mutationFn: (data: any) => api.post(`/projects/${id}/tasks`, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['tasks', id] }); setShowAddTask(false); resetTask() },
  })
  const updateTaskMutation = useMutation({
    mutationFn: ({ taskId, status }: { taskId: number; status: string }) =>
      api.put(`/projects/${id}/tasks/${taskId}`, { status }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['tasks', id] }),
  })
  const deleteTaskMutation = useMutation({
    mutationFn: (taskId: number) => api.delete(`/projects/${id}/tasks/${taskId}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['tasks', id] }),
  })
  const addMilestoneMutation = useMutation({
    mutationFn: (data: any) => api.post(`/projects/${id}/milestones`, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['milestones', id] }); setShowAddMilestone(false); resetMs() },
  })

  const sendChatMessage = () => {
    if (!chatInput.trim() || !wsRef.current) return
    wsRef.current.send(JSON.stringify({ content: chatInput, message_type: 'text' }))
    setChatInput('')
  }

  if (isLoading) return <PageLoader />
  if (!project) return <div className="text-gray-500">Project not found</div>

  const allMessages = [...(messages || []), ...wsMessages]
  const tasksByStatus = TASK_COLUMNS.reduce((acc, col) => {
    acc[col.key] = (tasks || []).filter((t: any) => t.status === col.key)
    return acc
  }, {} as Record<string, any[]>)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">{project.title}</h1>
          <div className="flex items-center gap-3 mt-1">
            <StatusBadge status={project.status} />
            {project.github_url && (
              <a href={project.github_url} target="_blank" rel="noreferrer"
                className="text-xs text-gray-500 hover:text-brand-600 flex items-center gap-1">
                🔗 GitHub
              </a>
            )}
          </div>
        </div>
        {onlineUsers.length > 0 && (
          <div className="flex items-center gap-1.5 text-xs text-brand-600 bg-brand-50 px-3 py-1.5 rounded-full">
            <span className="w-1.5 h-1.5 rounded-full bg-brand-400 animate-pulse" />
            {onlineUsers.length} online
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-gray-100 rounded-xl w-fit">
        {([['board', '📋 Board'], ['milestones', '🎯 Milestones'], ['chat', '💬 Chat'], ['files', '📁 Files']] as const).map(([key, label]) => (
          <button key={key} onClick={() => setActiveTab(key as any)}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition
              ${activeTab === key ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}>
            {label}
          </button>
        ))}
      </div>

      {/* Board */}
      {activeTab === 'board' && (
        <div>
          <div className="flex justify-end mb-4">
            <button onClick={() => setShowAddTask(true)} className="btn-primary btn-sm">+ Add task</button>
          </div>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {TASK_COLUMNS.map(col => (
              <div key={col.key} className="bg-gray-50 rounded-xl p-3 min-h-[200px]">
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ background: col.color }} />
                  <span className="text-xs font-semibold text-gray-600 uppercase tracking-wider">{col.label}</span>
                  <span className="ml-auto text-xs text-gray-400 bg-white rounded-full px-1.5 py-0.5">
                    {tasksByStatus[col.key]?.length || 0}
                  </span>
                </div>
                <div className="space-y-2">
                  {tasksByStatus[col.key]?.map((task: any) => (
                    <TaskCard key={task.id} task={task}
                      onStatusChange={(tid, s) => updateTaskMutation.mutate({ taskId: tid, status: s })}
                      onDelete={(tid) => deleteTaskMutation.mutate(tid)} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Milestones */}
      {activeTab === 'milestones' && (
        <div className="space-y-4">
          <div className="flex justify-end">
            <button onClick={() => setShowAddMilestone(true)} className="btn-primary btn-sm">+ Add milestone</button>
          </div>
          <div className="space-y-3">
            {milestones?.map((ms: any, i: number) => (
              <div key={ms.id} className="card card-body flex items-center gap-4">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-lg flex-shrink-0
                  ${ms.status === 'completed' ? 'bg-brand-50' : ms.status === 'overdue' ? 'bg-red-50' : 'bg-gray-100'}`}>
                  {ms.status === 'completed' ? '✅' : ms.status === 'overdue' ? '⚠️' : `${i + 1}`}
                </div>
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{ms.title}</p>
                  {ms.description && <p className="text-sm text-gray-500">{ms.description}</p>}
                </div>
                <div className="text-right flex-shrink-0">
                  <StatusBadge status={ms.status} />
                  {ms.due_date && (
                    <p className="text-xs text-gray-400 mt-1">
                      {new Date(ms.due_date).toLocaleDateString()}
                    </p>
                  )}
                </div>
              </div>
            ))}
            {!milestones?.length && (
              <div className="text-center py-12 text-gray-400 text-sm">No milestones yet</div>
            )}
          </div>
        </div>
      )}

      {/* Chat */}
      {activeTab === 'chat' && (
        <div className="card flex flex-col" style={{ height: '520px' }}>
          <div className="px-4 py-3 border-b border-gray-50 flex items-center justify-between">
            <h3 className="font-semibold text-sm">Project chat</h3>
            <span className="text-xs text-gray-400">{onlineUsers.length} online now</span>
          </div>
          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3">
            {allMessages.map((m: any, i: number) => {
              const isMe = m.sender_id === user?.id || m.user_id === user?.id
              const name = m.sender_name || m.user_name || 'Unknown'
              return (
                <div key={m.id || i} className={`flex gap-2 ${isMe ? 'flex-row-reverse' : ''}`}>
                  <div className="w-7 h-7 rounded-full bg-brand-100 flex items-center justify-center text-brand-600 text-xs font-bold flex-shrink-0">
                    {name?.[0]?.toUpperCase()}
                  </div>
                  <div className={`max-w-xs ${isMe ? 'items-end' : 'items-start'} flex flex-col`}>
                    {!isMe && <span className="text-xs text-gray-500 mb-0.5">{name}</span>}
                    <div className={`px-3 py-2 rounded-2xl text-sm ${isMe
                      ? 'bg-brand-400 text-white rounded-tr-sm' : 'bg-gray-100 text-gray-900 rounded-tl-sm'}`}>
                      {m.content}
                    </div>
                    <span className="text-xs text-gray-400 mt-0.5">
                      {m.created_at ? new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'now'}
                    </span>
                  </div>
                </div>
              )
            })}
            {allMessages.length === 0 && (
              <div className="text-center py-10 text-sm text-gray-400">No messages yet. Say hello! 👋</div>
            )}
            <div ref={chatEndRef} />
          </div>
          <div className="px-4 py-3 border-t border-gray-50 flex gap-2">
            <input value={chatInput} onChange={e => setChatInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') sendChatMessage() }}
              placeholder="Type a message..." className="input flex-1" />
            <button onClick={sendChatMessage} disabled={!chatInput.trim()} className="btn-primary px-4">
              Send
            </button>
          </div>
        </div>
      )}

      {/* Files placeholder */}
      {activeTab === 'files' && (
        <div className="card card-body text-center py-16 text-gray-400">
          <div className="text-3xl mb-3">📁</div>
          <p className="font-medium text-gray-600">File sharing</p>
          <p className="text-sm mt-1">Upload project files and documents here.</p>
          <button className="btn-primary btn-sm mt-4">Upload file</button>
        </div>
      )}

      {/* Add task modal */}
      <Modal open={showAddTask} onClose={() => setShowAddTask(false)} title="Add task">
        <form onSubmit={subTask(d => addTaskMutation.mutate(d))} className="space-y-4">
          <div>
            <label className="label">Task title *</label>
            <input {...regTask('title', { required: true })} className="input" placeholder="e.g. Build login API" />
          </div>
          <div>
            <label className="label">Description</label>
            <textarea {...regTask('description')} rows={2} className="input resize-none" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Priority</label>
              <select {...regTask('priority')} className="input">
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            <div>
              <label className="label">Due date</label>
              <input {...regTask('due_date')} type="date" className="input" />
            </div>
          </div>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={() => setShowAddTask(false)} className="btn-secondary flex-1">Cancel</button>
            <button type="submit" disabled={addTaskMutation.isPending} className="btn-primary flex-1">Add task</button>
          </div>
        </form>
      </Modal>

      {/* Add milestone modal */}
      <Modal open={showAddMilestone} onClose={() => setShowAddMilestone(false)} title="Add milestone">
        <form onSubmit={subMs(d => addMilestoneMutation.mutate(d))} className="space-y-4">
          <div>
            <label className="label">Title *</label>
            <input {...regMs('title', { required: true })} className="input" placeholder="e.g. Backend API complete" />
          </div>
          <div>
            <label className="label">Description</label>
            <textarea {...regMs('description')} rows={2} className="input resize-none" />
          </div>
          <div>
            <label className="label">Due date</label>
            <input {...regMs('due_date')} type="date" className="input" />
          </div>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={() => setShowAddMilestone(false)} className="btn-secondary flex-1">Cancel</button>
            <button type="submit" disabled={addMilestoneMutation.isPending} className="btn-primary flex-1">Add milestone</button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
