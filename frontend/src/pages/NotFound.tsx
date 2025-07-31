import React from 'react';
import { Link } from 'react-router-dom';
import Button from '../components/Button';
import { Home } from 'lucide-react';

const NotFound: React.FC = () => {
  return (
    <div className="min-h-full flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 text-center">
        <div>
          <h1 className="text-9xl font-extrabold text-blue-600 dark:text-blue-400">404</h1>
          <h2 className="mt-6 text-3xl font-bold text-gray-900 dark:text-white">
            Page Not Found
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            The page you are looking for doesn't exist or has been moved.
          </p>
        </div>
        <div className="mt-6">
          <Link to="/dashboard">
            <Button variant="primary" leftIcon={<Home className="h-4 w-4" />}>
              Back to Dashboard
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default NotFound;