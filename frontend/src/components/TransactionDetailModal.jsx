import React, { useState } from 'react';
import { formatCurrency, formatDate, truncateId } from '../utils/formatters';

export default function TransactionDetailModal({ transaction, walletCurrencyMap = {}, onClose }) {
  const [copiedId, setCopiedId] = useState(false);
  const [copiedSource, setCopiedSource] = useState(false);
  const [copiedDest, setCopiedDest] = useState(false);

  if (!transaction) return null;

  const rawAmount = Number(transaction.amount) || 0;
  const isPositive = transaction.type === 'deposit' || rawAmount > 0;
  const currency = transaction.currency || walletCurrencyMap[transaction.wallet_id] || 'USD';
  const formattedAmount = formatCurrency(Math.abs(rawAmount), currency);

  const handleCopy = (text, setCopiedFn) => {
    if (text) {
      navigator.clipboard.writeText(text);
      setCopiedFn(true);
      setTimeout(() => setCopiedFn(false), 2000);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '520px' }}>
        <div className="modal-header" style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
          <div>
            <h3 className="modal-title" style={{ fontSize: '1.1rem', fontWeight: 600 }}>
              Transaction Details
            </h3>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Recorded on {formatDate(transaction.created_at)}
            </span>
          </div>
          <button className="btn-close-modal" onClick={onClose} aria-label="Close modal">×</button>
        </div>

        {/* Amount & Status Banner */}
        <div style={{ background: 'var(--bg-subtle)', padding: '1.25rem', borderRadius: 'var(--radius-md)', textAlign: 'center', marginBottom: '1.25rem', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: isPositive ? 'var(--color-success)' : 'var(--text-main)', marginBottom: '0.25rem' }}>
            {isPositive ? '+' : '-'}{formattedAmount}
          </div>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className={`badge badge-${(transaction.status || 'completed').toLowerCase()}`}>
              {transaction.status || 'completed'}
            </span>
            <span className="currency-pill">{currency}</span>
            <span style={{ textTransform: 'capitalize', fontSize: '0.8125rem', fontWeight: 500, color: 'var(--text-secondary)' }}>
              {transaction.type}
            </span>
          </div>
        </div>

        {/* Key Transaction Fields */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', fontSize: '0.875rem', marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Transaction ID</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontFamily: 'monospace', fontSize: '0.8rem' }}>
              <span>{truncateId(transaction.transaction_id || transaction.id, 8)}</span>
              <button className="btn-copy-id" onClick={() => handleCopy(transaction.transaction_id || transaction.id, setCopiedId)}>
                {copiedId ? 'Copied' : 'Copy'}
              </button>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Source Wallet ID</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontFamily: 'monospace', fontSize: '0.8rem' }}>
              <span>{truncateId(transaction.wallet_id, 8)}</span>
              <button className="btn-copy-id" onClick={() => handleCopy(transaction.wallet_id, setCopiedSource)}>
                {copiedSource ? 'Copied' : 'Copy'}
              </button>
            </div>
          </div>

          {transaction.destination_wallet_id && (
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Destination Wallet ID</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontFamily: 'monospace', fontSize: '0.8rem' }}>
                <span>{truncateId(transaction.destination_wallet_id, 8)}</span>
                <button className="btn-copy-id" onClick={() => handleCopy(transaction.destination_wallet_id, setCopiedDest)}>
                  {copiedDest ? 'Copied' : 'Copy'}
                </button>
              </div>
            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Reference / Description</span>
            <span style={{ fontWeight: 500, color: transaction.reference ? 'var(--text-main)' : 'var(--text-muted)' }}>
              {transaction.reference || 'None'}
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Timestamp</span>
            <span>{formatDate(transaction.created_at)}</span>
          </div>
        </div>

        {/* Ledger Impact Breakdown Section */}
        <div style={{ borderTop: '1px dashed var(--border-color)', paddingTop: '1rem', marginTop: '0.5rem' }}>
          <h4 style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '0.65rem' }}>
            Accounting Audit (Ledger Entries)
          </h4>

          <div style={{ background: 'var(--bg-app)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)', padding: '0.75rem', fontSize: '0.8125rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Ledger Entry ID</span>
              <span style={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                {truncateId(transaction.transaction_id || transaction.id, 6)}-LE
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Ledger Impact</span>
              <span style={{ fontWeight: 600, color: isPositive ? 'var(--color-success)' : 'var(--text-main)' }}>
                {isPositive ? 'CREDIT (+)' : 'DEBIT (-)'} {formattedAmount}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Affected Wallet Account</span>
              <span style={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>{currency} Wallet ({truncateId(transaction.wallet_id, 4)})</span>
            </div>
          </div>
        </div>

        <div style={{ marginTop: '1.25rem', textAlign: 'right' }}>
          <button className="btn-secondary" onClick={onClose} style={{ minWidth: '90px' }}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
