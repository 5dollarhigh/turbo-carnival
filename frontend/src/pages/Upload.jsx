import React, { useState, useRef } from 'react';
import { Camera, Upload as UploadIcon, Mail, Check, AlertCircle, X } from 'lucide-react';
import { uploadScannedReceipt, uploadEmailReceipt } from '../services/api';

const Upload = () => {
  const [activeTab, setActiveTab] = useState('scan'); // 'scan' or 'email'
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [uploadedReceipt, setUploadedReceipt] = useState(null);
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);

  const handleFileUpload = async (file, type) => {
    if (!file) return;

    // Validate file type
    if (type === 'scan' && !file.type.startsWith('image/')) {
      setUploadStatus({ type: 'error', message: 'Please upload an image file' });
      return;
    }

    if (type === 'email' && !file.name.endsWith('.eml')) {
      setUploadStatus({ type: 'error', message: 'Please upload a .eml file' });
      return;
    }

    try {
      setUploading(true);
      setUploadStatus(null);

      const uploadFn = type === 'scan' ? uploadScannedReceipt : uploadEmailReceipt;
      const result = await uploadFn(file);

      setUploadStatus({
        type: 'success',
        message: result.message || 'Receipt uploaded successfully!',
      });
      setUploadedReceipt(result.receipt);

      // Clear input
      if (fileInputRef.current) fileInputRef.current.value = '';
      if (cameraInputRef.current) cameraInputRef.current.value = '';
    } catch (error) {
      setUploadStatus({
        type: 'error',
        message: error.response?.data?.error || 'Failed to upload receipt. Please try again.',
      });
    } finally {
      setUploading(false);
    }
  };

  const handleCameraCapture = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFileUpload(file, 'scan');
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFileUpload(file, activeTab);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();

    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileUpload(file, activeTab);
    }
  };

  const dismissStatus = () => {
    setUploadStatus(null);
    setUploadedReceipt(null);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Receipt</h1>
        <p className="text-gray-600">Scan a physical receipt or upload an email receipt</p>
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 mb-6 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('scan')}
          className={`px-6 py-3 font-medium transition-colors border-b-2 ${
            activeTab === 'scan'
              ? 'border-primary text-primary'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          <Camera className="w-5 h-5 inline mr-2" />
          Scan Receipt
        </button>
        <button
          onClick={() => setActiveTab('email')}
          className={`px-6 py-3 font-medium transition-colors border-b-2 ${
            activeTab === 'email'
              ? 'border-primary text-primary'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          <Mail className="w-5 h-5 inline mr-2" />
          Email Receipt
        </button>
      </div>

      {/* Upload Status */}
      {uploadStatus && (
        <div
          className={`mb-6 p-4 rounded-lg flex items-start justify-between ${
            uploadStatus.type === 'success'
              ? 'bg-green-50 text-green-800 border border-green-200'
              : 'bg-red-50 text-red-800 border border-red-200'
          }`}
        >
          <div className="flex items-start">
            {uploadStatus.type === 'success' ? (
              <Check className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" />
            ) : (
              <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" />
            )}
            <div>
              <p className="font-medium">{uploadStatus.message}</p>
              {uploadedReceipt && (
                <div className="mt-2 text-sm">
                  <p>Store: {uploadedReceipt.store_name}</p>
                  <p>Total: ${uploadedReceipt.total_amount.toFixed(2)}</p>
                  <p>Items: {uploadedReceipt.items.length}</p>
                </div>
              )}
            </div>
          </div>
          <button onClick={dismissStatus} className="ml-4">
            <X className="w-5 h-5" />
          </button>
        </div>
      )}

      {/* Upload Area */}
      <div className="bg-white rounded-lg shadow-sm p-8">
        {activeTab === 'scan' ? (
          <div>
            {/* Camera Capture Button (Mobile) */}
            <div className="mb-6">
              <button
                onClick={() => cameraInputRef.current?.click()}
                disabled={uploading}
                className="w-full bg-primary text-white py-4 px-6 rounded-lg font-medium hover:bg-green-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                <Camera className="w-6 h-6 mr-2" />
                {uploading ? 'Processing...' : 'Take Photo'}
              </button>
              <input
                ref={cameraInputRef}
                type="file"
                accept="image/*"
                capture="environment"
                onChange={handleCameraCapture}
                className="hidden"
              />
            </div>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">OR</span>
              </div>
            </div>

            {/* File Upload */}
            <div
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              className="mt-6 border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary transition-colors cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
            >
              <UploadIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-lg font-medium text-gray-700 mb-2">
                Upload Receipt Image
              </p>
              <p className="text-sm text-gray-500 mb-4">
                Drag and drop or click to select
              </p>
              <p className="text-xs text-gray-400">
                Supports: JPG, PNG, HEIC, PDF
              </p>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*,.pdf"
                onChange={handleFileSelect}
                className="hidden"
              />
            </div>

            <div className="mt-6 bg-blue-50 rounded-lg p-4 border border-blue-200">
              <h3 className="font-medium text-blue-900 mb-2">Tips for best results:</h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Ensure good lighting and avoid shadows</li>
                <li>• Keep the receipt flat and fully visible</li>
                <li>• Make sure text is clear and readable</li>
                <li>• Capture the entire receipt including totals</li>
              </ul>
            </div>
          </div>
        ) : (
          <div>
            {/* Email File Upload */}
            <div
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary transition-colors cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
            >
              <Mail className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-lg font-medium text-gray-700 mb-2">
                Upload Email Receipt (.eml)
              </p>
              <p className="text-sm text-gray-500 mb-4">
                Drag and drop or click to select
              </p>
              <p className="text-xs text-gray-400">
                Supports: .eml files only
              </p>
              <input
                ref={fileInputRef}
                type="file"
                accept=".eml"
                onChange={handleFileSelect}
                className="hidden"
              />
            </div>

            <div className="mt-6 bg-amber-50 rounded-lg p-4 border border-amber-200">
              <h3 className="font-medium text-amber-900 mb-2">How to save emails as .eml:</h3>
              <ul className="text-sm text-amber-800 space-y-2">
                <li>
                  <strong>Gmail:</strong> Open email → More (⋮) → Download message
                </li>
                <li>
                  <strong>Outlook:</strong> Open email → File → Save As → Choose .eml format
                </li>
                <li>
                  <strong>Apple Mail:</strong> Select email → File → Save As
                </li>
              </ul>
            </div>
          </div>
        )}

        {/* Uploading Indicator */}
        {uploading && (
          <div className="mt-6 flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mr-3"></div>
            <span className="text-gray-600">Processing receipt...</span>
          </div>
        )}
      </div>

      {/* Recent Uploads */}
      {uploadedReceipt && (
        <div className="mt-8 bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-bold mb-4">Receipt Details</h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Store:</span>
              <span className="font-medium">{uploadedReceipt.store_name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Date:</span>
              <span className="font-medium">
                {new Date(uploadedReceipt.purchase_date).toLocaleDateString()}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Total:</span>
              <span className="font-medium text-primary text-lg">
                ${uploadedReceipt.total_amount.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Tax:</span>
              <span className="font-medium">${uploadedReceipt.tax_amount.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Items:</span>
              <span className="font-medium">{uploadedReceipt.items.length}</span>
            </div>
          </div>

          {uploadedReceipt.items.length > 0 && (
            <div className="mt-6">
              <h3 className="font-semibold mb-3">Items:</h3>
              <div className="max-h-64 overflow-y-auto space-y-2">
                {uploadedReceipt.items.map((item, idx) => (
                  <div
                    key={idx}
                    className="flex justify-between items-center p-2 bg-gray-50 rounded"
                  >
                    <div>
                      <p className="font-medium text-sm">{item.name}</p>
                      <p className="text-xs text-gray-500">
                        {item.quantity}x @ ${item.unit_price.toFixed(2)}
                      </p>
                    </div>
                    <span className="font-semibold">${item.total_price.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="mt-6 flex space-x-3">
            <a
              href="/"
              className="flex-1 bg-primary text-white py-2 px-4 rounded-lg text-center font-medium hover:bg-green-600 transition-colors"
            >
              View Analytics
            </a>
            <button
              onClick={dismissStatus}
              className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-lg font-medium hover:bg-gray-300 transition-colors"
            >
              Upload Another
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Upload;
