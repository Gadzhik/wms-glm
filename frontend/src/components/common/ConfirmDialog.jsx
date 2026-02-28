import { AlertTriangle } from 'lucide-react';

const ConfirmDialog = ({
  isOpen,
  title,
  message,
  confirmText = 'Подтвердить',
  cancelText = 'Отмена',
  onConfirm,
  onCancel,
  type = 'danger',
}) => {
  if (!isOpen) return null;

  const typeClasses = {
    danger: {
      icon: 'text-danger-500',
      confirmBtn: 'bg-danger-500 hover:bg-danger-600 text-white',
    },
    warning: {
      icon: 'text-warning-500',
      confirmBtn: 'bg-warning-500 hover:bg-warning-600 text-white',
    },
    info: {
      icon: 'text-primary-500',
      confirmBtn: 'bg-primary-500 hover:bg-primary-600 text-white',
    },
  };

  const classes = typeClasses[type] || typeClasses.danger;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Overlay */}
      <div
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={onCancel}
      ></div>

      {/* Dialog */}
      <div className="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
        <div className="flex items-start space-x-4">
          <div className={`flex-shrink-0 ${classes.icon}`}>
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              {title}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              {message}
            </p>
          </div>
        </div>

        <div className="flex justify-end space-x-3">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            className={`px-4 py-2 rounded-lg transition-colors ${classes.confirmBtn}`}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmDialog;
