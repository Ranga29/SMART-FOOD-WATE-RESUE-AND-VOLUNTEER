import React, { useState } from "react";
import { Navbar } from "@/components/Navbar";
import { donorService } from "@/services/api";

export default function DonorPage() {
  const [formData, setFormData] = useState({
    donor_id: 1,
    food_name: "",
    servings: 40,
    expiry_hours: 4,
  });
  const [status, setStatus] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Calculate future expiry using exact epoch milliseconds
      const now = new Date();
      const expiry = new Date(now.getTime() + Number(formData.expiry_hours) * 60 * 60 * 1000);

      await donorService.postSurplus({
        donor_id: Number(formData.donor_id),
        food_name: formData.food_name,
        servings: Number(formData.servings),
        expiry_time: expiry.toISOString(),
      });
      setStatus("Surplus posted successfully!");
      setFormData({ donor_id: 1, food_name: "", servings: 40, expiry_hours: 4 });
    } catch (err: any) {
      setStatus("Failed to post surplus: " + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div>
      <Navbar />
      <div className="max-w-xl mx-auto px-4 py-10">
        <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200">
          <h2 className="text-2xl font-bold text-slate-800 mb-6">Post Food Surplus</h2>
          {status && <div className="mb-4 text-sm font-medium text-emerald-700 bg-emerald-50 p-3 rounded">{status}</div>}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 uppercase mb-1">Food Item Description</label>
              <input
                type="text"
                className="w-full border rounded-md p-2 text-sm"
                value={formData.food_name}
                onChange={(e) => setFormData({ ...formData, food_name: e.target.value })}
                placeholder="e.g. Steamed Rice & Dal"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 uppercase mb-1">Portions / Servings</label>
              <input
                type="number"
                className="w-full border rounded-md p-2 text-sm"
                value={formData.servings}
                onChange={(e) => setFormData({ ...formData, servings: Number(e.target.value) })}
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 uppercase mb-1">Safe Shelf Window (Hours)</label>
              <input
                type="number"
                className="w-full border rounded-md p-2 text-sm"
                value={formData.expiry_hours}
                onChange={(e) => setFormData({ ...formData, expiry_hours: Number(e.target.value) })}
                required
              />
            </div>
            <button
              type="submit"
              className="w-full bg-emerald-600 text-white font-medium py-2.5 rounded-md hover:bg-emerald-700 transition"
            >
              Broadcast Surplus Listing
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}