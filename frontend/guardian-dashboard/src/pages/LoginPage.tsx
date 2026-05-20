import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import './LoginPage.css';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [isSignup, setIsSignup] = useState(false);
  const [userType, setUserType] = useState('guardian');
  const [fullName, setFullName] = useState('');

  const navigate = useNavigate();
  const { login, signup } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isSignup) {
        await signup(email, password, userType, fullName);
      } else {
        await login(email, password);
      }
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>AI Financial Guardrails</h1>
        <p className="subtitle">Secure guardianship & longevity</p>

        <form onSubmit={handleSubmit}>
          {error && <div className="error-message">{error}</div>}

          {isSignup && (
            <>
              <div className="form-group">
                <label>Full Name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                  placeholder="Your full name"
                />
              </div>

              <div className="form-group">
                <label>User Type</label>
                <select value={userType} onChange={(e) => setUserType(e.target.value)}>
                  <option value="beneficiary">Beneficiary (Protected Person)</option>
                  <option value="guardian">Guardian</option>
                  <option value="advisor">Financial Advisor</option>
                </select>
              </div>
            </>
          )}

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="your@email.com"
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Password"
            />
          </div>

          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? 'Loading...' : isSignup ? 'Sign Up' : 'Sign In'}
          </button>
        </form>

        <div className="toggle-auth">
          <p>
            {isSignup ? 'Already have an account?' : "Don't have an account?"}
            <button
              type="button"
              onClick={() => {
                setIsSignup(!isSignup);
                setError('');
              }}
              className="toggle-btn"
            >
              {isSignup ? 'Sign In' : 'Sign Up'}
            </button>
          </p>
        </div>

        <div className="demo-hint">
          <p>Demo credentials:</p>
          <p>Email: guardian@example.com</p>
          <p>Password: password123</p>
        </div>
      </div>
    </div>
  );
}
