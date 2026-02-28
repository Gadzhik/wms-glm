import { formatStatus, getStatusColor } from '@utils/format';

const CameraStatus = ({ status, size = 'sm' }) => {
  const statusColor = getStatusColor(status);
  const statusLabel = formatStatus(status);

  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base',
  };

  const colorClasses = {
    success: 'bg-success-100 dark:bg-success-900/30 text-success-700 dark:text-success-300',
    danger: 'bg-danger-100 dark:bg-danger-900/30 text-danger-700 dark:text-danger-300',
    warning: 'bg-warning-100 dark:bg-warning-900/30 text-warning-700 dark:text-warning-300',
    primary: 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300',
    default: 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300',
  };

  const dotColorClasses = {
    success: 'bg-success-500',
    danger: 'bg-danger-500',
    warning: 'bg-warning-500',
    primary: 'bg-primary-500',
    default: 'bg-gray-500',
  };

  return (
    <div
      className={`inline-flex items-center space-x-1.5 rounded-full ${sizeClasses[size]} ${colorClasses[statusColor]}`}
    >
      <div className={`w-2 h-2 rounded-full ${dotColorClasses[statusColor]} ${
        status === 'online' ? 'animate-pulse' : ''
      }`}></div>
      <span className="font-medium">{statusLabel}</span>
    </div>
  );
};

export default CameraStatus;
