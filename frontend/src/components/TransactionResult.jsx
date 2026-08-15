import React from 'react';
import { formatCurrency, formatDate, truncateId } from '../utils/formatters';
import { CheckIcon } from './Icons';

export default function TransactionResult({ 
  transaction, 
  type = 'deposit', // 'deposit' | 'withdrawal' | 'transfer'
  currency = 'USD',
  onDone, 
  onViewTransaction 
}) {
  if (!transaction) return null;

  const rawAmount = Number(transaction.amount) || 0;
  const isPositive = type === 'deposit' || rawAmount > 0;
  const formattedAmount = formatCurrency(Math.abs(rawAmount), currency);

  // Title formatting
  let title = 'Transaction completed';
  if (type === 'deposit') title = 'Deposit successful';
  else if (type === 'withdrawal') title = 'Withdrawal successful';
  else if (type === 'transfer') title = 'Transfer successful';

  return (
    <div className="receipt-container">
      <div className="receipt-status-badge" style={{ backgroundColor: 'var(--color-success-bg)', color: 'var(--color-success)', border: '1px solid var(--color-success-border)' }}>
        <CheckIcon />
        <span>{title}</span>
      </div>

      <div className="receipt-amount-display" style={{ color: isPositive ? 'var(--color-success)' : 'var(--text-main)' }}>
        {isPositive ? '+' : '-'}{formattedAmount}
      </div>

      <div className="receipt-details-table">
        <div className="receipt-details-row">
          <span className="receipt-label">Operation</span>
          <span className="receipt-value" style={{ textTransform: 'capitalize' }}>{type}</span>
        </div>

        <div className="receipt-details-row">
          <span className="receipt-label">Source Wallet</span>
          <span className="receipt-value" style={{ fontFamily: 'monospace' }}>
            {truncateId(transaction.wallet_id || transaction.source_wallet_id, 8)}
          </span>
        </div>

        {transaction.destination_wallet_id && (
          <div className="receipt-details-row">
            <span className="receipt-label">Destination Wallet</span>
            <span className="receipt-value" style={{ fontFamily: 'monospace' }}>
              {truncateId(transaction.destination_wallet_id, 8)}
            </span>
          </div>
        )}

        {transaction.reference && (
          <div className="receipt-details-row">
            <span className="receipt-label">Reference</span>
            <span className="receipt-value">{transaction.reference}</span>
          </div>
        )}

        <div className="receipt-details-row">
          <span className="receipt-label">Date & Time</span>
          <span className="receipt-value">{formatDate(transaction.created_at || new Date())}</span>
        </div>

        <div className="receipt-details-row">
          <span className="receipt-label">Transaction ID</span>
          <span className="receipt-value" style={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
            {truncateId(transaction.transaction_id || transaction.id, 8)}
          </span>
        </div>

        <div className="receipt-details-row">
          <span className="receipt-label">Status</span>
          <span className="receipt-value" style={{ color: 'var(--color-success)', fontWeight: 600 }}>
            {transaction.status ? transaction.status.charAt(0).toUpperCase() + transaction.status.slice(1) : 'Completed'}
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
        {onDone && (
          <button className="btn-primary" onClick={onDone} style={{ minWidth: '110px' }}>
            Done
          </button>
        )}
        {onViewTransaction && (
          <button className="btn-secondary" onClick={onViewTransaction} style={{ minWidth: '130px' }}>
            View transactions
          </button>
        )}
      </div>
    </div>
  );
}
