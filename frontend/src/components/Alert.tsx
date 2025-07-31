import React from 'react';
import { XCircle, CheckCircle, AlertTriangle, Info, X } from 'lucide-react';

interface AlertProps {
  type?: 'info' | 'success' | 'warning' | 'error';
  title?: string;
  message: string;
  className?: string;
  onDismiss?: () => void;
}

const Alert: React.FC<AlertProps> = ({
  type = 'info',
  title,
  message,
  className = '',
  onDismiss,
}) => {
  // Alert styles based on type
  const styles = {
    info: {
      container: 'bg-blue-50 border-blue-400 text-blue-700 dark:bg-blue-900/50 dark:border-blue-800 dark:text-blue-300',
      icon: <Info className="h-5 w-5 text-blue-400 dark:text-blue-300" />,
    },
    success: {
      container: 'bg-green-50 border-green-400 text-green-700 dark:bg-green-900/50 dark:border-green-800 dark:text-green-300',
      icon: <CheckCircle className="h-5 w-5 text-green-400 dark:text-green-300" />,
    },
    warning: {
      container: 'bg-yellow-50 border-yellow-400 text-yellow-700 dark:bg-yellow-900/50 dark:border-yellow-800 dark:text-yellow-300',
      icon: <AlertTriangle className="h-5 w-5 text-yellow-400 dark:text-yellow-300" />,
    },
    error: {
      container: 'bg-red-50 border-red-400 text-red-700 dark:bg-red-900/50 dark:border-red-800 dark:text-red-300',
      icon: <XCircle className="h-5 w-5 text-red-400 dark:text-red-300" />,
    },
  };

  return (
    <div
      className={`flex rounded-md border p-4 ${styles[type].container} ${className}`}
      role="alert"
    >
      <div className="flex-shrink-0">{styles[type].icon}</div>
      <div className="ml-3">
        {title && (
          <h3 className="text-sm font-medium">
            {title}
          </h3>
        )}
        <div className={`text-sm ${title ? 'mt-2' : ''}`}>
          {message}
        </div>
      </div>
      {onDismiss && (
        <div className="ml-auto pl-3">
          <div className="-mx-1.5 -my-1.5">
            <button
              type="button"
              className={`
                inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2
                ${type === 'info' && 'text-blue-500 hover:bg-blue-100 focus:ring-blue-600 dark:hover:bg-blue-800'}
                ${type === 'success' && 'text-green-500 hover:bg-green-100 focus:ring-green-600 dark:hover:bg-green-800'}
                ${type === 'warning' && 'text-yellow-500 hover:bg-yellow-100 focus:ring-yellow-600 dark:hover:bg-yellow-800'}
                ${type === 'error' && 'text-red-500 hover:bg-red-100 focus:ring-red-600 dark:hover:bg-red-800'}
              `}
              onClick={onDismiss}
            >
              <span className="sr-only">Dismiss</span>
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Alert;