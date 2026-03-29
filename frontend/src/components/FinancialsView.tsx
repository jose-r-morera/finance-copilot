"use client";

import { useState } from "react";

interface FinancialStatement {
  fiscal_year: number;
  period: string;
  revenue: number | null;
  net_income: number | null;
  total_assets: number | null;
  total_liabilities: number | null;
  operating_cash_flow: number | null;
  all_metrics: any;
}

interface FinancialsViewProps {
  data: FinancialStatement[];
}

export const FinancialsView = ({ data }: FinancialsViewProps) => {
  const [activeTab, setActiveTab] = useState<"IS" | "BS" | "CF">("IS");

  const formatValue = (val: number | null) => {
    if (val === null) return "-";
    const abs = Math.abs(val);
    if (abs >= 1e9) return (val / 1e9).toFixed(2) + "B";
    if (abs >= 1e6) return (val / 1e6).toFixed(2) + "M";
    return val.toLocaleString();
  };

  const years = data.map(d => d.fiscal_year).sort((a, b) => a - b);

  return (
    <div className="space-y-6">
      <div className="flex border-b border-slate-200 dark:border-slate-800">
        {(["IS", "BS", "CF"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-bold transition-colors relative ${
              activeTab === tab ? "text-finance-500" : "text-slate-500 hover:text-slate-900 dark:hover:text-slate-100"
            }`}
          >
            {tab === "IS" ? "Income" : tab === "BS" ? "Balance Sheet" : "Cash Flow"}
            {activeTab === tab && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-finance-500 animate-in fade-in slide-in-from-bottom-1" />
            )}
          </button>
        ))}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="text-slate-400 font-medium border-b border-slate-100 dark:border-slate-800">
              <th className="py-3 px-4">Metric (USD)</th>
              {years.map(year => (
                <th key={year} className="py-3 px-4 text-right">{year}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50 dark:divide-slate-800/50">
            {activeTab === "IS" && (
              <>
                <MetricRow label="Total Revenue" field="revenue" data={data} years={years} formatValue={formatValue} />
                <MetricRow label="Net Income" field="net_income" data={data} years={years} formatValue={formatValue} />
              </>
            )}
            {activeTab === "BS" && (
              <>
                <MetricRow label="Total Assets" field="total_assets" data={data} years={years} formatValue={formatValue} />
                <MetricRow label="Total Liabilities" field="total_liabilities" data={data} years={years} formatValue={formatValue} />
              </>
            )}
            {activeTab === "CF" && (
              <>
                <MetricRow label="Operating Cash Flow" field="operating_cash_flow" data={data} years={years} formatValue={formatValue} />
              </>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const MetricRow = ({ label, field, data, years, formatValue }: any) => (
  <tr className="hover:bg-slate-50 dark:hover:bg-slate-900/50 transition-colors">
    <td className="py-3 px-4 font-semibold text-slate-700 dark:text-slate-300">{label}</td>
    {years.map((year: number) => {
      const yearData = data.find((d: any) => d.fiscal_year === year);
      return (
        <td key={year} className="py-3 px-4 text-right tabular-nums">
          {formatValue(yearData?.[field])}
        </td>
      );
    })}
  </tr>
);
