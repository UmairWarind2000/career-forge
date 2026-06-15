import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000',
});

API.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data) => API.post('/auth/register', data),
  login: (data) => API.post('/auth/login', data),
  getMe: () => API.get('/auth/me'),
};

export const resumeAPI = {
  upload: (formData) => API.post('/resume/upload', formData),
  getMyResume: () => API.get('/resume/my-resume'),
};

export const jobsAPI = {
  getRoles: () => API.get('/jobs/roles'),
  searchJobs: (role) => API.get(`/jobs/search?role=${role}`),
  getSkillsForRole: (role) => API.get(`/jobs/${role}/skills`),
};

export const gapAPI = {
  analyze: (data) => API.post('/gap/analyze', data),
  getScore: () => API.get('/gap/score'),
  getHistory: () => API.get('/gap/history'),
};

export const roadmapAPI = {
  generate: (data) => API.post('/roadmap/generate', data),
  getLatest: () => API.get('/roadmap/latest'),
};

export const coursesAPI = {
  recommend: (data) => API.post('/courses/recommend', data),
  getForMyRoadmap: () => API.get('/courses/for-my-roadmap'),
  search: (skill) => API.get(`/courses/search?skill=${skill}`),
};

export const liveJobsAPI = {
  search: (params) => API.get('/live-jobs/search', { params }),
  getCategories: () => API.get('/live-jobs/tech-categories'),
};

export const profileAPI = {
  getProfile: () => API.get('/profile/me'),
  updateProfile: (data) => API.put('/profile/update', data),
  changePassword: (data) => API.put('/profile/change-password', data),
};

export default API;