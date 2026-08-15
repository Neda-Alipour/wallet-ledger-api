/**
 * Utility functions for currency and date formatting.
 */

// Format numbers into currency strings (e.g. $4,250.00, €1,840.00)
export function formatCurrency(amount, currency = 'USD') {
  const numericAmount = Number(amount) || 0;
  
  try {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency.toUpperCase(),
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(numericAmount);
  } catch (err) {
    // Fallback if currency code is custom/unsupported
    return `${currency.toUpperCase()} ${numericAmount.toFixed(2)}`;
  }
}

// Format API timestamps into human-readable strings (e.g., "Aug 15, 2026, 10:42 PM")
export function formatDate(dateString) {
  if (!dateString) return 'N/A';
  
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return dateString;

  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  }).format(date);
}

// Shorten long UUID strings for display (e.g. "a1b2c3d4...ef56")
export function truncateId(id, length = 8) {
  if (!id) return '';
  if (id.length <= length * 2) return id;
  return `${id.substring(0, length)}...${id.substring(id.length - 4)}`;
}
