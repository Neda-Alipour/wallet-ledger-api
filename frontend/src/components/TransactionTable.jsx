import React from 'react';
import { formatCurrency, formatDate, truncateId } from '../utils/formatters';

export default function TransactionTable({ 
  transactions = [], 
  wallets = [], 
  onSelectTransaction 
}) {
  if (!transactions.length) {
    return null;
  }

  const walletCurrencyMap = {};
  wallets.forEach((w) => {
    walletCurrencyMap[w.id] = w.currency;
  });

  return (
    <div className="table-container">
      <table className="data-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Type</th>
            <th>Wallet / Currency</th>
            <th>Amount</th>
            <th>Reference</th>
            <th>Status</th>
            <th style={{ textAlign: 'right' }}>Details</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((tx) => {
            const isPositive = tx.type === 'deposit' || Number(tx.amount) > 0;
            const currency = tx.currency || walletCurrencyMap[tx.wallet_id] || 'USD';
            const rawAmount = Number(tx.amount) || 0;

            return (
              <tr 
                key={tx.transaction_id || tx.id}
                onClick={() => onSelectTransaction && onSelectTransaction(tx)}
                className="clickable-row"
              >
                <td data-label="Date" style={{ whiteSpace: 'nowrap' }}>
                  {formatDate(tx.created_at)}
                </td>
                <td data-label="Type" style={{ textTransform: 'capitalize', fontWeight: 500 }}>
                  {tx.type}
                </td>
                <td data-label="Wallet / Currency">
                  <span className="currency-pill">{currency}</span>
                  <span title={tx.wallet_id} style={{ fontFamily: 'monospace', fontSize: '0.75rem', color: 'var(--text-muted)', marginLeft: '0.4rem' }}>
                    ({truncateId(tx.wallet_id, 4)})
                  </span>
                </td>
                <td data-label="Amount" className={isPositive ? 'amount-positive' : 'amount-negative'}>
                  {isPositive ? '+' : '-'}{formatCurrency(Math.abs(rawAmount), currency)}
                </td>
                <td data-label="Reference" style={{ color: tx.reference ? 'var(--text-main)' : 'var(--text-muted)' }}>
                  {tx.reference || '—'}
                </td>
                <td data-label="Status">
                  <span className={`badge badge-${(tx.status || 'completed').toLowerCase()}`}>
                    {tx.status || 'completed'}
                  </span>
                </td>
                <td data-label="Details" style={{ textAlign: 'right' }}>
                  <button 
                    className="btn-link" 
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectTransaction && onSelectTransaction(tx);
                    }}
                  >
                    View →
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
