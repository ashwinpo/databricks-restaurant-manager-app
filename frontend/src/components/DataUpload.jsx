import React, { useState } from 'react';
import { Upload, FileText, Calendar, TrendingUp, X, CheckCircle, AlertCircle } from 'lucide-react';

const DataUpload = ({ config, onClose }) => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [dragActive, setDragActive] = useState(false);

  // Mock external data sources that restaurants might upload
  const dataSourceOptions = [
    {
      type: 'labor_schedule',
      name: 'Labor Schedule Export',
      description: 'Weekly staff schedules from scheduling software',
      format: '.csv, .xlsx',
      icon: Calendar,
      sampleInsights: ['Optimize shift patterns', 'Identify overstaffing periods', 'Labor cost forecasting']
    },
    {
      type: 'supplier_costs',
      name: 'Supplier Cost Data',
      description: 'Food cost updates from suppliers/commissary',
      format: '.csv, .pdf',
      icon: TrendingUp,
      sampleInsights: ['Food cost variance analysis', 'Menu pricing optimization', 'Supplier comparison']
    },
    {
      type: 'competitor_data',
      name: 'Competitor Pricing',
      description: 'Local competitor menu prices and promotions',
      format: '.csv, .txt',
      icon: FileText,
      sampleInsights: ['Pricing strategy recommendations', 'Promotion timing', 'Market positioning']
    },
    {
      type: 'customer_feedback',
      name: 'Customer Feedback',
      description: 'Reviews, surveys, and feedback data',
      format: '.csv, .json',
      icon: FileText,
      sampleInsights: ['Menu item performance', 'Service improvement areas', 'Customer satisfaction trends']
    }
  ];

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFiles = (files) => {
    Array.from(files).forEach(file => {
      const newFile = {
        id: Date.now() + Math.random(),
        name: file.name,
        size: file.size,
        type: file.type,
        uploadTime: new Date(),
        status: 'processing',
        insights: []
      };
      
      setUploadedFiles(prev => [...prev, newFile]);
      
      // Simulate processing
      setTimeout(() => {
        setUploadedFiles(prev => prev.map(f => 
          f.id === newFile.id 
            ? { 
                ...f, 
                status: 'completed',
                insights: [
                  'Generated 3 new actionable insights',
                  'Updated labor cost predictions',
                  'Enhanced menu optimization recommendations'
                ]
              }
            : f
        ));
      }, 2000);
    });
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  return (
    <div className="data-upload-modal">
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-content large" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <h3>
              <Upload size={24} />
              External Data Integration
            </h3>
            <button className="modal-close" onClick={onClose}>
              <X size={20} />
            </button>
          </div>
          
          <div className="modal-body">
            <div className="upload-intro">
              <p>Upload external data to enhance your restaurant insights. Supported data sources:</p>
            </div>

            {/* Data Source Types */}
            <div className="data-source-grid">
              {dataSourceOptions.map((source) => {
                const IconComponent = source.icon;
                return (
                  <div key={source.type} className="data-source-card">
                    <div className="source-header">
                      <IconComponent size={20} />
                      <h4>{source.name}</h4>
                    </div>
                    <p className="source-description">{source.description}</p>
                    <div className="source-format">
                      <span className="format-label">Formats:</span>
                      <span className="format-types">{source.format}</span>
                    </div>
                    <div className="source-insights">
                      <span className="insights-label">Sample Insights:</span>
                      <ul>
                        {source.sampleInsights.map((insight, idx) => (
                          <li key={idx}>{insight}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* File Upload Area */}
            <div 
              className={`upload-area ${dragActive ? 'drag-active' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <Upload size={48} />
              <h4>Drag & drop files here, or click to browse</h4>
              <p>Supports CSV, Excel, PDF, and text files up to 10MB</p>
              <input
                type="file"
                multiple
                accept=".csv,.xlsx,.xls,.pdf,.txt,.json"
                onChange={(e) => handleFiles(e.target.files)}
                style={{ display: 'none' }}
                id="file-upload"
              />
              <label htmlFor="file-upload" className="upload-button">
                Choose Files
              </label>
            </div>

            {/* Uploaded Files List */}
            {uploadedFiles.length > 0 && (
              <div className="uploaded-files">
                <h4>Uploaded Files</h4>
                {uploadedFiles.map((file) => (
                  <div key={file.id} className="file-item">
                    <div className="file-info">
                      <div className="file-details">
                        <span className="file-name">{file.name}</span>
                        <span className="file-meta">
                          {formatFileSize(file.size)} • {file.uploadTime.toLocaleTimeString()}
                        </span>
                      </div>
                      <div className="file-status">
                        {file.status === 'processing' && (
                          <div className="status processing">
                            <div className="spinner"></div>
                            Processing...
                          </div>
                        )}
                        {file.status === 'completed' && (
                          <div className="status completed">
                            <CheckCircle size={16} />
                            Processed
                          </div>
                        )}
                        {file.status === 'error' && (
                          <div className="status error">
                            <AlertCircle size={16} />
                            Error
                          </div>
                        )}
                      </div>
                      <button 
                        className="remove-file"
                        onClick={() => removeFile(file.id)}
                      >
                        <X size={16} />
                      </button>
                    </div>
                    
                    {file.insights.length > 0 && (
                      <div className="file-insights">
                        <h5>Generated Insights:</h5>
                        <ul>
                          {file.insights.map((insight, idx) => (
                            <li key={idx}>{insight}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="modal-footer">
            <button className="modal-btn primary" onClick={onClose}>
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataUpload;
