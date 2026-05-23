import create from 'zustand';
import api from '../services/api';

interface User {
  user_id: string;
  email: string;
  user_type: string;
}

interface AuthStore {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, userType: string, fullName: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),

  login: async (email: string, password: string) => {
    const response = await api.post('/auth/signin', { email, password });
    const { access_token, user_id, user_type } = response.data;
    
    localStorage.setItem('token', access_token);
    set({
      token: access_token,
      user: { user_id, email, user_type },
      isAuthenticated: true,
    });
  },

  signup: async (email: string, password: string, userType: string, fullName: string) => {
    const response = await api.post('/auth/signup', {
      email,
      password,
      user_type: userType,
      full_name: fullName,
    });
    const { access_token, user_id, user_type } = response.data;
    
    localStorage.setItem('token', access_token);
    set({
      token: access_token,
      user: { user_id, email, user_type },
      isAuthenticated: true,
    });
  },

  logout: () => {
    localStorage.removeItem('token');
    set({
      token: null,
      user: null,
      isAuthenticated: false,
    });
  },

  checkAuth: () => {
    const token = localStorage.getItem('token');
    if (token) {
      set({
        token,
        isAuthenticated: true,
      });
    }
  },
}));
