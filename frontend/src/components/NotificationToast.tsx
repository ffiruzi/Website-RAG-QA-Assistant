import React, { useEffect, useState } from 'react';
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface ToastProps {
  id: string;
  type: ToastType;
  title?: string;
  message: string;
  duration?: number;
  onClose: (id: string) => void;
}

const NotificationToast: React.FC<ToastProps> = ({
  id,
  type,
  title,
  message,
  duration = 5000,
  onClose,
}) => {
  const [isVisible, setIsVisible] = useState(true);

  // Auto-close after duration
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        setTimeout(() => onClose(id), 300); // Allow time for exit animation
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [duration, id, onClose]);

  // Handle close
  const handleClose = () => {
    setIsVisible(false);
    setTimeout(() => onClose(id), 300);
  };

  // Toast styles based on type
  const styles = {
    success: {
      bg: 'bg-green-50 dark:bg-green-900/50',
      border: 'border-green-400 dark:border-green-800',
      icon: <CheckCircle className="h-5 w-5 text-green-400 dark:text-green-300" />,
      title: title || 'Success',
    },
    error: {
      bg: 'bg-red-50 dark:bg-red-900/50',
      border: 'border-red-400 dark:border-red-800',
      icon: <XCircle className="h-5 w-5 text-red-400 dark:text-red-300" />,
      title: title || 'Error',
    },
    warning: {
      bg: 'bg-yellow-50 dark:bg-yellow-900/50',
      border: 'border-yellow-400 dark:border-yellow-800',
      icon: <AlertTriangle className="h-5 w-5 text-yellow-400 dark:text-yellow-300" />,
      title: title || 'Warning',
    },
    info: {
      bg: 'bg-blue-50 dark:bg-blue-900/50',
      border: 'border-blue-400 dark:border-blue-800',
      icon: <Info className="h-5 w-5 text-blue-400 dark:text-blue-300" />,
      title: title || 'Information',
    },
  };

  return (
    <div
      className={`
        transform transition-all duration-300 ease-in-out
        ${isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}
        max-w-sm w-full shadow-lg rounded-lg pointer-events-auto overflow-hidden
        ${styles[type].bg} border-l-4 ${styles[type].border}
      `}
      role="alert"
      aria-live="assertive"
    >
      <div className="p-4">
        <div className="flex items-start">
          <div className="flex-shrink-0">{styles[type].icon}</div>
          <div className="ml-3 w-0 flex-1 pt-0.5">
            <p className="text-sm font-medium text-gray-900 dark:text-white">{styles[type].title}</p>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-300">{message}</p>
          </div>
          <div className="ml-4 flex-shrink-0 flex">
            <button
              className="bg-transparent rounded-md inline-flex text-gray-400 hover:text-gray-500 dark:text-gray-500 dark:hover:text-gray-400 focus:outline-none"
              onClick={handleClose}
            >
              <span className="sr-only">Close</span>
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotificationToast;