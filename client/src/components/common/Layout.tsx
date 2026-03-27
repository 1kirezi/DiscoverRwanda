import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuthStore } from '../../store/auth'
import { useState } from 'react'

const icons: Record<string, string> = {
  dashboard: '⊞', challenges: '🏆', projects: '🗂️', learning: '📚',
  mentors: '🤝', portfolio: '🎨', admin: '⚙️', profile: '👤',
}

export default function Layout() {
  const { t, i18n } = useTranslation()
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const links = [
    { to: '/dashboard', label: t('nav.dashboard'), icon: icons.dashboard, roles: ['student','business','faculty','admin'] },
    { to: '/challenges', label: t('nav.challenges'), icon: icons.challenges, roles: ['student','business','faculty','admin'] },
    { to: '/learning', label: t('nav.learning'), icon: icons.learning, roles: ['student','faculty'] },
    { to: '/mentors', label: t('nav.mentors'), icon: icons.mentors, roles: ['student','faculty','admin'] },
    { to: '/portfolio', label: t('nav.portfolio'), icon: icons.portfolio, roles: ['student'] },
    { to: '/admin', label: t('nav.admin'), icon: icons.admin, roles: ['admin'] },
  ].filter(l => user && l.roles.includes(user.role))

  const handleLogout = () => { logout(); navigate('/login') }

  return (
    <div className="min-h-screen flex bg-gray-50">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/40 z-20 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-30 w-64 bg-white border-r border-gray-100 flex flex-col transition-transform duration-200
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 lg:static lg:z-auto`}>

        {/* Logo */}
        <div className="px-6 py-5 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-brand-400 flex items-center justify-center text-white font-bold text-sm">DR</div>
            <div>
              <p className="font-semibold text-gray-900 text-sm leading-none">Discover Rwanda</p>
              <p className="text-xs text-gray-400 mt-0.5">Tourism Tech Platform</p>
            </div>
          </div>
        </div>

        {/* Nav links */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {links.map(link => (
            <NavLink key={link.to} to={link.to}
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
              onClick={() => setSidebarOpen(false)}>
              <span className="text-base">{link.icon}</span>
              {link.label}
            </NavLink>
          ))}
        </nav>

        {/* User section */}
        <div className="px-3 py-4 border-t border-gray-100 space-y-2">
          {/* Language switcher */}
          <div className="flex gap-1 px-1">
            {['en','fr','pt'].map(lang => (
              <button key={lang}
                onClick={() => { i18n.changeLanguage(lang); localStorage.setItem('lang', lang) }}
                className={`flex-1 py-1 text-xs rounded font-medium transition
                  ${i18n.language === lang ? 'bg-brand-50 text-brand-600' : 'text-gray-400 hover:text-gray-600'}`}>
                {lang.toUpperCase()}
              </button>
            ))}
          </div>

          <NavLink to="/profile" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            onClick={() => setSidebarOpen(false)}>
            {user?.avatar_url
              ? <img src={user.avatar_url} className="w-6 h-6 rounded-full object-cover" alt="" />
              : <div className="w-6 h-6 rounded-full bg-brand-100 flex items-center justify-center text-brand-600 text-xs font-bold">
                  {user?.full_name?.[0]?.toUpperCase()}
                </div>
            }
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-800 truncate">{user?.full_name}</p>
              <p className="text-xs text-gray-400 capitalize">{user?.role}</p>
            </div>
          </NavLink>

          <button onClick={handleLogout}
            className="sidebar-link w-full text-red-500 hover:text-red-600 hover:bg-red-50">
            <span>↩</span> {t('auth.logout')}
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile topbar */}
        <header className="lg:hidden flex items-center justify-between px-4 py-3 bg-white border-b border-gray-100">
          <button onClick={() => setSidebarOpen(true)} className="p-2 rounded-lg hover:bg-gray-100 text-gray-600">
            ☰
          </button>
          <span className="font-semibold text-gray-900 text-sm">Discover Rwanda</span>
          <div className="w-9" />
        </header>

        <main className="flex-1 p-4 md:p-6 lg:p-8 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
