import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './i18n'
import { useAuthStore } from './store/auth'
import Layout from './components/common/Layout'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import ChallengesPage from './pages/ChallengesPage'
import ChallengeDetailPage from './pages/ChallengeDetailPage'
import ProjectWorkspacePage from './pages/ProjectWorkspacePage'
import LearningPage from './pages/LearningPage'
import LearningPathPage from './pages/LearningPathPage'
import MentorsPage from './pages/MentorsPage'
import PortfolioPage from './pages/PortfolioPage'
import AdminPage from './pages/AdminPage'
import ProfilePage from './pages/ProfilePage'

const qc = new QueryClient({ defaultOptions: { queries: { retry: 1, staleTime: 30000 } } })

function Guard({ children, roles }: { children: React.ReactNode; roles?: string[] }) {
  const { isAuthenticated, user } = useAuthStore()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (roles && user && !roles.includes(user.role)) return <Navigate to="/dashboard" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/" element={<Guard><Layout /></Guard>}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="challenges" element={<ChallengesPage />} />
            <Route path="challenges/:id" element={<ChallengeDetailPage />} />
            <Route path="projects/:id" element={<ProjectWorkspacePage />} />
            <Route path="learning" element={<LearningPage />} />
            <Route path="learning/paths/:id" element={<LearningPathPage />} />
            <Route path="mentors" element={<MentorsPage />} />
            <Route path="portfolio" element={<Guard roles={['student']}><PortfolioPage /></Guard>} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="admin" element={<Guard roles={['admin']}><AdminPage /></Guard>} />
          </Route>
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
