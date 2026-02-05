import { useState, useEffect, createContext, useContext, type ReactNode } from 'react';
import type { User, LoginRequest, RegisterRequest } from '@/types';
import { api } from '@/services/api';
import { toast } from 'sonner';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = api.getToken();
    if (token) {
      api.getProfile()
        .then(setUser)
        .catch(() => api.clearToken())
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (credentials: LoginRequest) => {
    const { user } = await api.login(credentials);
    setUser(user);
    toast.success('登录成功');
  };

  const register = async (data: RegisterRequest) => {
    const { user } = await api.register(data);
    setUser(user);
    toast.success('注册成功');
  };

  const logout = () => {
    api.clearToken();
    setUser(null);
    toast.info('已退出登录');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
