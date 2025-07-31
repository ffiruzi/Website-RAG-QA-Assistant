import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Card from '../../components/Card';
import Button from '../../components/Button';
import BarChart from '../../components/charts/BarChart';
import PieChart from '../../components/charts/PieChart';
import { useAnalytics } from '../../hooks/useAnalytics';
import { useWebsites } from '../../hooks/useWebsites';
import { ArrowLeft, RefreshCcw, FileText, FolderOpen } from 'lucide-react';

const ContentCoverageDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const websiteId = parseInt(id || '0');
  const navigate = useNavigate();
  const { getWebsite } = useWebsites();
  const website = getWebsite(websiteId);

  const {
    contentCoverage,
    isLoading,
    fetchContentCoverage
  } = useAnalytics();

  useEffect(() => {
    if (websiteId) {
      fetchContentCoverage(websiteId);
    }
  }, [websiteId]);

  // Get the data for this website
  const coverage = contentCoverage[websiteId];

  // Prepare data for content type distribution
  const contentTypeData = coverage?.by_content_type.map(item => ({
    name: item.type.charAt(0).toUpperCase() + item.type.slice(1),
    value: item.count,
    color: item.type === 'blog' ? '#60A5FA' :
           item.type === 'documentation' ? '#4ADE80' :
           item.type === 'product' ? '#F59E0B' : '#8B5CF6'
  })) || [];

  // Prepare data for page status
  const pageStatusData = coverage ? [
    {
      name: 'Indexed',
      value: coverage.pages.indexed,
      color: '#4ADE80' // green-400
    },
    {
      name: 'Crawled (Not Indexed)',
      value: coverage.pages.crawled - coverage.pages.indexed,
      color: '#FBBF24' // yellow-400
    },
    {
      name: 'Not Crawled',
      value: coverage.pages.total - coverage.pages.crawled,
      color: '#F87171' // red-400
    }
  ] : [];

  return (
    <div>
      <div className="flex items-center mb-6">
        <Button
          variant="outline"
          onClick={() => navigate(`/websites/${websiteId}`)}
          className="mr-4"
          leftIcon={<ArrowLeft className="h-4 w-4" />}
        >
          Back to Website
        </Button>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Content Coverage for {website?.name || 'Website'}
        </h1>
      </div>

      {/* Coverage Summary */}
      <Card className="mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="flex flex-col">
            <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Pages</span>
            <span className="text-3xl font-bold text-gray-900 dark:text-white">{coverage?.pages.total || 0}</span>
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Crawled Pages</span>
            <span className="text-3xl font-bold text-green-600 dark:text-green-400">{coverage?.pages.crawled || 0}</span>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {coverage ? ((coverage.pages.crawled / coverage.pages.total) * 100).toFixed(1) : 0}%
            </span>
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Indexed Pages</span>
            <span className="text-3xl font-bold text-blue-600 dark:text-blue-400">{coverage?.pages.indexed || 0}</span>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {coverage ? ((coverage.pages.indexed / coverage.pages.total) * 100).toFixed(1) : 0}%
            </span>
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Overall Coverage</span>
            <span className="text-3xl font-bold text-purple-600 dark:text-purple-400">
              {coverage?.pages.coverage_percentage.toFixed(1) || 0}%
            </span>
          </div>
        </div>
      </Card>

      {/* Page Status and Content Type Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card title="Page Status Distribution">
          <PieChart
            data={pageStatusData}
            height={300}
          />
        </Card>

        <Card title="Content Type Distribution">
          <PieChart
            data={contentTypeData}
            height={300}
          />
        </Card>
      </div>

      {/* Coverage by Section */}
      <Card title="Coverage by Website Section">
        {isLoading.content[websiteId] ? (
          <div className="flex items-center justify-center h-64">
            <div className="loader"></div>
          </div>
        ) : coverage?.by_section ? (
          <BarChart
            data={coverage.by_section}
            xKey="section"
            bars={[
              { key: 'coverage', name: 'Coverage %', color: '#60A5FA' }
            ]}
            height={300}
          />
        ) : (
          <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
            No data available
          </div>
        )}
      </Card>

      {/* Section Details */}
      {coverage?.by_section && coverage.by_section.length > 0 && (
        <Card title="Section Details" className="mt-6">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Section
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Pages
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Coverage
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-800 dark:divide-gray-700">
                {coverage.by_section.map((section, idx) => (
                  <tr key={idx}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <FolderOpen className="h-5 w-5 text-gray-500 dark:text-gray-400 mr-2" />
                        {section.section}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {section.pages}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-24 bg-gray-200 rounded-full h-2.5 dark:bg-gray-700 mr-2">
                          <div
                            className="bg-blue-600 h-2.5 rounded-full dark:bg-blue-500"
                            style={{ width: `${section.coverage}%` }}
                          ></div>
                        </div>
                        <span>{section.coverage}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Button variant="outline" size="sm">
                        View Pages
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
};

export default ContentCoverageDetails;