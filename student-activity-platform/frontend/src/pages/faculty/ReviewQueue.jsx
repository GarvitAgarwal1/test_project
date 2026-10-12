import React, { useState, useEffect } from 'react';
import { getVerificationQueue, makeDecision } from '../../api/verification';
import { toast } from 'react-hot-toast';
import { format } from 'date-fns';

export default function ReviewQueue() {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchQueue();
  }, []);

  const fetchQueue = async () => {
    try {
      const data = await getVerificationQueue();
      setQueue(data.items || []);
    } catch (error) {
      toast.error('Failed to load queue');
    } finally {
      setLoading(false);
    }
  };

  const handleDecision = async (id, decision) => {
    const remarks = decision === 'REJECTED' ? prompt('Enter rejection remarks (required):') : '';
    if (decision === 'REJECTED' && !remarks) return;

    try {
      await makeDecision(id, { decision, remarks });
      toast.success(`Activity ${decision.toLowerCase()}`);
      fetchQueue();
    } catch (error) {
      toast.error('Decision failed');
    }
  };

  if (loading) return <div className="p-8 text-center text-gray-500">Loading queue...</div>;

  return (
    <div className="max-w-6xl mx-auto py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Verification Queue</h1>
      
      {queue.length === 0 ? (
        <div className="bg-white p-8 rounded-lg shadow-sm border text-center text-gray-500">
          No activities pending verification.
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {queue.map((activity) => (
              <li key={activity.id} className="p-4 hover:bg-gray-50 flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-3">
                    <p className="text-sm font-medium text-indigo-600 truncate">{activity.title}</p>
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${activity.status === 'FLAGGED' ? 'bg-orange-100 text-orange-800' : 'bg-yellow-100 text-yellow-800'}`}>
                      {activity.status}
                    </span>
                  </div>
                  <div className="mt-2 text-sm text-gray-500">
                    <p>Student: {activity.student_name} • Date: {activity.activity_date} • Category: {activity.category}</p>
                    <p>Level: {activity.level} • Organizer: {activity.organizer}</p>
                  </div>
                  {activity.anomaly_flags?.length > 0 && (
                    <div className="mt-2 text-xs text-red-600 font-medium">
                      ⚠️ Flags: {activity.anomaly_flags.map(f => f.rule_code).join(', ')}
                    </div>
                  )}
                  <div className="mt-2">
                    <a href={`/api/v1/uploads/${activity.proof_file_path}`} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-600 hover:underline">
                      View Certificate ↗
                    </a>
                  </div>
                </div>
                
                <div className="flex space-x-3">
                  <button onClick={() => handleDecision(activity.id, 'APPROVED')} className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-green-600 hover:bg-green-700">
                    Approve
                  </button>
                  <button onClick={() => handleDecision(activity.id, 'REJECTED')} className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-red-600 hover:bg-red-700">
                    Reject
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
