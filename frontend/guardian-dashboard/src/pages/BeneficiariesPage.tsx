import React from 'react';
import './BeneficiariesPage.css';

export default function BeneficiariesPage() {
  const beneficiaries = []; // TODO: Fetch from API

  return (
    <div className="beneficiaries">
      <h1>Beneficiaries</h1>
      
      <button className="add-btn">+ Add Beneficiary</button>

      {beneficiaries.length === 0 ? (
        <div className="empty-state">
          <p>No beneficiaries added yet</p>
          <p>Start by adding a beneficiary account</p>
        </div>
      ) : (
        <div className="beneficiaries-grid">
          {beneficiaries.map((beneficiary: any) => (
            <div key={beneficiary.user_id} className="beneficiary-card">
              <h3>{beneficiary.full_name}</h3>
              <p className="email">{beneficiary.email}</p>
              <div className="status">
                <p>Account Balance: ${beneficiary.balance?.toFixed(2) || '0.00'}</p>
                <p>Last Transaction: {beneficiary.last_transaction || 'Never'}</p>
              </div>
              <button className="view-btn">View Details</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
