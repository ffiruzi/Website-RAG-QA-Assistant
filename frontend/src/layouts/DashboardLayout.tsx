import React, { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useTheme } from '../hooks/useTheme';
import {
  Sun,
  Moon,
  Home,
  Globe,
  BarChart2,
  Activity,
  FileText,
  Monitor,
  PieChart,
  Download
} from 'lucide-react';

const DashboardLayout: React.FC = () => {
  const { user, isLoading, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-100 dark:bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const isActive = (path: string) => {
    return location.pathname.startsWith(path);
  };

  return (
    <div className="flex h-screen bg-gray-100 dark:bg-gray-900">
      {/* Sidebar */}
      <div className="hidden md:flex md:flex-shrink-0">
        <div className="flex flex-col w-64">
          <div className="flex flex-col h-0 flex-1 bg-white dark:bg-gray-800">
            <div className="flex items-center h-16 flex-shrink-0 px-4 bg-blue-600 dark:bg-blue-800">

              <span className="ml-2 text-white font-semibold">RAG Q&A System</span>
            </div>
            <div className="flex-1 flex flex-col overflow-y-auto">
              <nav className="flex-1 px-2 py-4 space-y-1">
                <Link
                  to="/dashboard"
                  className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                    isActive('/dashboard')
                      ? 'bg-gray-100 text-blue-600 dark:bg-gray-700 dark:text-blue-400'
                      : 'text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                >
                  <Home className={`mr-3 h-5 w-5 ${
                    isActive('/dashboard')
                      ? 'text-blue-600 dark:text-blue-400'
                      : 'text-gray-500 dark:text-gray-400'
                  }`} />
                  Dashboard
                </Link>

                <Link
                  to="/websites"
                  className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                    isActive('/websites')
                      ? 'bg-gray-100 text-blue-600 dark:bg-gray-700 dark:text-blue-400'
                      : 'text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                >
                  <Globe className={`mr-3 h-5 w-5 ${
                    isActive('/websites')
                      ? 'text-blue-600 dark:text-blue-400'
                      : 'text-gray-500 dark:text-gray-400'
                  }`} />
                  Websites
                </Link>

                <div className="pt-4 pb-2">
                  <div className="px-2">
                    <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Monitoring & Analytics
                    </h3>
                  </div>
                </div>

                <Link
                  to="/analytics"
                  className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                    isActive('/analytics')
                      ? 'bg-gray-100 text-blue-600 dark:bg-gray-700 dark:text-blue-400'
                      : 'text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                >
                  <BarChart2 className={`mr-3 h-5 w-5 ${
                    isActive('/analytics')
                      ? 'text-blue-600 dark:text-blue-400'
                      : 'text-gray-500 dark:text-gray-400'
                  }`} />
                  Analytics Dashboard
                </Link>

                <Link
                  to="/monitoring/crawling"
                  className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                    isActive('/monitoring/crawling')
                      ? 'bg-gray-100 text-blue-600 dark:bg-gray-700 dark:text-blue-400'
                      : 'text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                >
                  <Activity className={`mr-3 h-5 w-5 ${
                    isActive('/monitoring/crawling')
                      ? 'text-blue-600 dark:text-blue-400'
                      : 'text-gray-500 dark:text-gray-400'
                  }`} />
                  Crawling Monitor
                </Link>

                <Link
                  to="/monitoring/performance"
                  className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                    isActive('/monitoring/performance')
                      ? 'bg-gray-100 text-blue-600 dark:bg-gray-700 dark:text-blue-400'
                      : 'text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                >
                  <Monitor className={`mr-3 h-5 w-5 ${
                    isActive('/monitoring/performance')
                      ? 'text-blue-600 dark:text-blue-400'
                      : 'text-gray-500 dark:text-gray-400'
                  }`} />
                  Performance Monitor
                </Link>

                <Link
                  to="/reports"
                  className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                    isActive('/reports')
                      ? 'bg-gray-100 text-blue-600 dark:bg-gray-700 dark:text-blue-400'
                      : 'text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                >
                  <Download className={`mr-3 h-5 w-5 ${
                    isActive('/reports')
                      ? 'text-blue-600 dark:text-blue-400'
                      : 'text-gray-500 dark:text-gray-400'
                  }`} />
                  Export Reports
                </Link>
              </nav>
            </div>
            {user && (
              <div className="flex-shrink-0 flex border-t border-gray-200 dark:border-gray-700 p-4">
                <div className="flex-shrink-0 w-full group block">
                  <div className="flex items-center">
                    <div>
                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        {user.fullName}
                      </p>
                      <p className="text-xs font-medium text-gray-500 dark:text-gray-400">
                        {user.email}
                      </p>
                    </div>
                    <button
                      onClick={logout}
                      className="ml-auto bg-gray-100 dark:bg-gray-700 p-1 rounded-full text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
                    >
                      Log out
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Mobile sidebar */}
      <div className={`md:hidden fixed inset-0 flex z-40 ${sidebarOpen ? 'block' : 'hidden'}`}>
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75" aria-hidden="true" onClick={() => setSidebarOpen(false)}></div>

        <div className="relative flex-1 flex flex-col max-w-xs w-full bg-white dark:bg-gray-800">
          <div className="absolute top-0 right-0 -mr-12 pt-2">
            <button
              type="button"
              className="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
              onClick={() => setSidebarOpen(false)}
            >
              <span className="sr-only">Close sidebar</span>
              <svg className="h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="flex-1 h-0 pt-5 pb-4 overflow-y-auto">
            <div className="flex-shrink-0 flex items-center px-4">
              <img
                className="h-8 w-auto"
                src={theme === 'dark' ? '/logo-light.svg' : '/logo-dark.svg'}
                alt="Logo"
              />
              <span className="ml-2 text-gray-900 dark:text-white font-semibold">RAG Q&A System</span>
            </div>
            <nav className="mt-5 px-2 space-y-1">
              {/* Mobile nav links - same as desktop */}
              <Link
                to="/dashboard"
                className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                  isActive('/dashboard')
                    ? 'bg-gray-100 text-blue-600 dark:bg-gray-700 dark:text-blue-400'
                    : 'text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
                onClick={() => setSidebarOpen(false)}
              >
                <Home className={`mr-3 h-5 w-5 ${
                  isActive('/dashboard')
                    ? 'text-blue-600 dark:text-blue-400'
                    : 'text-gray-500 dark:text-gray-400'
                }`} />
                Dashboard
              </Link>

              <Link
                to="/websites"
                className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                  isActive('/websites')
                    ? 'bg-gray-100 text-blue-600 dark:bg-gray-700 dark:text-blue-400'
                    : 'text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
                onClick={() => setSidebarOpen(false)}
              >
                <Globe className={`mr-3 h-5 w-5 ${
                  isActive('/websites')
                    ? 'text-blue-600 dark:text-blue-400'
                    : 'text-gray-500 dark:text-gray-400'
                }`} />
                Websites
              </Link>

              <div className="pt-4 pb-2">
                <div className="px-2">
                  <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Monitoring & Analytics
                  </h3>
                </div>
              </div>

              <Link
                to="/analytics"
                className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                  isActive('/analytics')
                    ? 'bg-gray-100 text-blue-600 dark:bg-gray-700 dark:text-blue-400'
                    : 'text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
                onClick={() => setSidebarOpen(false)}
              >
                <BarChart2 className={`mr-3 h-5 w-5 ${
                  isActive('/analytics')
                    ? 'text-blue-600 dark:text-blue-400'
                    : 'text-gray-500 dark:text-gray-400'
                }`} />
                Analytics Dashboard
              </Link>

              <Link
                to="/monitoring/crawling"
                className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                  isActive('/monitoring/crawling')
                    ? 'bg-gray-100 text-blue-600 dark:bg-gray-700 dark:text-blue-400'
                    : 'text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
                onClick={() => setSidebarOpen(false)}
              >
                <Activity className={`mr-3 h-5 w-5 ${
                  isActive('/monitoring/crawling')
                    ? 'text-blue-600 dark:text-blue-400'
                    : 'text-gray-500 dark:text-gray-400'
                }`} />
                Crawling Monitor
              </Link>

              <Link
                to="/monitoring/performance"
                className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                  isActive('/monitoring/performance')
                    ? 'bg-gray-100 text-blue-600 dark:bg-gray-700 dark:text-blue-400'
                    : 'text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
                onClick={() => setSidebarOpen(false)}
              >
                <Monitor className={`mr-3 h-5 w-5 ${
                  isActive('/monitoring/performance')
                    ? 'text-blue-600 dark:text-blue-400'
                    : 'text-gray-500 dark:text-gray-400'
                }`} />
                Performance Monitor
              </Link>

              <Link
                to="/reports"
                className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                  isActive('/reports')
                    ? 'bg-gray-100 text-blue-600 dark:bg-gray-700 dark:text-blue-400'
                    : 'text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
                onClick={() => setSidebarOpen(false)}
              >
                <Download className={`mr-3 h-5 w-5 ${
                  isActive('/reports')
                    ? 'text-blue-600 dark:text-blue-400'
                    : 'text-gray-500 dark:text-gray-400'
                }`} />
                Export Reports
              </Link>
            </nav>
          </div>

          {user && (
            <div className="flex-shrink-0 flex border-t border-gray-200 dark:border-gray-700 p-4">
              <div className="flex-shrink-0 w-full group block">
                <div className="flex items-center">
                  <div>
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      {user.fullName}
                    </p>
                    <p className="text-xs font-medium text-gray-500 dark:text-gray-400">
                      {user.email}
                    </p>
                  </div>
                  <button
                    onClick={logout}
                    className="ml-auto bg-gray-100 dark:bg-gray-700 p-1 rounded-full text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
                  >
                    Log out
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Main content */}
      <div className="flex flex-col w-0 flex-1 overflow-hidden">
        <div className="relative z-10 flex-shrink-0 flex h-16 bg-white dark:bg-gray-800 shadow">
          <button
            type="button"
            className="px-4 border-r border-gray-200 dark:border-gray-700 text-gray-500 md:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <span className="sr-only">Open sidebar</span>
            <svg className="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <div className="flex-1 px-4 flex justify-between">
            <div className="flex-1 flex"></div>
            <div className="ml-4 flex items-center md:ml-6">
              <button
                onClick={toggleTheme}
                className="p-1 rounded-full text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 focus:outline-none"
              >
                {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
              </button>
            </div>
          </div>
        </div>

        <main className="flex-1 relative overflow-y-auto focus:outline-none">
          <div className="py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
              <Outlet />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;