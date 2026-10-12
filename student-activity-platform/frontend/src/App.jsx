import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import ProtectedRoute from './components/ProtectedRoute';
import DashboardLayout from './layouts/DashboardLayout';
import StudentDashboard from './pages/student/Dashboard';
import FacultyReviewQueue from './pages/faculty/ReviewQueue';
import AdminAnalytics from './pages/admin/AnalyticsDashboard';

import AddActivity from './pages/student/AddActivity';

function App() {
  const { user, loading } = useAuth();

  if (loading) return null; // Let the auth context handle initial loading

  const getHomeRoute = () => {
    if (!user) return '/login';
    if (user.role === 'student') return '/student';
    if (user.role === 'faculty') return '/faculty';
    if (user.role === 'admin') return '/admin';
    return '/login';
  };

  return (
    <Routes>
      <Route path="/" element={<Navigate to={getHomeRoute()} replace />} />
      <Route path="/login" element={!user ? <Login /> : <Navigate to={getHomeRoute()} replace />} />
      <Route path="/register" element={!user ? <Register /> : <Navigate to={getHomeRoute()} replace />} />
      
      {/* Student Routes */}
      <Route path="/student" element={
        <ProtectedRoute allowedRoles={['student']}>
          <DashboardLayout />
        </ProtectedRoute>
      }>
        <Route index element={<StudentDashboard />} />
        <Route path="add-activity" element={<AddActivity />} />
      </Route>

      {/* Faculty Routes */}
      <Route path="/faculty" element={
        <ProtectedRoute allowedRoles={['faculty']}>
          <DashboardLayout />
        </ProtectedRoute>
      }>
        <Route index element={<FacultyReviewQueue />} />
      </Route>

      {/* Admin Routes */}
      <Route path="/admin" element={
        <ProtectedRoute allowedRoles={['admin']}>
          <DashboardLayout />
        </ProtectedRoute>
      }>
        <Route index element={<AdminAnalytics />} />
      </Route>

      {/* Fallback route */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
