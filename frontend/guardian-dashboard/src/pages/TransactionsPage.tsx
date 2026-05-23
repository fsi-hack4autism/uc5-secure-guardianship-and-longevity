import React from 'react';
import './TransactionsPage.css';

export default function TransactionsPage() {
  const transactions = []; // TODO: Fetch from API

  return (
    <div className="transactions">
      <h1>Transactions</h1>
      
      <div className="filters">
        <input type="text" placeholder="Search transactions..." />
        <select>
          <option>All Status</option>
          <option>Pending</option>
          <option>Approved</option>
          <option>Rejected</option>
        </select>
      </div>

      {transactions.length === 0 ? (
        <div className="empty-state">
          <p>No transactions yet</p>
        </div>
      ) : (
        <table className="transactions-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Beneficiary</th>
              <th>Amount</th>
              <th>Merchant</th>
              <th>Status</th>
              <th>Risk Level</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((tx: any) => (
              <tr key={tx.transaction_id}>
                <td>{new Date(tx.created_at).toLocaleDateString()}</td>
                <td>{tx.beneficiary_name}</td>
                <td>${tx.amount.toFixed(2)}</td>
                <td>{tx.merchant_name}</td>
                <td><span className="status">{tx.status}</span></td>
                <td><span className={`risk ${tx.risk_level}`}>{tx.risk_level}</span></td>
                <td>
                  {tx.requires_guardian_approval && (
                    <>
                      <button className="approve-btn">Approve</button>
                      <button className="reject-btn">Reject</button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
