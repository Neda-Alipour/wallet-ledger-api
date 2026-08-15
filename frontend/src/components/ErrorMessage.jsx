import React from 'react';

export default function ErrorMessage({ message, onRetry }) {
  if (!message) return null;

  return (
    <div className="alert-error">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem' }}>
        <span>{message}</span>
        {onRetry && (
          <button 
            onClick={onRetry} 
            className="btn-secondary" 
            style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}
          >
            Retry
          </button>
        )}
      </div>
    </div>
  );
}
