import React from 'react';
import { Outlet } from 'react-router-dom';
import { useTheme } from '../hooks/useTheme';

const AuthLayout: React.FC = () => {
  const { theme } = useTheme();

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <img
          className="mx-auto h-12 w-auto"
//           src={theme === 'dark' ? '/logo-light.svg' : '/logo-dark.svg'}
          alt="Logo"
        />
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
          Website RAG Q&A System
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
          Intelligent question answering for your websites
        </p>
      </div>

      <Outlet />
    </div>
  );
};

export default AuthLayout;