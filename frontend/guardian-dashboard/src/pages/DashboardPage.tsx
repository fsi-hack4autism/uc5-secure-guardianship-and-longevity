import React from 'react';
import './DashboardPage.css';

export default function DashboardPage() {
  return (
    <div className="dashboard">
      <h1>Guardian Dashboard</h1>
      <div className="welcome-message">
        <h2>Welcome to AI Financial Guardrails</h2>
        <p>
          This is your central hub for managing beneficiary accounts, monitoring transactions,
          and ensuring financial security.
        </p>
      </div>

      <div className="dashboard-grid">
        <div className="card">
          <h3>Pending Approvals</h3>
          <p className="metric">0</p>
          <p className="description">Transactions awaiting your review</p>
        </div>

        <div className="card">
          <h3>Active Beneficiaries</h3>
          <p className="metric">0</p>
          <p className="description">People under your guardianship</p>
        </div>

        <div className="card">
          <h3>Fraud Alerts</h3>
          <p className="metric">0</p>
          <p className="description">Suspicious activities detected</p>
        </div>

        <div className="card">
          <h3>Monthly Volume</h3>
          <p className="metric">$0</p>
          <p className="description">Total transactions this month</p>
        </div>
      </div>

      <div className="quick-actions">
        <h3>Quick Actions</h3>
        <div className="actions">
          <button className="action-btn">Review Pending Transactions</button>
          <button className="action-btn">View Beneficiary Accounts</button>
          <button className="action-btn">Generate Compliance Report</button>
        </div>
      </div>
    </div>
  );
}
