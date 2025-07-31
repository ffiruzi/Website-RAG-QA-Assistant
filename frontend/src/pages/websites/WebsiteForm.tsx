import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/Card';
import Button from '../../components/Button';
import { useNotification } from '../../hooks/useNotification';
import { useWebsites } from '../../hooks/useWebsites';

const WebsiteForm: React.FC = () => {
  const navigate = useNavigate();
  const { addToast } = useNotification();
  const { createWebsite } = useWebsites();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    url: '',
    name: '',
    description: '',
    is_active: true,
    sitemap_url: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;

    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData(prev => ({ ...prev, [name]: checked }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // Convert form data to API format
      const websiteData = {
        url: formData.url,
        name: formData.name,
        description: formData.description || undefined,
        is_active: formData.is_active,
        sitemap_url: formData.sitemap_url || undefined,
      };

      // Create website using context
      await createWebsite(websiteData);

      // Show success notification
      addToast({
        type: 'success',
        title: 'Website Added',
        message: `${formData.name} has been successfully added.`,
      });

      // Redirect to websites list
      navigate('/websites');
    } catch (error) {
      console.error('Error creating website:', error);

      // Show error notification
      addToast({
        type: 'error',
        title: 'Error',
        message: 'Failed to create website. Please try again.',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <div className="flex items-center mb-6">
        <Button
          variant="outline"
          onClick={() => navigate('/websites')}
          className="mr-4"
        >
          Back
        </Button>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Add Website
        </h1>
      </div>

      <Card>
        <form onSubmit={handleSubmit}>
          <div className="space-y-6">
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Website URL *
                </label>
                <input
                  type="url"
                  name="url"
                  value={formData.url}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  placeholder="https://example.com"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Website Name *
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  placeholder="Example Website"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Description
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                placeholder="Describe the website's purpose or content"
              ></textarea>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Sitemap URL (Optional)
              </label>
              <input
                type="url"
                name="sitemap_url"
                value={formData.sitemap_url}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                placeholder="https://example.com/sitemap.xml"
              />
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                If provided, the sitemap will be used to discover pages for crawling
              </p>
            </div>

            <div className="flex items-center">
              <input
                id="is_active"
                name="is_active"
                type="checkbox"
                checked={formData.is_active}
                onChange={handleChange}
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800"
              />
              <label
                htmlFor="is_active"
                className="ml-2 block text-sm text-gray-700 dark:text-gray-300"
              >
                Active
              </label>
            </div>

            <div className="flex justify-end space-x-3">
              <Button
                variant="outline"
                onClick={() => navigate('/websites')}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                isLoading={isSubmitting}
                disabled={isSubmitting}
              >
                Create Website
              </Button>
            </div>
          </div>
        </form>
      </Card>
    </div>
  );
};

export default WebsiteForm;