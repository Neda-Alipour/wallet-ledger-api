import React, { useState, useEffect } from 'react';
import { getWalletsApi, getTransactionsApi, depositApi, withdrawApi } from '../api/api';
import WalletCard from '../components/WalletCard';
import TransactionTable from '../components/TransactionTable';
import TransactionResult from '../components/TransactionResult';
import TransactionDetailModal from '../components/TransactionDetailModal';
import Loading from '../components/Loading';
import ErrorMessage from '../components/ErrorMessage';
import EmptyState from '../components/EmptyState';
import { formatCurrency } from '../utils/formatters';

export default function Wallets() {
  const [wallets, setWallets] = useState([]);
  const [walletTxCounts, setWalletTxCounts] = useState({});
  const [selectedWalletId, setSelectedWalletId] = useState('');
  const [selectedWalletTransactions, setSelectedWalletTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Deposit / Withdraw modal
  const [activeModal, setActiveModal] = useState(null);
  const [selectedModalWallet, setSelectedModalWallet] = useState(null);
  const [amount, setAmount] = useState('');
  const [reference, setReference] = useState('');
  const [modalSubmitting, setModalSubmitting] = useState(false);
  const [modalError, setModalError] = useState('');

  // Receipt
  const [completedTransaction, setCompletedTransaction] = useState(null);
  const [completedType, setCompletedType] = useState('deposit');

  // Detail modal
  const [detailTransaction, setDetailTransaction] = useState(null);

  const fetchWallets = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getWalletsApi();
      const walletList = data?.wallets || (data?.wallet ? [data.wallet] : []);
      setWallets(walletList);

      if (walletList.length > 0 && !selectedWalletId) {
        setSelectedWalletId(walletList[0].id);
      }

      const counts = {};
      await Promise.all(
        walletList.map(async (w) => {
          try {
            const res = await getTransactionsApi(w.id, 50);
            counts[w.id] = (res?.transactions || []).length;
          } catch {
            counts[w.id] = 0;
          }
        })
      );
      setWalletTxCounts(counts);
    } catch (err) {
      setError(err.message || 'Failed to load wallets.');
    } finally {
      setLoading(false);
    }
  };

  const fetchWalletTx = async (walletId) => {
    if (!walletId) return;
    try {
      const res = await getTransactionsApi(walletId, 20);
      setSelectedWalletTransactions(res?.transactions || []);
    } catch { /* silent */ }
  };

  useEffect(() => { fetchWallets(); }, []);
  useEffect(() => { if (selectedWalletId) fetchWalletTx(selectedWalletId); }, [selectedWalletId]);

  const openModal = (wallet, type) => {
    setSelectedModalWallet(wallet);
    setActiveModal(type);
    setAmount('');
    setReference('');
    setModalError('');
  };

  const closeModal = () => {
    setActiveModal(null);
    setSelectedModalWallet(null);
    setModalError('');
  };

  const handleModalSubmit = async (e) => {
    e.preventDefault();
    setModalError('');
    const num = Number(amount);
    if (!num || num <= 0) { setModalError('Enter a valid amount greater than zero.'); return; }
    setModalSubmitting(true);
    try {
      let result;
      if (activeModal === 'deposit') {
        result = await depositApi(selectedModalWallet.id, num, reference);
        setCompletedType('deposit');
      } else {
        result = await withdrawApi(selectedModalWallet.id, num, reference);
        setCompletedType('withdrawal');
      }
      closeModal();
      setCompletedTransaction(result);
      await fetchWallets();
    } catch (err) {
      setModalError(err.message || `${activeModal} failed.`);
    } finally {
      setModalSubmitting(false);
    }
  };

  if (loading) return <Loading message="Loading wallets..." />;

  if (completedTransaction) {
    return (
      <div>
        <TransactionResult
          transaction={completedTransaction}
          type={completedType}
          currency={selectedModalWallet?.currency || 'USD'}
          onDone={() => setCompletedTransaction(null)}
          onViewTransaction={() => {
            const tx = completedTransaction;
            setCompletedTransaction(null);
            setDetailTransaction(tx);
          }}
        />
      </div>
    );
  }

  const walletCurrencyMap = Object.fromEntries(wallets.map((w) => [w.id, w.currency]));
  const activeWallet = wallets.find((w) => w.id === selectedWalletId);

  return (
    <div>
      <ErrorMessage message={error} onRetry={fetchWallets} />

      {/* Wallet Cards Grid */}
      {wallets.length === 0 ? (
        <EmptyState title="No wallets found" description="You don't have any active wallet accounts." />
      ) : (
        <>
          <div className="wallets-grid" style={{ marginBottom: '2.5rem' }}>
            {wallets.map((wallet) => (
              <div key={wallet.id}>
                <WalletCard
                  wallet={wallet}
                  showActions={true}
                  onDeposit={(w) => openModal(w, 'deposit')}
                  onWithdraw={(w) => openModal(w, 'withdraw')}
                />
                <div style={{
                  padding: '0.4rem 1rem',
                  background: 'var(--bg-subtle)',
                  border: '1px solid var(--border-color)',
                  borderTop: 'none',
                  borderRadius: '0 0 var(--r-md) var(--r-md)',
                  fontSize: '0.75rem',
                  color: 'var(--text-secondary)',
                  display: 'flex',
                  justifyContent: 'space-between'
                }}>
                  <span>Transactions</span>
                  <span style={{ fontWeight: 600 }}>{walletTxCounts[wallet.id] ?? 0}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Wallet Activity Filter */}
          <div className="section-header">
            <h2 className="section-title">Wallet Activity</h2>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              {wallets.map((w) => (
                <button
                  key={w.id}
                  className="btn-secondary"
                  onClick={() => setSelectedWalletId(w.id)}
                  style={{
                    background: selectedWalletId === w.id ? 'var(--bg-subtle)' : undefined,
                    fontWeight: selectedWalletId === w.id ? 600 : 500,
                    borderColor: selectedWalletId === w.id ? 'var(--border-dark)' : undefined,
                    minHeight: '32px',
                    padding: '0.3rem 0.75rem',
                    fontSize: '0.8125rem',
                  }}
                >
                  {w.currency} Wallet
                </button>
              ))}
            </div>
          </div>

          {selectedWalletTransactions.length === 0 ? (
            <EmptyState
              title={`No transactions for ${activeWallet?.currency || ''} wallet`}
              description="No transaction records for the selected wallet."
            />
          ) : (
            <TransactionTable
              transactions={selectedWalletTransactions}
              wallets={wallets}
              onSelectTransaction={setDetailTransaction}
            />
          )}
        </>
      )}

      {/* Deposit / Withdraw Modal */}
      {activeModal && selectedModalWallet && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <div className="modal-title" style={{ textTransform: 'capitalize' }}>
                  {activeModal === 'deposit' ? 'Deposit funds' : 'Withdraw funds'}
                </div>
                <div className="modal-subtitle">{selectedModalWallet.currency} Wallet</div>
              </div>
              <button className="btn-close-modal" onClick={closeModal}>×</button>
            </div>

            {modalError && <div className="alert-error">{modalError}</div>}

            <form onSubmit={handleModalSubmit}>
              <div className="form-group">
                <label className="form-label">Wallet ID</label>
                <input type="text" className="form-control" value={selectedModalWallet.id} disabled style={{ fontFamily: 'monospace', fontSize: '0.8rem' }} />
              </div>

              <div className="form-group">
                <label className="form-label">Amount ({selectedModalWallet.currency})</label>
                <input
                  type="number" step="0.01" min="0.01"
                  className="form-control" placeholder="0.00"
                  value={amount} onChange={(e) => setAmount(e.target.value)}
                  disabled={modalSubmitting} required
                />
                {activeModal === 'withdraw' && selectedModalWallet?.balance !== undefined && (
                  <span className="form-hint">
                    Available: {formatCurrency(selectedModalWallet.balance, selectedModalWallet.currency)}
                  </span>
                )}
              </div>

              <div className="form-group">
                <label className="form-label">Reference (Optional)</label>
                <input
                  type="text" className="form-control" placeholder="e.g. Salary deposit"
                  value={reference} onChange={(e) => setReference(e.target.value)}
                  disabled={modalSubmitting}
                />
              </div>

              <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
                <button type="button" className="btn-secondary" onClick={closeModal} disabled={modalSubmitting} style={{ flex: 1 }}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={modalSubmitting} style={{ flex: 1 }}>
                  {modalSubmitting ? 'Processing…' : `Submit ${activeModal}`}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Transaction Detail Modal */}
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
