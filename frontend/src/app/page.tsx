"use client";

import { useState } from "react";
import { Search, Loader2, ArrowRight } from "lucide-react";

export default function Home() {
  const [company, setCompany] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showReport, setShowReport] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!company.trim()) return;
    
    setIsSubmitting(true);
    // Simulate API call
    setTimeout(() => {
      setIsSubmitting(false);
      setShowReport(true);
    }, 2000);
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-6 sm:p-24 relative overflow-hidden bg-slate-50 dark:bg-slate-950">
      {/* Decorative background elements */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-finance-400/10 rounded-full blur-3xl -z-10 animate-pulse" />
      <div className="absolute bottom-0 right-1/4 w-64 h-64 bg-finance-600/10 rounded-full blur-3xl -z-10" />

      {!showReport ? (
        <div className="flex-1 w-full flex flex-col items-center justify-center">
          <div className="w-full max-w-2xl text-center space-y-8 z-10">
            <header className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-700">
              <h1 className="text-4xl sm:text-6xl font-black tracking-tight text-slate-900 dark:text-slate-50">
                Finance <span className="text-finance-500">Copilot</span>
              </h1>
              <p className="text-lg sm:text-xl text-slate-500 dark:text-slate-400 font-medium max-w-lg mx-auto leading-relaxed">
                Automated corporate finance analysis for elite decision-making.
              </p>
            </header>

            <section className="animate-in fade-in slide-in-from-bottom-8 duration-700 delay-200">
              <form onSubmit={handleSubmit} className="group relative">
                <div className="absolute -inset-0.5 bg-gradient-to-r from-finance-400 to-finance-600 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200" />
                <div className="relative flex items-center bg-white dark:bg-slate-900 rounded-2xl p-1.5 shadow-2xl">
                  <div className="pl-4 text-slate-400"><Search className="w-5 h-5" /></div>
                  <input
                    type="text"
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                    placeholder="Enter company name (e.g. NVIDIA, Apple)..."
                    className="w-full bg-transparent border-none focus:ring-0 text-lg py-4 px-4 text-slate-700 dark:text-slate-200 placeholder:text-slate-400 outline-none"
                    disabled={isSubmitting}
                  />
                  <button
                    type="submit"
                    disabled={isSubmitting || !company.trim()}
                    className="flex items-center justify-center gap-2 bg-slate-900 dark:bg-slate-50 text-white dark:text-slate-900 px-6 py-4 rounded-xl font-bold transition-all active:scale-95 disabled:opacity-50 disabled:active:scale-100 group/btn overflow-hidden whitespace-nowrap"
                  >
                    {isSubmitting ? (
                      <><Loader2 className="w-5 h-5 animate-spin" /><span className="hidden sm:inline">Analysing...</span></>
                    ) : (
                      <><span className="hidden sm:inline">Generate Report</span><span className="sm:hidden">Go</span><ArrowRight className="w-5 h-5 group-hover/btn:translate-x-1 transition-transform" /></>
                    )}
                  </button>
                </div>
              </form>
              <div className="mt-8 flex flex-wrap justify-center gap-4 text-sm text-slate-400 animate-in fade-in duration-1000 delay-500">
                <span className="px-3 py-1 rounded-full border border-slate-200 dark:border-slate-800">SEC Filings Analysis</span>
                <span className="px-3 py-1 rounded-full border border-slate-200 dark:border-slate-800">Valuation Metrics</span>
                <span className="px-3 py-1 rounded-full border border-slate-200 dark:border-slate-800">Risk Assessment</span>
              </div>
            </section>
          </div>
        </div>
      ) : (
        <div className="w-full max-w-6xl space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
          <header className="flex items-center justify-between">
            <h2 className="text-3xl font-bold text-slate-900 dark:text-slate-50">
              Analysis: <span className="text-finance-500">{company}</span>
            </h2>
            <button 
              onClick={() => setShowReport(false)}
              className="text-sm font-medium text-slate-500 hover:text-slate-900 dark:hover:text-slate-100 transition-colors"
            >
              ← Back to search
            </button>
          </header>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column: Brand & Info */}
            <div className="lg:col-span-1 space-y-8">
              <section className="bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <span className="w-2 h-2 bg-blue-500 rounded-full" />
                  Brand & Positioning
                </h3>
                <div className="space-y-4 text-sm text-slate-600 dark:text-slate-400 italic">
                  Waiting for Ingestion Agent...
                </div>
              </section>

              <section className="bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <span className="w-2 h-2 bg-purple-500 rounded-full" />
                  Competitor Benchmarking
                </h3>
                <div className="space-y-4 text-sm text-slate-600 dark:text-slate-400 italic">
                  Identifying peers...
                </div>
              </section>
            </div>

            {/* Right Column: Multi-scenario & Advisory */}
            <div className="lg:col-span-2 space-y-8">
              <section className="bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800 min-h-[300px]">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full" />
                  Financial Forecast (Triple-Scenario)
                </h3>
                <div className="flex items-center justify-center h-48 text-sm text-slate-400 font-medium border-2 border-dashed border-slate-100 dark:border-slate-800 rounded-xl">
                  Charts will be rendered here
                </div>
              </section>

              <section className="bg-slate-900 text-white p-6 rounded-2xl shadow-xl dark:bg-slate-800">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <span className="w-2 h-2 bg-orange-500 rounded-full" />
                  Strategic Advisory
                </h3>
                <div className="space-y-4 text-sm text-slate-300 dark:text-slate-300 italic">
                  Reasoning over data...
                </div>
              </section>
            </div>
          </div>

          {/* Thinking Log Section */}
          <section className="bg-slate-100 dark:bg-slate-900/50 p-6 rounded-2xl border border-dashed border-slate-200 dark:border-slate-800">
            <h3 className="text-xs font-black uppercase tracking-widest text-slate-400 mb-4">
              Agent Thinking Log (Observability)
            </h3>
            <div className="font-mono text-[10px] text-slate-500 space-y-1">
              <p>[System] Initialising Director-Lead architecture...</p>
              <p className="animate-pulse">[Director] Waiting for ticker input...</p>
            </div>
          </section>
        </div>
      )}

      <footer className="mt-auto pt-12 flex flex-col items-center gap-3 text-center px-4 w-full z-10">
        <div className="px-4 py-2 rounded-lg bg-orange-50/50 dark:bg-orange-900/10 border border-orange-100 dark:border-orange-900/20 max-w-lg animate-in fade-in duration-1000 delay-700">
          <p className="text-[10px] sm:text-xs font-semibold text-orange-800 dark:text-orange-300 leading-relaxed">
            Educational Purpose Only • Not Financial Advice • All outputs are demonstrations, not recommendations.
          </p>
        </div>
        <p className="uppercase tracking-[0.2em] text-[10px] text-slate-400 font-bold">
          © 2026 Finance Copilot AI
        </p>
      </footer>
    </main>
  );
}
