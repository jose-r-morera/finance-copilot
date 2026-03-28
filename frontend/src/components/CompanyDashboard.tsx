"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar,
} from "recharts";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface CompanyInfo {
  name: string;
  sector: string;
  industry: string;
  description: string;
  market_cap: number;
  currency: string;
  website: string;
  country: string;
}

interface PricePoint {
  date: string;
  close: number;
}

interface ForecastRow {
  year: string;
  revenue: number;
  cagr: number;
}

interface Forecast {
  historical_cagr_pct: number;
  scenarios: { base: ForecastRow[]; upside: ForecastRow[]; downside: ForecastRow[] };
  disclaimer: string;
}

function fmt(n: number | null | undefined, decimals = 0): string {
  if (n == null) return "N/A";
  if (Math.abs(n) >= 1e9) return `${(n / 1e9).toFixed(1)}B`;
  if (Math.abs(n) >= 1e6) return `${(n / 1e6).toFixed(1)}M`;
  return n.toLocaleString(undefined, { maximumFractionDigits: decimals });
}

export default function CompanyDashboard({ ticker }: { ticker: string }) {
  const [info, setInfo] = useState<CompanyInfo | null>(null);
  const [prices, setPrices] = useState<PricePoint[]>([]);
  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [advisory, setAdvisory] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [loadingAdvisory, setLoadingAdvisory] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    setAdvisory("");
    Promise.all([
      axios.get(`${API}/api/v1/company/info/${ticker}`).then((r) => setInfo(r.data)),
      axios
        .get(`${API}/api/v1/company/prices/${ticker}?period=1y`)
        .then((r) => setPrices(r.data.slice(-60))),
      axios.get(`${API}/api/v1/model/forecast/${ticker}`).then((r) => setForecast(r.data)),
    ])
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [ticker]);

  const fetchAdvisory = async () => {
    setLoadingAdvisory(true);
    try {
      const res = await axios.post(`${API}/api/v1/advisory/analyse`, {
        ticker,
        question: "What are the key funding and strategic options for this company?",
      });
      setAdvisory(res.data.analysis);
    } catch (e: any) {
      setAdvisory(`Error: ${e.message}`);
    } finally {
      setLoadingAdvisory(false);
    }
  };

  if (loading) return <div className="text-gray-400 animate-pulse">Loading {ticker}…</div>;
  if (error) return <div className="text-red-400">Error: {error}</div>;

  // Merge forecast scenarios for chart
  const forecastChart = forecast
    ? forecast.scenarios.base.map((row, i) => ({
        year: row.year,
        Base: row.revenue,
        Upside: forecast.scenarios.upside[i]?.revenue,
        Downside: forecast.scenarios.downside[i]?.revenue,
      }))
    : [];

  return (
    <div className="space-y-6">
      {/* Company Header */}
      {info && (
        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold">{info.name}</h2>
              <p className="text-gray-400">
                {info.sector} · {info.industry} · {info.country}
              </p>
            </div>
            <div className="text-right">
              <p className="text-xl font-semibold text-green-400">
                {info.currency} {fmt(info.market_cap)}
              </p>
              <p className="text-gray-500 text-sm">Market Cap</p>
            </div>
          </div>
          <p className="mt-3 text-gray-300 text-sm leading-relaxed line-clamp-3">
            {info.description}
          </p>
          {info.website && (
            <a
              href={info.website}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 text-sm mt-2 inline-block hover:underline"
            >
              {info.website}
            </a>
          )}
        </div>
      )}

      {/* Price Chart */}
      {prices.length > 0 && (
        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
          <h3 className="text-lg font-semibold mb-4">📈 Price History (60 trading days)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={prices}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" tick={{ fill: "#9CA3AF", fontSize: 10 }} tickCount={6} />
              <YAxis tick={{ fill: "#9CA3AF", fontSize: 10 }} width={60} />
              <Tooltip
                contentStyle={{ backgroundColor: "#1F2937", border: "none" }}
                labelStyle={{ color: "#F9FAFB" }}
              />
              <Line type="monotone" dataKey="close" stroke="#60A5FA" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Forecast */}
      {forecast && (
        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
          <h3 className="text-lg font-semibold mb-1">📊 Revenue Forecast (Base / Upside / Downside)</h3>
          <p className="text-gray-400 text-sm mb-4">
            Historical CAGR: {forecast.historical_cagr_pct}% · {forecast.disclaimer}
          </p>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={forecastChart}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="year" tick={{ fill: "#9CA3AF" }} />
              <YAxis tick={{ fill: "#9CA3AF", fontSize: 10 }} width={70} tickFormatter={(v) => fmt(v)} />
              <Tooltip
                contentStyle={{ backgroundColor: "#1F2937", border: "none" }}
                formatter={(v: number) => fmt(v)}
              />
              <Legend />
              <Bar dataKey="Base" fill="#60A5FA" />
              <Bar dataKey="Upside" fill="#34D399" />
              <Bar dataKey="Downside" fill="#F87171" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* AI Advisory */}
      <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
        <h3 className="text-lg font-semibold mb-3">🤖 AI Strategic Advisory (Google Gemini)</h3>
        <button
          onClick={fetchAdvisory}
          disabled={loadingAdvisory}
          className="px-5 py-2 bg-purple-700 hover:bg-purple-600 disabled:bg-gray-700 rounded-lg mb-4 transition-colors"
        >
          {loadingAdvisory ? "Analysing…" : "Generate Advisory"}
        </button>
        {advisory && (
          <div className="bg-gray-800 rounded-lg p-4 text-sm text-gray-200 whitespace-pre-wrap leading-relaxed">
            {advisory}
          </div>
        )}
      </div>
    </div>
  );
}
