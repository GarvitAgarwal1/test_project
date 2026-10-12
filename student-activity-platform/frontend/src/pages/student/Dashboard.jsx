import { useAuth } from '../../context/AuthContext';

export default function Dashboard() {
  const { user } = useAuth();
  
  return (
    <div>
      <h1 className="text-2xl font-semibold text-gray-900">Student Dashboard</h1>
      <p className="mt-4 text-gray-600">
        Welcome back, {user?.full_name}! Here you can manage your activities and points.
      </p>
    </div>
  );
}
