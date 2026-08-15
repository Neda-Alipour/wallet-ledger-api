import React, { useState } from 'react';
import { formatCurrency, truncateId } from '../utils/formatters';

export default function WalletCard({ wallet, onDeposit, onWithdraw, showActions = true }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (wallet?.id) {
      navigator.clipboard.writeText(wallet.id);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="wallet-card">
      {/* Top row: currency label + status */}
      <div className="wallet-card-top">
        <span className="wallet-currency-badge">{wallet.currency} Wallet</span>
        <span className="wallet-status-dot">Active</span>
      </div>

      {/* Balance */}
      <div className="wallet-balance">{formatCurrency(wallet.balance, wallet.currency)}</div>
      <div className="wallet-balance-label">Available balance</div>

      {/* Wallet ID */}
      <div className="wallet-id-row">
        <span title={wallet.id}>ID: {truncateId(wallet.id, 6)}</span>
        <button className="btn-copy-id" onClick={handleCopy}>
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>

      {/* Optional actions */}
      {showActions && (onDeposit || onWithdraw) && (
        <div className="wallet-actions">
          {onDeposit && (
            <button className="btn-secondary" style={{ flex: 1 }} onClick={() => onDeposit(wallet)}>
              Deposit
            </button>
          )}
          {onWithdraw && (
            <button className="btn-secondary" style={{ flex: 1 }} onClick={() => onWithdraw(wallet)}>
              Withdraw
            </button>
          )}
        </div>
      )}
    </div>
  );
}
