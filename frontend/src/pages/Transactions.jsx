import React, { useState, useEffect } from 'react';
import { getWalletsApi, getTransactionsApi } from '../api/api';
import TransactionTable from '../components/TransactionTable';
import TransactionDetailModal from '../components/TransactionDetailModal';
import Loading from '../components/Loading';
import ErrorMessage from '../components/ErrorMessage';
import EmptyState from '../components/EmptyState';

export default function Transactions() {
  const [wallets, setWallets] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [selectedWalletId, setSelectedWalletId] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [limit, setLimit] = useState(20);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedTransaction, setSelectedTransaction] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const walletData = await getWalletsApi();
      const walletList = walletData?.wallets || (walletData?.wallet ? [walletData.wallet] : []);
      setWallets(walletList);

      if (selectedWalletId) {
        const res = await getTransactionsApi(selectedWalletId, limit);
        setTransactions(res?.transactions || []);
      } else if (walletList.length > 0) {
        const txResults = await Promise.all(
          walletList.map((w) =>
            getTransactionsApi(w.id, limit)
              .then((res) => (res?.transactions || []).map((t) => ({ ...t, currency: w.currency })))
              .catch(() => [])
          )
        );
        const merged = txResults
          .flat()
          .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        setTransactions(merged);
      }
    } catch (err) {
      setError(err.message || 'Failed to load transactions.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [selectedWalletId, limit]);

  const filtered = transactions.filter((tx) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      (tx.reference || '').toLowerCase().includes(q) ||
      (tx.transaction_id || tx.id || '').toLowerCase().includes(q) ||
      (tx.wallet_id || '').toLowerCase().includes(q)
    );
  });

  const walletCurrencyMap = Object.fromEntries(wallets.map((w) => [w.id, w.currency]));

  return (
    <div>
      {/* Filter Bar */}
      <div className="page-header" style={{ marginBottom: '1.25rem' }}>
        <div /> {/* spacer — title is in header */}
        <div style={{ display: 'flex', gap: '0.625rem', flexWrap: 'wrap', width: '100%' }}>
          <input
            type="text"
            className="form-control"
            placeholder="Search by reference or ID…"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ flex: '1', minWidth: '160px', maxWidth: '280px' }}
          />
          <select
            className="form-control"
            value={selectedWalletId}
            onChange={(e) => setSelectedWalletId(e.target.value)}
            style={{ flex: '0 0 auto', width: 'auto', minWidth: '140px' }}
          >
            <option value="">All Wallets</option>
            {wallets.map((w) => (
              <option key={w.id} value={w.id}>{w.currency} Wallet</option>
            ))}
          </select>
          <select
            className="form-control"
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            style={{ flex: '0 0 auto', width: 'auto' }}
          >
            <option value={10}>10 items</option>
            <option value={20}>20 items</option>
            <option value={50}>50 items</option>
          </select>
        </div>
      </div>

      <ErrorMessage message={error} onRetry={fetchData} />

      {loading ? (
        <Loading message="Loading transactions…" />
      ) : filtered.length === 0 ? (
        <EmptyState
          title="No transactions found"
          description={searchQuery ? 'No transactions match your search.' : 'No transaction records to display.'}
        />
      ) : (
        <TransactionTable
          transactions={filtered}
          wallets={wallets}
          onSelectTransaction={setSelectedTransaction}
        />
      )}

      {selectedTransaction && (
        <TransactionDetailModal
          transaction={selectedTransaction}
          walletCurrencyMap={walletCurrencyMap}
          onClose={() => setSelectedTransaction(null)}
        />
      )}
    </div>
  );
}
