import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';
import { useEffect } from 'react';

export default function Register() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirm_password: '',
    full_name: '',
    enrollment_no: '',
    department_id: '',
    year: '1'
  });
  
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { register } = useAuth();

  useEffect(() => {
    // In a real app we'd fetch this from the backend
    // For now mocking departments
    setDepartments([
      { id: 1, name: 'Computer Science' },
      { id: 2, name: 'Information Technology' },
      { id: 3, name: 'Electronics' }
    ]);
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirm_password) {
      return setError('Passwords do not match');
    }
    
    if (formData.password.length < 8) {
      return setError('Password must be at least 8 characters');
    }

    setLoading(true);
    
    try {
      const { confirm_password, ...submitData } = formData;
      // Convert strings to numbers where necessary
      submitData.department_id = parseInt(submitData.department_id);
      submitData.year = parseInt(submitData.year);
      submitData.role = 'student'; // Always student for public registration
      
      await register(submitData);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to register');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Student Registration
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">
              {error}
            </div>
          )}
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Full Name</label>
              <input name="full_name" type="text" required className="input-field mt-1" value={formData.full_name} onChange={handleChange} />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Email address</label>
              <input name="email" type="email" required className="input-field mt-1" value={formData.email} onChange={handleChange} />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Enrollment No.</label>
                <input name="enrollment_no" type="text" required className="input-field mt-1" value={formData.enrollment_no} onChange={handleChange} />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Year</label>
                <select name="year" required className="input-field mt-1" value={formData.year} onChange={handleChange}>
                  <option value="1">1st Year</option>
                  <option value="2">2nd Year</option>
                  <option value="3">3rd Year</option>
                  <option value="4">4th Year</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Department</label>
              <select name="department_id" required className="input-field mt-1" value={formData.department_id} onChange={handleChange}>
                <option value="">Select Department</option>
                {departments.map(dept => (
                  <option key={dept.id} value={dept.id}>{dept.name}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Password</label>
              <input name="password" type="password" required className="input-field mt-1" value={formData.password} onChange={handleChange} />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Confirm Password</label>
              <input name="confirm_password" type="password" required className="input-field mt-1" value={formData.confirm_password} onChange={handleChange} />
            </div>
          </div>

          <div>
            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? 'Registering...' : 'Register'}
            </button>
          </div>
          
          <div className="text-sm text-center">
            <Link to="/login" className="font-medium text-indigo-600 hover:text-indigo-500">
              Already have an account? Sign in
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
