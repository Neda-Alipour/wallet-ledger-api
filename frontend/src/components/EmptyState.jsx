import React from 'react';

export default function EmptyState({ title = 'No data available', description = 'There are no items to display right now.' }) {
  return (
    <div className="state-container">
      <h3 className="state-title">{title}</h3>
      <p className="state-desc">{description}</p>
    </div>
  );
}
