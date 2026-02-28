import { Navigate } from 'react-router-dom';
import { useAuth } from '@hooks/useAuth';
import LoginForm from '@components/auth/LoginForm';

const Login = () => {
  const { isAuthenticated } = useAuth();

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <LoginForm />;
};

export default Login;
