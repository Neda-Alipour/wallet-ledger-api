import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getWalletsApi, getTransactionsApi } from '../api/api';
import WalletCard from '../components/WalletCard';
import TransactionTable from '../components/TransactionTable';
import TransactionDetailModal from '../components/TransactionDetailModal';
import SendMoneyModal from '../components/SendMoneyModal';
import Loading from '../components/Loading';
import ErrorMessage from '../components/ErrorMessage';
import EmptyState from '../components/EmptyState';
import { formatCurrency } from '../utils/formatters';
import { SendIcon, WalletsIcon, TransactionsIcon } from '../components/Icons';

export default function Dashboard() {
  const [wallets, setWallets] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [sendModalOpen, setSendModalOpen] = useState(false);
  const [selectedTransaction, setSelectedTransaction] = useState(null);

  const navigate = useNavigate();

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const walletData = await getWalletsApi();
      const walletList = walletData?.wallets || (walletData?.wallet ? [walletData.wallet] : []);
      setWallets(walletList);

      if (walletList.length > 0) {
        const txResults = await Promise.all(
          walletList.map((w) =>
            getTransactionsApi(w.id, 10)
              .then((res) => (res?.transactions || []).map((t) => ({ ...t, currency: w.currency })))
              .catch(() => [])
          )
        );
        const merged = txResults
          .flat()
          .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
          .slice(0, 10);
        setTransactions(merged);
      }
    } catch (err) {
      setError(err.message || 'Failed to load dashboard data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  if (loading) return <Loading message="Loading dashboard..." />;

  const walletCurrencyMap = Object.fromEntries(wallets.map((w) => [w.id, w.currency]));

  return (
    <div>
      <ErrorMessage message={error} onRetry={fetchData} />

      {/* TOP ROW: Summary card + Quick actions */}
      <div className="dashboard-top">
        {/* Summary Card */}
        <div className="summary-card">
          <div className="summary-label">My Wallets Summary</div>
          <div className="summary-headline">{wallets.length} active {wallets.length === 1 ? 'wallet' : 'wallets'}</div>
          <div className="summary-balances">
            {wallets.map((w) => (
              <div key={w.id} className="balance-chip">
                <span className="balance-chip-currency">{w.currency} Balance</span>
                <span className="balance-chip-amount">{formatCurrency(w.balance, w.currency)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions Card */}
        <div className="quick-card">
          <div className="qa-label">Quick Actions</div>

          <button className="qa-btn-primary" onClick={() => setSendModalOpen(true)}>
            <SendIcon style={{ width: '15px', height: '15px' }} />
            Send Money
          </button>

          <button className="qa-btn-secondary" onClick={() => navigate('/wallets')}>
            <WalletsIcon style={{ width: '15px', height: '15px' }} />
            View Wallets
          </button>

          <button className="qa-btn-secondary" onClick={() => navigate('/transactions')}>
            <TransactionsIcon style={{ width: '15px', height: '15px' }} />
            View Transactions
          </button>
        </div>
      </div>

      {/* My Wallets Section */}
      <div style={{ marginBottom: '2rem' }}>
        <div className="section-header">
          <h2 className="section-title">My Wallets</h2>
          <Link to="/wallets" className="section-link">Manage wallets →</Link>
        </div>

        {wallets.length === 0 ? (
          <EmptyState title="No wallets found" description="No active wallet accounts associated with this profile." />
        ) : (
          <div className="wallets-grid">
            {wallets.map((wallet) => (
              <WalletCard key={wallet.id} wallet={wallet} showActions={false} />
            ))}
          </div>
        )}
      </div>

      {/* Recent Activity Section */}
      <div>
        <div className="section-header">
          <h2 className="section-title">Recent Activity</h2>
          <Link to="/transactions" className="section-link">View all transactions →</Link>
        </div>

        {transactions.length === 0 ? (
          <EmptyState
            title="No transactions yet"
            description="Your wallet activity will appear here once you make or receive a transfer."
          />
        ) : (
          <TransactionTable
            transactions={transactions}
            wallets={wallets}
            onSelectTransaction={setSelectedTransaction}
          />
        )}
      </div>

      {/* Send Money Modal */}
      <SendMoneyModal
        wallets={wallets}
        isOpen={sendModalOpen}
        onClose={() => setSendModalOpen(false)}
        onSuccess={fetchData}
      />

      {/* Transaction Detail Modal */}
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
