import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';
import {
  getMonthlyTrends,
  getCategoryBreakdown,
  getTopItems,
  getStoreComparison,
  getSummary,
  getWasteInsights,
  getShoppingFrequency
} from '../services/api';
import { DollarSign, ShoppingCart, TrendingUp, Calendar, Package, AlertCircle } from 'lucide-react';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [monthlyTrends, setMonthlyTrends] = useState(null);
  const [categories, setCategories] = useState(null);
  const [topItems, setTopItems] = useState([]);
  const [stores, setStores] = useState(null);
  const [frequency, setFrequency] = useState(null);
  const [wasteInsights, setWasteInsights] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [
        summaryData,
        trendsData,
        categoriesData,
        itemsData,
        storesData,
        frequencyData,
        wasteData
      ] = await Promise.all([
        getSummary(),
        getMonthlyTrends(12),
        getCategoryBreakdown(),
        getTopItems(20),
        getStoreComparison(),
        getShoppingFrequency(),
        getWasteInsights()
      ]);

      setSummary(summaryData);
      setMonthlyTrends(trendsData);
      setCategories(categoriesData);
      setTopItems(itemsData.items);
      setStores(storesData);
      setFrequency(frequencyData);
      setWasteInsights(wasteData);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your analytics...</p>
        </div>
      </div>
    );
  }

  if (!summary || summary.total_receipts === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center max-w-md mx-auto p-6">
          <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-700 mb-2">No Data Yet</h2>
          <p className="text-gray-600 mb-6">
            Start by uploading your first receipt to see your spending analytics!
          </p>
          <a
            href="/upload"
            className="inline-block bg-primary text-white px-6 py-3 rounded-lg font-medium hover:bg-green-600 transition-colors"
          >
            Upload Receipt
          </a>
        </div>
      </div>
    );
  }

  // Prepare monthly trends chart data
  const monthlyChartData = {
    labels: monthlyTrends?.trends?.map(t => t.label) || [],
    datasets: [
      {
        label: 'Total Spent',
        data: monthlyTrends?.trends?.map(t => t.total_spent) || [],
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  // Prepare category breakdown chart
  const categoryChartData = {
    labels: categories?.categories?.map(c => c.category) || [],
    datasets: [
      {
        data: categories?.categories?.map(c => c.total_spent) || [],
        backgroundColor: categories?.categories?.map(c => c.color) || [],
        borderWidth: 2,
        borderColor: '#fff',
      },
    ],
  };

  // Prepare store comparison chart
  const storeChartData = {
    labels: stores?.stores?.map(s => s.store_name) || [],
    datasets: [
      {
        label: 'Total Spent',
        data: stores?.stores?.map(s => s.total_spent) || [],
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
      },
    },
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Grocery Analytics</h1>
        <p className="text-gray-600">Comprehensive overview of your spending patterns</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          icon={DollarSign}
          label="Total Spent"
          value={`$${summary.total_spent.toFixed(2)}`}
          color="text-green-600"
          bgColor="bg-green-100"
        />
        <StatCard
          icon={ShoppingCart}
          label="Total Receipts"
          value={summary.total_receipts}
          color="text-blue-600"
          bgColor="bg-blue-100"
        />
        <StatCard
          icon={TrendingUp}
          label="Avg Receipt"
          value={`$${summary.average_receipt.toFixed(2)}`}
          color="text-purple-600"
          bgColor="bg-purple-100"
        />
        <StatCard
          icon={Package}
          label="Total Items"
          value={summary.total_items}
          color="text-orange-600"
          bgColor="bg-orange-100"
        />
      </div>

      {/* Shopping Frequency */}
      {frequency && (
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="flex items-center mb-4">
            <Calendar className="w-6 h-6 text-primary mr-2" />
            <h2 className="text-xl font-bold">Shopping Frequency</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <p className="text-gray-600 text-sm">Pattern</p>
              <p className="text-2xl font-bold text-gray-900">{frequency.shopping_frequency}</p>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Average Days Between Trips</p>
              <p className="text-2xl font-bold text-gray-900">{frequency.average_days_between_trips} days</p>
            </div>
          </div>
        </div>
      )}

      {/* Monthly Spending Trends */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
        <h2 className="text-xl font-bold mb-4">Monthly Spending Trends</h2>
        <div className="h-64">
          <Line data={monthlyChartData} options={chartOptions} />
        </div>
        {monthlyTrends && (
          <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-600">Total Period Spend</p>
              <p className="text-lg font-bold text-primary">
                ${monthlyTrends.total_period_spend.toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-gray-600">Average Monthly</p>
              <p className="text-lg font-bold text-primary">
                ${monthlyTrends.average_monthly_spend.toFixed(2)}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Category Breakdown and Store Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Category Breakdown */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-bold mb-4">Spending by Category</h2>
          <div className="h-64 mb-4">
            <Doughnut data={categoryChartData} options={chartOptions} />
          </div>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {categories?.categories?.slice(0, 5).map((cat, idx) => (
              <div key={idx} className="flex justify-between items-center text-sm">
                <div className="flex items-center">
                  <div
                    className="w-3 h-3 rounded-full mr-2"
                    style={{ backgroundColor: cat.color }}
                  ></div>
                  <span className="text-gray-700">{cat.category}</span>
                </div>
                <span className="font-semibold">${cat.total_spent.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Store Comparison */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-bold mb-4">Store Comparison</h2>
          <div className="h-64 mb-4">
            <Bar data={storeChartData} options={chartOptions} />
          </div>
          <div className="space-y-2">
            {stores?.stores?.map((store, idx) => (
              <div key={idx} className="flex justify-between items-center text-sm">
                <span className="text-gray-700">{store.store_name}</span>
                <div className="text-right">
                  <span className="font-semibold">${store.total_spent.toFixed(2)}</span>
                  <span className="text-gray-500 ml-2">({store.visit_count} visits)</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Top Expensive Items */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
        <h2 className="text-xl font-bold mb-4">Top Expensive Items</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Item</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Total Spent</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Purchases</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Avg Price</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {topItems.slice(0, 10).map((item, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">{item.name}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{item.category}</td>
                  <td className="px-4 py-3 text-sm text-right font-semibold text-green-600">
                    ${item.total_spent.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-sm text-right text-gray-600">{item.purchase_count}x</td>
                  <td className="px-4 py-3 text-sm text-right text-gray-600">
                    ${item.average_price.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Waste Insights */}
      {wasteInsights?.insights && wasteInsights.insights.length > 0 && (
        <div className="bg-amber-50 rounded-lg shadow-sm p-6 mb-8 border border-amber-200">
          <div className="flex items-center mb-4">
            <AlertCircle className="w-6 h-6 text-amber-600 mr-2" />
            <h2 className="text-xl font-bold text-amber-900">Money-Saving Insights</h2>
          </div>
          <div className="space-y-3">
            {wasteInsights.insights.slice(0, 5).map((insight, idx) => (
              <div key={idx} className="bg-white rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold text-gray-900">{insight.item_name}</h3>
                  <span className="text-sm font-bold text-amber-600">
                    ${insight.total_spent.toFixed(2)} spent
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-1">
                  Purchased {insight.purchase_frequency} times (avg qty: {insight.average_quantity})
                </p>
                <p className="text-sm text-amber-700 font-medium">
                  💡 {insight.suggestion}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Most Expensive Purchase */}
      {summary.most_expensive_item && (
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-bold mb-4 text-purple-900">Your Most Expensive Item</h2>
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center">
            <div>
              <p className="text-2xl font-bold text-purple-900 mb-2">
                {summary.most_expensive_item.name}
              </p>
              <p className="text-gray-600">
                {summary.most_expensive_item.store} • {new Date(summary.most_expensive_item.date).toLocaleDateString()}
              </p>
            </div>
            <div className="mt-4 sm:mt-0">
              <p className="text-4xl font-bold text-purple-600">
                ${summary.most_expensive_item.price.toFixed(2)}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// StatCard Component
const StatCard = ({ icon: Icon, label, value, color, bgColor }) => (
  <div className="bg-white rounded-lg shadow-sm p-6">
    <div className="flex items-center">
      <div className={`${bgColor} p-3 rounded-lg mr-4`}>
        <Icon className={`w-6 h-6 ${color}`} />
      </div>
      <div>
        <p className="text-sm text-gray-600 mb-1">{label}</p>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
      </div>
    </div>
  </div>
);

export default Dashboard;
