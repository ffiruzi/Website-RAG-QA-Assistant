import React, { useEffect, useState } from 'react';
import Card from '../../components/Card';
import Button from '../../components/Button';
import Table from '../../components/Table';
import StatusBadge from '../../components/Dashboard/StatusBadge';
import ProgressBar from '../../components/Dashboard/ProgressBar';
import { useAnalytics } from '../../hooks/useAnalytics';
import { Play, Pause, RefreshCcw, AlertTriangle } from 'lucide-react';
import { formatDate, formatDuration } from '../../utils/formatters';

const CrawlingMonitor: React.FC = () => {
  const { crawlingStats, isLoading, fetchCrawlingStats } = useAnalytics();

  // Set up auto-refresh
  useEffect(() => {
    fetchCrawlingStats();

    const refreshInterval = setInterval(() => {
      fetchCrawlingStats();
    }, 10000); // Refresh every 10 seconds

    return () => clearInterval(refreshInterval);
  }, []);

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Crawling Monitor</h1>
        <Button
          variant="outline"
          onClick={() => fetchCrawlingStats()}
          leftIcon={<RefreshCcw className="h-4 w-4" />}
        >
          Refresh
        </Button>
      </div>

      {/* Active Jobs */}
      <Card title="Active Crawling Jobs" className="mb-6">
        {isLoading.crawling ? (
          <div className="flex items-center justify-center h-20">
            <div className="loader"></div>
          </div>
        ) : crawlingStats?.active_jobs && crawlingStats.active_jobs.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Website
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Progress
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Duration
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-800 dark:divide-gray-700">
                {crawlingStats.active_jobs.map((job) => {
                  const startTime = new Date(job.start_time);
                  const duration = formatDuration(new Date().getTime() - startTime.getTime());

                  return (
                    <tr key={job.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {job.website_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <StatusBadge status="running" />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <ProgressBar
                          progress={job.progress}
                          showPercentage={true}
                          height="h-2.5"
                        />
                        <span className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          {job.urls_processed} / {job.urls_total} URLs
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {duration}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Button
                          variant="outline"
                          size="sm"
                          leftIcon={<Pause className="h-4 w-4" />}
                        >
                          Pause
                        </Button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-8 text-center text-gray-500 dark:text-gray-400">
            <div className="flex flex-col items-center justify-center">
              <RefreshCcw className="h-10 w-10 text-gray-400 dark:text-gray-500 mb-4" />
              <p>No active crawling jobs</p>
              <p className="text-sm mt-2">Start a new crawling job from the website details page</p>
            </div>
          </div>
        )}
      </Card>

      {/* Recent Jobs */}
      <Card title="Recent Crawling Jobs">
        {isLoading.crawling ? (
          <div className="flex items-center justify-center h-20">
            <div className="loader"></div>
          </div>
        ) : crawlingStats?.recent_jobs && crawlingStats.recent_jobs.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Website
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Pages
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Duration
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-800 dark:divide-gray-700">
                {crawlingStats.recent_jobs.map((job) => {
                  const startTime = new Date(job.start_time);
                  const endTime = job.end_time ? new Date(job.end_time) : null;
                  const duration = endTime
                    ? formatDuration(endTime.getTime() - startTime.getTime())
                    : 'In progress';

                  return (
                    <tr key={job.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {job.website_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <StatusBadge status={job.status} />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {job.urls_processed} / {job.urls_total}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {duration}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {job.status === 'failed' ? (
                          <Button
                            variant="outline"
                            size="sm"
                            leftIcon={<Play className="h-4 w-4" />}
                          >
                            Retry
                          </Button>
                        ) : (
                          <Button
                            variant="outline"
                            size="sm"
                          >
                            View Details
                          </Button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-4 text-center text-gray-500 dark:text-gray-400">
            No recent jobs found
          </div>
        )}
      </Card>

      {/* Job Details (for if an error occurred) */}
      {crawlingStats?.recent_jobs && crawlingStats.recent_jobs.some(job => job.error) && (
        <Card title="Error Details" className="mt-6">
          {crawlingStats.recent_jobs
            .filter(job => job.error)
            .map((job, idx) => (
              <div key={idx} className="p-4 mb-4 border border-red-200 rounded-lg bg-red-50 dark:bg-red-900/20 dark:border-red-800">
                <div className="flex items-center mb-2">
                  <AlertTriangle className="h-5 w-5 text-red-500 mr-2" />
                  <h3 className="text-lg font-medium text-red-800 dark:text-red-300">
                    Error in job for {job.website_name}
                  </h3>
                </div>
                <p className="text-sm text-red-700 dark:text-red-200 mb-2">
                  Time: {formatDate(job.end_time)} - Processed {job.urls_processed} of {job.urls_total} URLs
                </p>
                <div className="bg-white p-3 rounded border border-red-300 dark:bg-red-900/30 dark:border-red-700">
                  <code className="text-sm text-red-800 dark:text-red-200 font-mono whitespace-pre-wrap">
                    {job.error}
                  </code>
                </div>
              </div>
            ))}
        </Card>
      )}
    </div>
  );
};

export default CrawlingMonitor;