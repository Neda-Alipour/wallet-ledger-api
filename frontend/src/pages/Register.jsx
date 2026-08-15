import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogoIcon } from '../components/Icons';

export default function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const validate = () => {
    if (!email.trim())         return 'Email address is required.';
    if (password.length < 4)   return 'Password must be at least 4 characters.';
    if (!/[A-Z]/.test(password)) return 'Password must include at least one uppercase letter (A–Z).';
    if (!/[0-9]/.test(password)) return 'Password must include at least one digit (0–9).';
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    const validationErr = validate();
    if (validationErr) { setError(validationErr); return; }
    setSubmitting(true);
    try {
      await register(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Registration failed. Email may already be in use.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <div className="auth-brand">
          <div className="auth-logo-mark">
            <LogoIcon style={{ width: '22px', height: '22px', color: '#fff' }} />
          </div>
          <div>
            <div className="auth-app-name">Wallet Ledger</div>
          </div>
        </div>

        <h1 className="auth-title" style={{ textAlign: 'center', marginBottom: '0.25rem' }}>Create account</h1>
        <p className="auth-subtitle" style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          Get started with multi-currency wallets
        </p>

        {error && <div className="alert-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="register-email">Email address</label>
            <input
              id="register-email"
              type="email"
              className="form-control"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={submitting}
              autoComplete="email"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="register-password">Password</label>
            <input
              id="register-password"
              type="password"
              className="form-control"
              placeholder="Min 4 chars, 1 uppercase, 1 number"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={submitting}
              autoComplete="new-password"
              required
            />
            <span className="form-hint">Minimum 4 characters, 1 uppercase letter, 1 digit.</span>
          </div>

          <button
            type="submit"
            className="btn-primary"
            disabled={submitting}
            style={{ width: '100%', marginTop: '0.5rem' }}
          >
            {submitting ? 'Creating account…' : 'Create account'}
          </button>
        </form>

        <div className="auth-footer">
          Already have an account?{' '}
          <Link to="/login" style={{ fontWeight: 600, color: 'var(--text-main)' }}>
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}
