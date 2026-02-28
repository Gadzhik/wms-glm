import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '@hooks/useAuth';
import ProtectedRoute from '@components/auth/ProtectedRoute';
import Layout from '@components/common/Layout';
import Login from '@pages/Login';
import Dashboard from '@pages/Dashboard';
import Cameras from '@pages/Cameras';
import Live from '@pages/Live';
import Archive from '@pages/Archive';
import Events from '@pages/Events';
import Settings from '@pages/Settings';

function App() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900">
        <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <Routes>
      {/* Публичные маршруты */}
      <Route path="/login" element={<Login />} />

      {/* Защищенные маршруты */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="cameras/*" element={<Cameras />} />
        <Route path="live" element={<Live />} />
        <Route path="archive/*" element={<Archive />} />
        <Route path="events" element={<Events />} />
        <Route path="settings" element={<Settings />} />
      </Route>

      {/* Редирект для неизвестных маршрутов */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;
