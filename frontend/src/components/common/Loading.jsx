const Loading = ({ size = 'md', text }) => {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4',
    xl: 'w-16 h-16 border-5',
  };

  return (
    <div className="flex flex-col items-center justify-center space-y-4">
      <div
        className={`${sizeClasses[size]} border-primary-500 border-t-transparent rounded-full animate-spin`}
      ></div>
      {text && (
        <p className="text-gray-600 dark:text-gray-400 text-sm">{text}</p>
      )}
    </div>
  );
};

export default Loading;
