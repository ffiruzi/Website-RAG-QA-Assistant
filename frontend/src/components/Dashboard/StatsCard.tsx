import React from 'react';

interface StatsCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: React.ReactNode;
  change?: {
    value: number;
    isPositive: boolean;
  };
  className?: string;
}

const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  description,
  icon,
  change,
  className = '',
}) => {
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 ${className}`}>
      <div className="flex items-center">
        {icon && (
          <div className="flex-shrink-0 mr-4">
            {icon}
          </div>
        )}
        <div>
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
            {title}
          </p>
          <p className="mt-1 text-3xl font-semibold text-gray-900 dark:text-white">
            {value}
          </p>
          {description && (
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {description}
            </p>
          )}
          {change && (
            <div className="mt-2">
              <span
                className={`text-sm font-medium ${
                  change.isPositive
                    ? 'text-green-600 dark:text-green-400'
                    : 'text-red-600 dark:text-red-400'
                }`}
              >
                {change.isPositive ? '↑' : '↓'} {Math.abs(change.value)}%
              </span>
              <span className="ml-1 text-sm text-gray-500 dark:text-gray-400">from previous period</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StatsCard;