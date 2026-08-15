import React from 'react';

export default function Loading({ message = 'Loading...' }) {
  return (
    <div className="state-container">
      <div className="spinner"></div>
      <p className="state-title">{message}</p>
    </div>
  );
}
