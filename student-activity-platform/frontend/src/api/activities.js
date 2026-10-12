import axiosInstance from './axios';

export const getMyActivities = async (params) => {
  const response = await axiosInstance.get('/api/v1/activities/mine', { params });
  return response.data;
};

export const getActivity = async (id) => {
  const response = await axiosInstance.get(`/api/v1/activities/${id}`);
  return response.data;
};

export const createActivity = async (formData) => {
  const response = await axiosInstance.post('/api/v1/activities', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};
