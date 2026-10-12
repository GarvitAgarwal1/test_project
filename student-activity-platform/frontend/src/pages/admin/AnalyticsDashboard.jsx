import { useAuth } from '../../context/AuthContext';

export default function AnalyticsDashboard() {
  const { user } = useAuth();
  
  return (
    <div>
      <h1 className="text-2xl font-semibold text-gray-900">Admin Analytics Dashboard</h1>
      <p className="mt-4 text-gray-600">
        Welcome back, {user?.full_name}. Here you can view platform analytics and manage system settings.
      </p>
    </div>
  );
}
