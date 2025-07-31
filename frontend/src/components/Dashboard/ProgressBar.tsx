import React from 'react';

interface ProgressBarProps {
  progress: number;
  className?: string;
  height?: string;
  showPercentage?: boolean;
  color?: 'blue' | 'green' | 'red' | 'yellow';
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  className = '',
  height = 'h-2',
  showPercentage = false,
  color = 'blue'
}) => {
  // Ensure progress is between 0 and 100
  const normalizedProgress = Math.max(0, Math.min(100, progress));

  // Color classes
  const colorClasses = {
    blue: 'bg-blue-600 dark:bg-blue-500',
    green: 'bg-green-600 dark:bg-green-500',
    red: 'bg-red-600 dark:bg-red-500',
    yellow: 'bg-yellow-600 dark:bg-yellow-500'
  };

  return (
    <div className={className}>
      <div className={`w-full ${height} bg-gray-200 rounded-full dark:bg-gray-700 mb-1`}>
        <div
          className={`${height} rounded-full ${colorClasses[color]}`}
          style={{ width: `${normalizedProgress}%` }}
        ></div>
      </div>
      {showPercentage && (
        <div className="text-xs font-medium text-gray-500 dark:text-gray-400">
          {normalizedProgress.toFixed(0)}%
        </div>
      )}
    </div>
  );
};

export default ProgressBar;