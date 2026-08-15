import React, { useState } from 'react';
import { transferApi } from '../api/api';
import TransactionResult from './TransactionResult';
import ErrorMessage from './ErrorMessage';
import { formatCurrency, truncateId } from '../utils/formatters';

export default function SendMoneyModal({ wallets = [], isOpen, onClose, onSuccess }) {
  const [sourceWalletId, setSourceWalletId] = useState(wallets.length > 0 ? wallets[0].id : '');
  const [destinationWalletId, setDestinationWalletId] = useState('');
  const [amount, setAmount] = useState('');
  const [reference, setReference] = useState('');

  const [step, setStep] = useState('form'); // 'form' | 'review' | 'receipt'
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [completedTransfer, setCompletedTransfer] = useState(null);

  if (!isOpen) return null;

  const selectedSourceWallet = wallets.find((w) => w.id === (sourceWalletId || (wallets[0]?.id)));
  const currentSourceId = sourceWalletId || (wallets[0]?.id || '');

  const handleReviewStep = (e) => {
    e.preventDefault();
    setError('');

    if (!currentSourceId) {
      setError('Please select a source wallet.');
      return;
    }

    if (!destinationWalletId.trim()) {
      setError('Destination Wallet ID is required.');
      return;
    }

    if (currentSourceId === destinationWalletId.trim()) {
      setError('Source and destination wallet IDs must be different.');
      return;
    }

    const numAmount = Number(amount);
    if (!numAmount || numAmount <= 0) {
      setError('Transfer amount must be greater than zero.');
      return;
    }

    if (selectedSourceWallet && numAmount > Number(selectedSourceWallet.balance)) {
      setError(`Insufficient balance. Available balance: ${formatCurrency(selectedSourceWallet.balance, selectedSourceWallet.currency)}.`);
      return;
    }

    setStep('review');
  };

  const handleConfirmTransfer = async () => {
    setSubmitting(true);
    setError('');

    try {
      const result = await transferApi(
        currentSourceId,
        destinationWalletId.trim(),
        Number(amount),
        reference
      );

      setCompletedTransfer(result);
      setStep('receipt');
      if (onSuccess) onSuccess();
    } catch (err) {
      setStep('form');
      setError(err.message || 'Transfer failed. Please check the recipient wallet ID.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = () => {
    setStep('form');
    setCompletedTransfer(null);
    setDestinationWalletId('');
    setAmount('');
    setReference('');
    setError('');
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={handleReset}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '480px' }}>
        <div className="modal-header">
          <h3 className="modal-title">
            {step === 'receipt' ? 'Transfer Receipt' : step === 'review' ? 'Review Transfer' : 'Send Money'}
          </h3>
          <button className="btn-close-modal" onClick={handleReset}>×</button>
        </div>

        <ErrorMessage message={error} />

        {/* Step 1: Form */}
        {step === 'form' && (
          <form onSubmit={handleReviewStep}>
            <div className="form-group">
              <label className="form-label">From (Your Wallet)</label>
              <select
                className="form-control"
                value={currentSourceId}
                onChange={(e) => setSourceWalletId(e.target.value)}
                disabled={submitting}
              >
                {wallets.map((w) => (
                  <option key={w.id} value={w.id}>
                    {w.currency} Wallet — Balance: {formatCurrency(w.balance, w.currency)}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">To (Destination Wallet ID)</label>
              <input
                type="text"
                className="form-control"
                placeholder="e.g. 550e8400-e29b-41d4-a716-446655440000"
                value={destinationWalletId}
                onChange={(e) => setDestinationWalletId(e.target.value)}
                disabled={submitting}
                required
                style={{ fontFamily: 'monospace' }}
              />
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Enter the recipient's wallet UUID.
              </span>
            </div>

            <div className="form-group">
              <label className="form-label">
                Amount ({selectedSourceWallet?.currency || 'USD'})
              </label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                className="form-control"
                placeholder="0.00"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                disabled={submitting}
                required
              />
              {selectedSourceWallet && (
                <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                  Available balance: {formatCurrency(selectedSourceWallet.balance, selectedSourceWallet.currency)}
                </span>
              )}
            </div>

            <div className="form-group">
              <label className="form-label">Reference (Optional)</label>
              <input
                type="text"
                className="form-control"
                placeholder="e.g. Payment note"
                value={reference}
                onChange={(e) => setReference(e.target.value)}
                disabled={submitting}
              />
            </div>

            <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1.25rem' }}>
              <button type="button" className="btn-secondary" onClick={handleReset} style={{ flex: 1 }}>
                Cancel
              </button>
              <button type="submit" className="btn-primary" style={{ flex: 1 }}>
                Review transfer →
              </button>
            </div>
          </form>
        )}

        {/* Step 2: Review Transfer Summary */}
        {step === 'review' && (
          <div>
            <div style={{ textAlign: 'center', padding: '1.25rem', background: 'var(--bg-subtle)', borderRadius: 'var(--radius-md)', marginBottom: '1.25rem', border: '1px solid var(--border-color)' }}>
              <span style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>You are sending</span>
              <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--accent-primary)', marginTop: '0.2rem' }}>
                {formatCurrency(amount, selectedSourceWallet?.currency)}
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>From Source Wallet</span>
                <span style={{ fontWeight: 500 }}>
                  {selectedSourceWallet?.currency} Wallet ({truncateId(currentSourceId, 6)})
                </span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>To Destination Wallet</span>
                <span style={{ fontFamily: 'monospace', fontWeight: 500 }}>
                  {truncateId(destinationWalletId, 8)}
                </span>
              </div>

              {reference && (
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Reference</span>
                  <span>{reference}</span>
                </div>
              )}
            </div>

            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button 
                type="button" 
                className="btn-secondary" 
                onClick={() => setStep('form')} 
                disabled={submitting}
                style={{ flex: 1 }}
              >
                Back to edit
              </button>
              <button 
                type="button" 
                className="btn-primary" 
                onClick={handleConfirmTransfer} 
                disabled={submitting}
                style={{ flex: 1 }}
              >
                {submitting ? 'Processing...' : 'Confirm transfer'}
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Receipt View */}
        {step === 'receipt' && completedTransfer && (
          <TransactionResult 
            transaction={completedTransfer} 
            type="transfer" 
            currency={selectedSourceWallet?.currency || 'USD'}
            onDone={handleReset}
            onViewTransaction={handleReset}
          />
        )}
      </div>
    </div>
  );
}
