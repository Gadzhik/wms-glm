import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authStore } from '@store/authStore';

export const useAuth = () => {
  const navigate = useNavigate();
  const {
    user,
    token,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    changePassword,
    getCurrentUser,
    clearError,
    updateUser,
  } = authStore();

  useEffect(() => {
    // Проверяем наличие токена при загрузке
    if (token && !user) {
      getCurrentUser().catch(() => {
        // Если не удалось получить пользователя, выходим
        logout();
      });
    }
  }, [token, user, getCurrentUser, logout]);

  const handleLogin = async (username, password) => {
    const result = await login(username, password);
    if (result.success) {
      navigate('/dashboard');
    }
    return result;
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleChangePassword = async (oldPassword, newPassword) => {
    return await changePassword(oldPassword, newPassword);
  };

  const hasPermission = (permission) => {
    if (!user) return false;
    // Администратор имеет все права
    if (user.role === 'admin') return true;
    // Проверяем права пользователя
    return user.permissions?.includes(permission) || false;
  };

  const isAdmin = user?.role === 'admin';

  return {
    user,
    token,
    isAuthenticated,
    isLoading,
    error,
    login: handleLogin,
    logout: handleLogout,
    changePassword: handleChangePassword,
    getCurrentUser,
    clearError,
    updateUser,
    hasPermission,
    isAdmin,
  };
};
