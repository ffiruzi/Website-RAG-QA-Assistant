import React, { createContext, useContext, useState, useCallback } from 'react';

// Define toast notification type
export type ToastType = 'info' | 'success' | 'warning' | 'error';

interface Toast {
  id: string;
  type: ToastType;
  title?: string;
  message: string;
  duration?: number;
}

// Define notification context type
interface NotificationContextType {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => string;
  removeToast: (id: string) => void;
  clearToasts: () => void;
}

// Create notification context
const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

// NotificationToast component
const NotificationToast: React.FC<Toast & { onClose: () => void }> = ({
  id,
  type,
  title,
  message,
  duration = 5000,
  onClose,
}) => {
  // Toast styles based on type
  const getColors = () => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-400 text-green-700 dark:bg-green-900/50 dark:border-green-800 dark:text-green-300';
      case 'error':
        return 'bg-red-50 border-red-400 text-red-700 dark:bg-red-900/50 dark:border-red-800 dark:text-red-300';
      case 'warning':
        return 'bg-yellow-50 border-yellow-400 text-yellow-700 dark:bg-yellow-900/50 dark:border-yellow-800 dark:text-yellow-300';
      default:
        return 'bg-blue-50 border-blue-400 text-blue-700 dark:bg-blue-900/50 dark:border-blue-800 dark:text-blue-300';
    }
  };

  React.useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  return (
    <div
      className={`transform transition-all duration-300 max-w-sm w-full shadow-lg rounded-lg overflow-hidden ${getColors()} border-l-4 mb-4`}
      role="alert"
    >
      <div className="p-4">
        <div className="flex">
          <div className="flex-1">
            {title && <p className="font-bold">{title}</p>}
            <p className="text-sm">{message}</p>
          </div>
          <div>
            <button
              onClick={onClose}
              className="inline-flex text-gray-400 focus:outline-none focus:text-gray-500 transition ease-in-out duration-150"
            >
              <span className="sr-only">Close</span>
              <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Toast container styles
const toastContainerStyles = {
  position: 'fixed',
  top: '1rem',
  right: '1rem',
  zIndex: 9999,
  display: 'flex',
  flexDirection: 'column',
  gap: '0.5rem',
  maxWidth: '24rem',
  width: '100%',
} as React.CSSProperties;

// Provider component
export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  // Add a new toast
  const addToast = useCallback(
    ({ type, title, message, duration }: Omit<Toast, 'id'>) => {
      // Create a unique ID
      const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

      // Create toast object
      const toast: Toast = {
        id,
        type,
        title,
        message,
        duration,
      };

      // Add toast to state
      setToasts(prevToasts => [...prevToasts, toast]);

      return id;
    },
    []
  );

  // Remove a toast
  const removeToast = useCallback((id: string) => {
    setToasts(prevToasts => prevToasts.filter(toast => toast.id !== id));
  }, []);

  // Clear all toasts
  const clearToasts = useCallback(() => {
    setToasts([]);
  }, []);

  return (
    <NotificationContext.Provider
      value={{
        toasts,
        addToast,
        removeToast,
        clearToasts,
      }}
    >
      {children}

      {/* Toast container */}
      <div style={toastContainerStyles}>
        {toasts.map(toast => (
          <NotificationToast
            key={toast.id}
            id={toast.id}
            type={toast.type}
            title={toast.title}
            message={toast.message}
            duration={toast.duration}
            onClose={() => removeToast(toast.id)}
          />
        ))}
      </div>
    </NotificationContext.Provider>
  );
};

// Hook for using notification context
export const useNotification = () => {
  const context = useContext(NotificationContext);

  if (context === undefined) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }

  return context;
};