import { AlertCircle, RefreshCw } from 'lucide-react';

const Error = ({ message, onRetry, showRetry = true }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      <div className="mb-4">
        <AlertCircle className="w-16 h-16 text-danger-500" />
      </div>
      <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-2">
        Произошла ошибка
      </h3>
      <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md">
        {message || 'Не удалось загрузить данные. Попробуйте позже.'}
      </p>
      {showRetry && onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center space-x-2 px-6 py-3 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors"
        >
          <RefreshCw className="w-5 h-5" />
          <span>Повторить</span>
        </button>
      )}
    </div>
  );
};

export default Error;
