import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [content, setContent] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [newUrl, setNewUrl] = useState('');
  const [newTags, setNewTags] = useState('');
  const [newCategory, setNewCategory] = useState('General');
  const [categories, setCategories] = useState([]);
  const [tags, setTags] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [showAddForm, setShowAddForm] = useState(false);

  // Predefined categories with colors
  const categoryColors = {
    'General': 'bg-gray-100 text-gray-800 border-gray-300',
    'Entertainment': 'bg-pink-100 text-pink-800 border-pink-300',
    'Education': 'bg-blue-100 text-blue-800 border-blue-300',
    'Cooking': 'bg-green-100 text-green-800 border-green-300',
    'DIY': 'bg-yellow-100 text-yellow-800 border-yellow-300',
    'Funny': 'bg-purple-100 text-purple-800 border-purple-300',
    'Inspirational': 'bg-orange-100 text-orange-800 border-orange-300',
    'News': 'bg-red-100 text-red-800 border-red-300',
    'Health': 'bg-teal-100 text-teal-800 border-teal-300'
  };

  useEffect(() => {
    loadContent();
    loadCategories();
    loadTags();
  }, []);

  const loadContent = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/content`);
      const data = await response.json();
      setContent(data);
    } catch (error) {
      console.error('Error loading content:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/categories`);
      const data = await response.json();
      setCategories(data);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  const loadTags = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/tags`);
      const data = await response.json();
      setTags(data);
    } catch (error) {
      console.error('Error loading tags:', error);
    }
  };

  const handleAddContent = async (e) => {
    e.preventDefault();
    if (!newUrl.trim()) return;

    try {
      setLoading(true);
      const tagsArray = newTags.split(',').map(tag => tag.trim()).filter(tag => tag);
      
      const response = await fetch(`${API_BASE_URL}/api/content`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: newUrl.trim(),
          tags: tagsArray,
          category: newCategory
        }),
      });

      if (response.ok) {
        setNewUrl('');
        setNewTags('');
        setNewCategory('General');
        setShowAddForm(false);
        await loadContent();
        await loadCategories();
        await loadTags();
      }
    } catch (error) {
      console.error('Error adding content:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      loadContent();
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery.trim()
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setContent(data);
      }
    } catch (error) {
      console.error('Error searching:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (contentId) => {
    if (!window.confirm('Are you sure you want to delete this item?')) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/content/${contentId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        await loadContent();
        await loadCategories();  
        await loadTags();
      }
    } catch (error) {
      console.error('Error deleting content:', error);
    }
  };

  const filteredContent = selectedCategory === 'all' 
    ? content 
    : content.filter(item => item.category === selectedCategory);

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getCategoryColor = (category) => {
    return categoryColors[category] || categoryColors['General'];
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            📱 My Saved Content
          </h1>
          <p className="text-gray-600 text-lg">
            Organize your saved Facebook content with ease
          </p>
        </div>

        {/* Add Content Button */}
        <div className="text-center mb-6">
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg shadow-md transition-colors duration-200 text-lg"
          >
            ➕ Add New Content
          </button>
        </div>

        {/* Add Content Form */}
        {showAddForm && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8 border-2 border-blue-200">
            <h2 className="text-2xl font-semibold mb-4 text-gray-800">Add New Content</h2>
            <form onSubmit={handleAddContent} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Facebook URL *
                </label>
                <input
                  type="url"
                  value={newUrl}
                  onChange={(e) => setNewUrl(e.target.value)}
                  placeholder="Paste your Facebook link here..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                  required
                />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Category
                  </label>
                  <select
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                  >
                    {Object.keys(categoryColors).map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tags (comma separated)
                  </label>
                  <input
                    type="text"
                    value={newTags}
                    onChange={(e) => setNewTags(e.target.value)}
                    placeholder="funny, cooking, tutorial..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                  />
                </div>
              </div>
              
              <div className="flex gap-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg disabled:opacity-50 transition-colors duration-200"
                >
                  {loading ? '⏳ Saving...' : '💾 Save Content'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Search Bar */}
        <div className="bg-white rounded-xl shadow-md p-4 mb-6">
          <form onSubmit={handleSearch} className="flex gap-4">
            <div className="flex-1">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="🔍 Search your saved content..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg disabled:opacity-50 transition-colors duration-200"
            >
              Search
            </button>
            {searchQuery && (
              <button
                type="button"
                onClick={() => {
                  setSearchQuery('');
                  loadContent();
                }}
                className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-3 px-4 rounded-lg transition-colors duration-200"
              >
                Clear
              </button>
            )}
          </form>
        </div>

        {/* Category Filter */}
        <div className="bg-white rounded-xl shadow-md p-4 mb-6">
          <h3 className="text-lg font-semibold mb-3 text-gray-800">Filter by Category:</h3>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedCategory('all')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors duration-200 ${
                selectedCategory === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              All ({content.length})
            </button>
            {categories.map(cat => (
              <button
                key={cat.name}
                onClick={() => setSelectedCategory(cat.name)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors duration-200 ${
                  selectedCategory === cat.name
                    ? 'bg-blue-600 text-white'
                    : `${getCategoryColor(cat.name)} hover:opacity-80`
                }`}
              >
                {cat.name} ({cat.count})
              </button>
            ))}
          </div>
        </div>

        {/* Content Grid */}
        {loading && (
          <div className="text-center py-8">
            <div className="text-2xl">⏳ Loading...</div>
          </div>
        )}

        {!loading && filteredContent.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📱</div>
            <h3 className="text-xl font-semibold text-gray-600 mb-2">
              {content.length === 0 ? 'No saved content yet' : 'No content matches your filter'}
            </h3>
            <p className="text-gray-500">
              {content.length === 0 
                ? 'Add your first Facebook link to get started!' 
                : 'Try a different category or search term'
              }
            </p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredContent.map((item) => (
            <div key={item.id} className="bg-white rounded-xl shadow-lg overflow-hidden border-2 border-gray-100 hover:shadow-xl transition-shadow duration-300">
              {/* Thumbnail */}
              {item.thumbnail && (
                <div className="h-48 bg-gray-200 overflow-hidden">
                  <img
                    src={item.thumbnail}
                    alt={item.title}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                </div>
              )}
              
              {/* Content */}
              <div className="p-4">
                <h3 className="font-bold text-lg mb-2 text-gray-800 line-clamp-2">
                  {item.title}
                </h3>
                
                <p className="text-gray-600 text-sm mb-3 line-clamp-3">
                  {item.description}
                </p>
                
                {/* Category */}
                <div className="mb-3">
                  <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium border ${getCategoryColor(item.category)}`}>
                    {item.category}
                  </span>
                </div>
                
                {/* Tags */}
                {item.tags && item.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {item.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}
                
                {/* Date */}
                <p className="text-xs text-gray-500 mb-4">
                  Saved on {formatDate(item.date_saved)}
                </p>
                
                {/* Actions */}
                <div className="flex gap-2">
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-center py-2 px-4 rounded-lg font-medium transition-colors duration-200"
                  >
                    🔗 View
                  </a>
                  <button
                    onClick={() => handleDelete(item.id)}
                    className="bg-red-500 hover:bg-red-600 text-white py-2 px-4 rounded-lg font-medium transition-colors duration-200"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;