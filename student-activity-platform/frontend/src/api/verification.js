import axiosInstance from './axios';

export const getVerificationQueue = async (params) => {
  const response = await axiosInstance.get('/api/v1/verification/queue', { params });
  return response.data;
};

export const makeDecision = async (activityId, decisionData) => {
  const response = await axiosInstance.post(`/api/v1/verification/${activityId}/decision`, decisionData);
  return response.data;
};
