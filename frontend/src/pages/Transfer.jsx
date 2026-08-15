import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getWalletsApi, transferApi } from '../api/api';
import TransactionResult from '../components/TransactionResult';
import TransactionDetailModal from '../components/TransactionDetailModal';
import Loading from '../components/Loading';
import ErrorMessage from '../components/ErrorMessage';
import { formatCurrency, truncateId } from '../utils/formatters';

export default function Transfer() {
  const [wallets, setWallets] = useState([]);
  const [sourceWalletId, setSourceWalletId] = useState('');
  const [destinationWalletId, setDestinationWalletId] = useState('');
  const [amount, setAmount] = useState('');
  const [reference, setReference] = useState('');
  
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Transfer Step State: 'form' | 'review' | 'receipt'
  const [step, setStep] = useState('form');
  const [completedTransfer, setCompletedTransfer] = useState(null);
  const [detailTransaction, setDetailTransaction] = useState(null);

  const navigate = useNavigate();

  const loadWallets = async () => {
    setLoading(true);
    setError('');

    try {
      const data = await getWalletsApi();
      const walletList = data?.wallets || (data?.wallet ? [data.wallet] : []);
      setWallets(walletList);

      if (walletList.length > 0 && !sourceWalletId) {
        setSourceWalletId(walletList[0].id);
      }
    } catch (err) {
      setError(err.message || 'Failed to load source wallets.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWallets();
  }, []);

  const selectedSourceWallet = wallets.find((w) => w.id === sourceWalletId);

  const handleReviewStep = (e) => {
    e.preventDefault();
    setError('');

    if (!sourceWalletId) {
      setError('Please select a source wallet.');
      return;
    }

    if (!destinationWalletId.trim()) {
      setError('Destination Wallet ID is required.');
      return;
    }

    if (sourceWalletId === destinationWalletId.trim()) {
      setError('Source and destination wallet IDs must be different.');
      return;
    }

    const numericAmount = Number(amount);
    if (!numericAmount || numericAmount <= 0) {
      setError('Transfer amount must be greater than zero.');
      return;
    }

    if (selectedSourceWallet && numericAmount > Number(selectedSourceWallet.balance)) {
      setError(`Insufficient balance. Available balance: ${formatCurrency(selectedSourceWallet.balance, selectedSourceWallet.currency)}.`);
      return;
    }

    // Proceed to Step 2: Confirmation Review
    setStep('review');
  };

  const handleConfirmTransfer = async () => {
    setSubmitting(true);
    setError('');

    try {
      const result = await transferApi(
        sourceWalletId,
        destinationWalletId.trim(),
        Number(amount),
        reference
      );

      setCompletedTransfer(result);
      setStep('receipt');
      await loadWallets(); // Refresh wallet balances
    } catch (err) {
      setStep('form');
      setError(err.message || 'Transfer failed. Please verify the destination wallet ID.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <Loading message="Loading wallets..." />;
  }

  // Create wallet currency map for transaction detail modal
  const walletCurrencyMap = {};
  wallets.forEach((w) => {
    walletCurrencyMap[w.id] = w.currency;
  });

  // Step 3: Receipt View
  if (step === 'receipt' && completedTransfer) {
    return (
      <div style={{ padding: '1rem 0' }}>
        <TransactionResult 
          transaction={completedTransfer} 
          type="transfer" 
          currency={selectedSourceWallet?.currency || 'USD'}
          onDone={() => {
            setStep('form');
            setCompletedTransfer(null);
            setDestinationWalletId('');
            setAmount('');
            setReference('');
          }}
          onViewTransaction={() => {
            const tx = completedTransfer;
            setCompletedTransfer(null);
            setStep('form');
            setDetailTransaction(tx);
          }}
        />

        {detailTransaction && (
          <TransactionDetailModal 
            transaction={detailTransaction} 
            walletCurrencyMap={walletCurrencyMap} 
            onClose={() => setDetailTransaction(null)} 
          />
        )}
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '540px', margin: '0 auto' }}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Send money</h1>
          <p className="page-subtitle">Transfer funds directly between wallets in the system.</p>
        </div>
      </div>

      <ErrorMessage message={error} />

      {/* Step 1: Form */}
      {step === 'form' && (
        <div className="card">
          <form onSubmit={handleReviewStep}>
            <div className="form-group">
              <label className="form-label" htmlFor="source-wallet">From (Your Source Wallet)</label>
              <select
                id="source-wallet"
                className="form-control"
                value={sourceWalletId}
                onChange={(e) => setSourceWalletId(e.target.value)}
                disabled={submitting}
              >
                {wallets.map((w) => (
                  <option key={w.id} value={w.id}>
                    {w.currency} Wallet — Available: {formatCurrency(w.balance, w.currency)}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="destination-wallet">To (Destination Wallet ID)</label>
              <input
                id="destination-wallet"
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
              <label className="form-label" htmlFor="transfer-amount">
                Amount ({selectedSourceWallet?.currency || 'USD'})
              </label>
              <input
                id="transfer-amount"
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
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="transfer-reference">Reference (Optional)</label>
              <input
                id="transfer-reference"
                type="text"
                className="form-control"
                placeholder="e.g. Invoice payment or description"
                value={reference}
                onChange={(e) => setReference(e.target.value)}
                disabled={submitting}
              />
            </div>

            <button type="submit" className="btn-primary" disabled={submitting} style={{ marginTop: '0.75rem', width: '100%' }}>
              Review transfer →
            </button>
          </form>
        </div>
      )}

      {/* Step 2: Confirmation Review Summary */}
      {step === 'review' && (
        <div className="card">
          <h2 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
            Review transfer summary
          </h2>

          <div style={{ textAlign: 'center', padding: '1.25rem 0', background: 'var(--bg-subtle)', borderRadius: 'var(--radius-sm)', marginBottom: '1.25rem', border: '1px solid var(--border-color)' }}>
            <span style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>You are sending</span>
            <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--accent-primary)', marginTop: '0.2rem' }}>
              {formatCurrency(amount, selectedSourceWallet?.currency)}
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-secondary)' }}>From Source Wallet</span>
              <span style={{ fontWeight: 500 }}>
                {selectedSourceWallet?.currency} Wallet ({truncateId(sourceWalletId, 6)})
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
              {submitting ? 'Processing...' : 'Confirm & Send'}
            </button>
          </div>
        </div>
      )}

      {detailTransaction && (
        <TransactionDetailModal 
          transaction={detailTransaction} 
          walletCurrencyMap={walletCurrencyMap} 
          onClose={() => setDetailTransaction(null)} 
        />
      )}
    </div>
  );
}
