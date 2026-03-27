import { ReactNode } from 'react'

// ── Spinner ───────────────────────────────────────────────────────────────────
export function Spinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const s = { sm: 'w-4 h-4', md: 'w-6 h-6', lg: 'w-10 h-10' }[size]
  return (
    <div className={`${s} border-2 border-brand-200 border-t-brand-400 rounded-full animate-spin`} />
  )
}

export function PageLoader() {
  return (
    <div className="flex items-center justify-center min-h-64">
      <Spinner size="lg" />
    </div>
  )
}

// ── Empty state ────────────────────────────────────────────────────────────────
export function EmptyState({ icon, title, description, action }: {
  icon?: string; title: string; description?: string; action?: ReactNode
}) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      {icon && <div className="text-4xl mb-3">{icon}</div>}
      <h3 className="text-gray-800 font-medium mb-1">{title}</h3>
      {description && <p className="text-sm text-gray-500 max-w-xs mb-4">{description}</p>}
      {action}
    </div>
  )
}

// ── Skill chip ─────────────────────────────────────────────────────────────────
export function SkillChip({ skill }: { skill: string }) {
  return (
    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
      {skill}
    </span>
  )
}

// ── Difficulty badge ───────────────────────────────────────────────────────────
export function DifficultyBadge({ level }: { level: string }) {
  const map: Record<string, string> = {
    beginner: 'badge-green',
    intermediate: 'badge-amber',
    advanced: 'badge-red',
  }
  return <span className={map[level] || 'badge-gray'}>{level}</span>
}

// ── Status badge ───────────────────────────────────────────────────────────────
export function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    active: 'badge-green', approved: 'badge-green', completed: 'badge-purple',
    pending: 'badge-amber', submitted: 'badge-amber', under_review: 'badge-amber',
    rejected: 'badge-red', todo: 'badge-gray', in_progress: 'badge-amber',
    in_review: 'badge-purple', done: 'badge-green',
  }
  return <span className={map[status] || 'badge-gray'}>{status.replace('_', ' ')}</span>
}

// ── Progress bar ───────────────────────────────────────────────────────────────
export function ProgressBar({ value, max = 100, color = 'brand' }: {
  value: number; max?: number; color?: string
}) {
  const pct = Math.min(100, Math.round((value / max) * 100))
  return (
    <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
      <div
        className="h-2 rounded-full transition-all duration-500"
        style={{ width: `${pct}%`, background: color === 'brand' ? '#1D9E75' : color }}
      />
    </div>
  )
}

// ── Modal ──────────────────────────────────────────────────────────────────────
export function Modal({ open, onClose, title, children }: {
  open: boolean; onClose: () => void; title: string; children: ReactNode
}) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 className="text-lg font-semibold">{title}</h2>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded-lg text-gray-500">✕</button>
        </div>
        <div className="p-6">{children}</div>
      </div>
    </div>
  )
}

// ── Toast (simple) ─────────────────────────────────────────────────────────────
export function Toast({ message, type = 'success' }: { message: string; type?: 'success' | 'error' }) {
  return (
    <div className={`fixed bottom-6 right-6 z-50 flex items-center gap-3 px-5 py-3 rounded-xl shadow-lg text-white text-sm font-medium
      ${type === 'success' ? 'bg-brand-400' : 'bg-red-500'}`}>
      {type === 'success' ? '✓' : '✕'} {message}
    </div>
  )
}

// ── Score ring ─────────────────────────────────────────────────────────────────
export function ScoreRing({ score, size = 56 }: { score: number; size?: number }) {
  const r = (size - 8) / 2
  const circ = 2 * Math.PI * r
  const dash = (score / 100) * circ
  const color = score >= 70 ? '#1D9E75' : score >= 40 ? '#EF9F27' : '#E24B4A'
  return (
    <svg width={size} height={size} className="rotate-[-90deg]">
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#E5E7EB" strokeWidth="5" />
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth="5"
        strokeDasharray={`${dash} ${circ}`} strokeLinecap="round" />
      <text x={size/2} y={size/2} textAnchor="middle" dominantBaseline="central"
        className="rotate-90" style={{ transform: `rotate(90deg) translate(0, 0)`, transformOrigin: `${size/2}px ${size/2}px`,
          fill: color, fontSize: '11px', fontWeight: 600 }}>
        {Math.round(score)}
      </text>
    </svg>
  )
}
