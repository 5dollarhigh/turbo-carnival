import React, { useState, useEffect } from 'react';
import { getReceipts, deleteReceipt } from '../services/api';
import { Search, Trash2, ChevronDown, ChevronUp, Filter, X } from 'lucide-react';

const Receipts = () => {
  const [receipts, setReceipts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedReceipt, setExpandedReceipt] = useState(null);
  const [filterStore, setFilterStore] = useState('');
  const [stores, setStores] = useState([]);
  const [deleting, setDeleting] = useState(null);

  useEffect(() => {
    loadReceipts();
  }, []);

  const loadReceipts = async () => {
    try {
      setLoading(true);
      const data = await getReceipts({ limit: 500 });
      setReceipts(data.receipts);

      // Extract unique stores
      const uniqueStores = [...new Set(data.receipts.map(r => r.store_name))];
      setStores(uniqueStores);
    } catch (error) {
      console.error('Error loading receipts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this receipt?')) {
      return;
    }

    try {
      setDeleting(id);
      await deleteReceipt(id);
      setReceipts(receipts.filter(r => r.id !== id));
      if (expandedReceipt === id) {
        setExpandedReceipt(null);
      }
    } catch (error) {
      console.error('Error deleting receipt:', error);
      alert('Failed to delete receipt');
    } finally {
      setDeleting(null);
    }
  };

  const toggleExpand = (id) => {
    setExpandedReceipt(expandedReceipt === id ? null : id);
  };

  const filteredReceipts = receipts.filter(receipt => {
    const matchesSearch = searchTerm === '' ||
      receipt.store_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      receipt.items.some(item => item.name.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesStore = filterStore === '' || receipt.store_name === filterStore;

    return matchesSearch && matchesStore;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading receipts...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Receipts</h1>
        <p className="text-gray-600">View and manage all your uploaded receipts</p>
      </div>

      {/* Search and Filter */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search by store or item..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          {/* Store Filter */}
          <div className="relative sm:w-64">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <select
              value={filterStore}
              onChange={(e) => setFilterStore(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary appearance-none bg-white"
            >
              <option value="">All Stores</option>
              {stores.map(store => (
                <option key={store} value={store}>{store}</option>
              ))}
            </select>
          </div>
        </div>

        {(searchTerm || filterStore) && (
          <div className="mt-3 flex items-center justify-between">
            <p className="text-sm text-gray-600">
              Showing {filteredReceipts.length} of {receipts.length} receipts
            </p>
            <button
              onClick={() => {
                setSearchTerm('');
                setFilterStore('');
              }}
              className="text-sm text-primary hover:text-green-700 flex items-center"
            >
              <X className="w-4 h-4 mr-1" />
              Clear filters
            </button>
          </div>
        )}
      </div>

      {/* Receipts List */}
      {filteredReceipts.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow-sm">
          <p className="text-gray-600 text-lg">
            {receipts.length === 0
              ? 'No receipts yet. Upload your first receipt to get started!'
              : 'No receipts match your search criteria.'}
          </p>
          {receipts.length === 0 && (
            <a
              href="/upload"
              className="inline-block mt-4 bg-primary text-white px-6 py-3 rounded-lg font-medium hover:bg-green-600 transition-colors"
            >
              Upload Receipt
            </a>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {filteredReceipts.map(receipt => (
            <div key={receipt.id} className="bg-white rounded-lg shadow-sm overflow-hidden">
              {/* Receipt Summary */}
              <div
                className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                onClick={() => toggleExpand(receipt.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <h3 className="text-lg font-bold text-gray-900 mr-3">
                        {receipt.store_name}
                      </h3>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        receipt.source_type === 'scan'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-purple-100 text-purple-800'
                      }`}>
                        {receipt.source_type === 'scan' ? '📸 Scanned' : '📧 Email'}
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                      <span>
                        {new Date(receipt.purchase_date).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                        })}
                      </span>
                      <span>•</span>
                      <span>{receipt.items.length} items</span>
                      <span>•</span>
                      <span className="font-semibold text-primary">
                        ${receipt.total_amount.toFixed(2)}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 ml-4">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(receipt.id);
                      }}
                      disabled={deleting === receipt.id}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                      title="Delete receipt"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                    {expandedReceipt === receipt.id ? (
                      <ChevronUp className="w-6 h-6 text-gray-400" />
                    ) : (
                      <ChevronDown className="w-6 h-6 text-gray-400" />
                    )}
                  </div>
                </div>
              </div>

              {/* Expanded Details */}
              {expandedReceipt === receipt.id && (
                <div className="border-t border-gray-200 bg-gray-50 p-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-600 mb-1">Subtotal</p>
                      <p className="text-lg font-semibold">
                        ${(receipt.total_amount - receipt.tax_amount).toFixed(2)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 mb-1">Tax</p>
                      <p className="text-lg font-semibold">${receipt.tax_amount.toFixed(2)}</p>
                    </div>
                  </div>

                  {/* Items List */}
                  <div className="bg-white rounded-lg p-4">
                    <h4 className="font-semibold mb-3">Items</h4>
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                      {receipt.items.map((item, idx) => (
                        <div
                          key={idx}
                          className="flex justify-between items-start p-2 hover:bg-gray-50 rounded"
                        >
                          <div className="flex-1">
                            <p className="font-medium text-sm">{item.name}</p>
                            <div className="flex items-center gap-3 mt-1">
                              <span className="text-xs text-gray-500">
                                Qty: {item.quantity}
                              </span>
                              <span className="text-xs text-gray-500">
                                @ ${item.unit_price.toFixed(2)}
                              </span>
                              {item.category && (
                                <span className="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">
                                  {item.category}
                                </span>
                              )}
                            </div>
                          </div>
                          <span className="font-semibold text-gray-900 ml-4">
                            ${item.total_price.toFixed(2)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Receipts;
