import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import Card from '../../components/Card';
import Button from '../../components/Button';
import { useWebsites } from '../../hooks/useWebsites';

// Mock activity type
interface Activity {
  id: number;
  name: string;
  url: string;
  type: string;
  timestamp: string;
}

const Dashboard: React.FC = () => {
  const { websites, fetchWebsites } = useWebsites();

  // Fetch websites on component mount
  useEffect(() => {
    fetchWebsites();
  }, []);

  // Mock activities
  const recentActivity: Activity[] = [
    {
      id: 1,
      name: "Example Website",
      url: "https://example.com",
      type: "website_added",
      timestamp: "2023-05-15T14:32:00Z",
    },
    {
      id: 2,
      name: "Documentation Site",
      url: "https://docs.example.com",
      type: "website_crawled",
      timestamp: "2023-05-14T09:15:00Z",
    },
    {
      id: 3,
      name: "Company Blog",
      url: "https://blog.example.com",
      type: "embeddings_updated",
      timestamp: "2023-05-12T16:45:00Z",
    },
  ];

  // Stats with real website count
  const stats = [
    {
      title: 'Websites',
      value: websites.length,
      description: 'Total websites in the system',
      color: 'bg-blue-500 dark:bg-blue-600',
    },
    {
      title: 'Conversations',
      value: 128,
      description: 'Total conversations this month',
      color: 'bg-green-500 dark:bg-green-600',
    },
    {
      title: 'Messages',
      value: '1,024',
      description: 'Total messages processed',
      color: 'bg-purple-500 dark:bg-purple-600',
    },
    {
      title: 'Processing',
      value: 2,
      description: 'Websites currently updating',
      color: 'bg-yellow-500 dark:bg-yellow-600',
    },
  ];

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <Link to="/websites/new">
          <Button variant="primary">
            Add New Website
          </Button>
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {stats.map((stat, index) => (
          <Card key={index} className="overflow-hidden">
            <div className="flex items-center">
              <div className={`flex-shrink-0 rounded-full p-3 ${stat.color} text-white`}>
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </div>
              <div className="ml-5">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {stat.title}
                </p>
                <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                  {stat.value}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {stat.description}
                </p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Recent Activity and Quick Actions Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card
          title="Recent Activity"
          subtitle="Latest changes to your websites"
        >
          <ul className="divide-y divide-gray-200 dark:divide-gray-700">
            {/* Show real websites first if available */}
            {websites.slice(0, 3).map(website => (
              <li key={website.id} className="py-4">
                <div className="flex justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {website.name}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                      {website.url}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {new Date(website.created_at).toLocaleDateString()}
                    </p>
                    <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                      Website Added
                    </p>
                  </div>
                </div>
              </li>
            ))}

            {/* Fill with mock data if needed */}
            {websites.length === 0 && recentActivity.map(activity => (
              <li key={activity.id} className="py-4">
                <div className="flex justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {activity.name}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                      {activity.url}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {formatDate(activity.timestamp)}
                    </p>
                    <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                      {activity.type === 'website_added'
                        ? 'Website Added'
                        : activity.type === 'website_crawled'
                        ? 'Content Crawled'
                        : 'Embeddings Updated'}
                    </p>
                  </div>
                </div>
              </li>
            ))}
          </ul>
          <div className="mt-4">
            <Link to="/websites">
              <Button variant="outline" className="w-full">
                View All Websites
              </Button>
            </Link>
          </div>
        </Card>

        {/* Quick Actions */}
        <Card
          title="Quick Actions"
          subtitle="Tools and common operations"
        >
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-750 transition duration-150">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">Crawl Website</h3>
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                Start a new content crawling job for one of your websites.
              </p>
              <div className="mt-4">
                <Link to="/websites">
                  <Button variant="outline" size="sm">
                    Select Website
                  </Button>
                </Link>
              </div>
            </div>
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-750 transition duration-150">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">Update Embeddings</h3>
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                Generate or update embeddings for website content.
              </p>
              <div className="mt-4">
                <Link to="/websites">
                  <Button variant="outline" size="sm">
                    Select Website
                  </Button>
                </Link>
              </div>
            </div>
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-750 transition duration-150">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">View Analytics</h3>
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                See usage statistics and performance metrics.
              </p>
              <div className="mt-4">
                <Button variant="outline" size="sm">
                  Go to Analytics
                </Button>
              </div>
            </div>
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-750 transition duration-150">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">Settings</h3>
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                Configure your account and system preferences.
              </p>
              <div className="mt-4">
                <Button variant="outline" size="sm">
                  Go to Settings
                </Button>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;