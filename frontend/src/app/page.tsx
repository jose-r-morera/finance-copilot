"use client";

import { useState } from "react";
import CompanyDashboard from "@/components/CompanyDashboard";

export default function Home() {
  const [ticker, setTicker] = useState("");
  const [activeTicker, setActiveTicker] = useState<string | null>(null);

  return (
    <main className="min-h-screen bg-gray-950 text-gray-100 p-6">
      <div className="max-w-6xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-blue-400">💹 Finance Copilot</h1>
          <p className="text-gray-400 mt-1">
            Corporate Finance Autopilot — AI-powered analysis · Powered by Google Gemini + Yahoo Finance
          </p>
          <p className="text-xs text-yellow-500 mt-1">
            ⚠️ Student hackathon project. NOT investment advice. Data from public sources.
          </p>
        </header>

        <div className="flex gap-3 mb-8">
          <input
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            onKeyDown={(e) => e.key === "Enter" && setActiveTicker(ticker)}
            placeholder="Enter ticker (e.g. AAPL, MSFT, TSLA)"
            className="flex-1 bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={() => setActiveTicker(ticker)}
            disabled={!ticker}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg font-medium transition-colors"
          >
            Analyse
          </button>
        </div>

        {activeTicker && <CompanyDashboard ticker={activeTicker} />}
      </div>
    </main>
  );
}
