import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Card from '../../components/Card';
import Button from '../../components/Button';
import Table from '../../components/Table';
import { useWebsites } from '../../hooks/useWebsites';
import { Website } from '../../contexts/WebsitesContext';

const Websites: React.FC = () => {
  const { websites, isLoading, error, fetchWebsites } = useWebsites();
  const [searchTerm, setSearchTerm] = useState('');

  // Refresh websites when component mounts
  useEffect(() => {
    fetchWebsites();
  }, []);

  // Define table columns
  const columns = [
    {
      header: 'Name',
      accessor: (website: Website) => (
        <Link to={`/websites/${website.id}`} className="text-blue-600 hover:underline dark:text-blue-400">
          {website.name}
        </Link>
      ),
    },
    {
      header: 'URL',
      accessor: (website: Website) => (
        <a
          href={website.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:underline dark:text-blue-400"
        >
          {website.url}
        </a>
      ),
    },
    {
      header: 'Status',
      accessor: (website: Website) => (
        <span
          className={`px-2 py-1 text-xs font-medium rounded-full ${
            website.is_active
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
              : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
          }`}
        >
          {website.is_active ? 'Active' : 'Inactive'}
        </span>
      ),
    },
    {
      header: 'Created',
      accessor: (website: Website) => new Date(website.created_at).toLocaleDateString(),
    },
  ];

  // Filter websites based on search term
  const filteredWebsites = websites.filter((website) => {
    if (!searchTerm) return true;
    const search = searchTerm.toLowerCase();
    return (
      website.name.toLowerCase().includes(search) ||
      website.url.toLowerCase().includes(search) ||
      (website.description && website.description.toLowerCase().includes(search))
    );
  });

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Websites</h1>
        <Link to="/websites/new">
          <Button variant="primary">Add Website</Button>
        </Link>
      </div>

      <Card>
        <div className="mb-4">
          <input
            type="text"
            placeholder="Search websites..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
        </div>

        {isLoading ? (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-2 border-blue-500 border-t-transparent"></div>
            <p className="mt-2 text-gray-500 dark:text-gray-400">Loading websites...</p>
          </div>
        ) : error ? (
          <div className="text-center py-8">
            <p className="text-red-500">Error loading websites: {error}</p>
            <Button
              variant="outline"
              className="mt-4"
              onClick={() => fetchWebsites()}
            >
              Try Again
            </Button>
          </div>
        ) : filteredWebsites.length > 0 ? (
          <Table
            columns={columns}
            data={filteredWebsites}
            keyField="id"
          />
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500 dark:text-gray-400">
              No websites found. Add your first website to get started.
            </p>
          </div>
        )}
      </Card>
    </div>
  );
};

export default Websites;