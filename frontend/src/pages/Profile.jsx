import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { getWalletsApi } from '../api/api';
import { formatCurrency } from '../utils/formatters';

export default function Profile() {
  const { user, logout } = useAuth();
  const [wallets, setWallets] = useState([]);

  useEffect(() => {
    async function loadUserWallets() {
      try {
        const data = await getWalletsApi();
        setWallets(data?.wallets || []);
      } catch (err) {
        console.error('Failed to load profile wallets:', err);
      }
    }
    loadUserWallets();
  }, []);

  return (
    <div style={{ maxWidth: '540px' }}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Profile & Account</h1>
          <p className="page-subtitle">Your user account details and wallet summary.</p>
        </div>
      </div>

      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.85rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
          Account details
        </h2>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          <div>
            <span className="form-label" style={{ display: 'block', color: 'var(--text-secondary)' }}>Email address</span>
            <span style={{ fontSize: '0.9375rem', fontWeight: 500, color: 'var(--text-main)' }}>
              {user?.name || user?.email || 'N/A'}
            </span>
          </div>

          <div>
            <span className="form-label" style={{ display: 'block', color: 'var(--text-secondary)' }}>User ID</span>
            <span style={{ fontFamily: 'monospace', fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
              {user?.id || 'N/A'}
            </span>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.85rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
          Wallets ({wallets.length})
        </h2>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {wallets.map((wallet) => (
            <div 
              key={wallet.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0.6rem 0.75rem',
                background: 'var(--bg-subtle)',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-color)'
              }}
            >
              <div>
                <span style={{ fontWeight: 500, fontSize: '0.875rem' }}>{wallet.currency} Wallet</span>
                <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                  {wallet.id}
                </span>
              </div>
              <span style={{ fontWeight: 600, fontSize: '0.9375rem', color: 'var(--text-main)' }}>
                {formatCurrency(wallet.balance, wallet.currency)}
              </span>
            </div>
          ))}
        </div>

        <button 
          onClick={logout} 
          className="btn-logout" 
          style={{ width: '100%', marginTop: '1.25rem', padding: '0.55rem' }}
        >
          Sign out
        </button>
      </div>
    </div>
  );
}
