"use client";

import { useState, useEffect } from "react";
import { SearchBox } from "@/components/SearchBox";
import { PriceChart } from "@/components/PriceChart";
import { FinancialsView } from "@/components/FinancialsView";
import { Loader2, Globe, TrendingUp, ShieldAlert, BarChart3, Database } from "lucide-react";

export default function Home() {
  const [ticker, setTicker] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showReport, setShowReport] = useState(false);
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [isBriefExpanded, setIsBriefExpanded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const fetchAnalysis = async (tickerSymbol: string) => {
    setIsLoading(true);
    setError(null);
    setShowReport(true); // Move to dashboard immediately
    
    try {
      const response = await fetch(`http://localhost:8000/api/v1/company/${tickerSymbol}/analysis`);
      const data = await response.json();
      
      if (data.status === "ready") {
        setAnalysisData(data);
      } else if (data.status === "processing") {
        // If it's processing but we have some company data (from fast phase), show it!
        if (data.company) {
          setAnalysisData(data);
        } else {
          setAnalysisData({ status: "processing", ticker: tickerSymbol });
        }
        // Auto-poll after 3 seconds for faster updates during fast phase
        setTimeout(() => fetchAnalysis(tickerSymbol), 3000);
      }
    } catch (err) {
      console.error("Failed to fetch analysis:", err);
      setError("Failed to connect to backend");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelect = (selected: { ticker: string; name: string }) => {
    setTicker(selected.ticker);
    fetchAnalysis(selected.ticker);
  };

  const formatMarketCap = (cap: number | null) => {
    if (!cap) return "N/A";
    return `$${(cap / 1e9).toFixed(1)}B`;
  };

  if (!mounted) return null;

  return (
    <main className="flex min-h-screen flex-col items-center p-6 sm:p-24 relative overflow-hidden bg-slate-50 dark:bg-slate-950">
      {/* Decorative background elements */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-finance-400/10 rounded-full blur-3xl -z-10 animate-pulse" />
      <div className="absolute bottom-0 right-1/4 w-64 h-64 bg-finance-600/10 rounded-full blur-3xl -z-10" />

      {!showReport ? (
        <div className="flex-1 w-full flex flex-col items-center justify-center">
          <div className="w-full max-w-2xl text-center space-y-8 z-30">
            <header className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-700">
              <h1 className="text-4xl sm:text-6xl font-black tracking-tight text-slate-900 dark:text-slate-50">
                Finance <span className="text-finance-500">Copilot</span>
              </h1>
              <p className="text-lg sm:text-xl text-slate-500 dark:text-slate-400 font-medium max-w-lg mx-auto leading-relaxed">
                Automated corporate finance analysis for elite decision-making.
              </p>
            </header>

            <section className="animate-in fade-in slide-in-from-bottom-8 duration-700 delay-200 w-full">
              <div className="max-w-xl mx-auto">
                <SearchBox onSelect={handleSelect} disabled={isLoading} />
                {isLoading && (
                  <div className="mt-4 flex items-center justify-center gap-2 text-sm text-slate-500">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Initializing Agentic Ingestion...
                  </div>
                )}
                {error && <p className="mt-4 text-red-500 text-sm font-medium">{error}</p>}
              </div>

              <div className="mt-8 flex flex-wrap justify-center gap-4 text-sm text-slate-400 animate-in fade-in duration-1000 delay-500">
                <span className="px-3 py-1 rounded-full border border-slate-200 dark:border-slate-800">SEC Filings Analysis</span>
                <span className="px-3 py-1 rounded-full border border-slate-200 dark:border-slate-800">Valuation Metrics</span>
                <span className="px-3 py-1 rounded-full border border-slate-200 dark:border-slate-800">Risk Assessment</span>
                <span className="px-3 py-1 rounded-full border border-slate-200 dark:border-slate-800">Peer Comparison</span>
              </div>
            </section>
          </div>
        </div>
      ) : (
        <div className="w-full max-w-6xl space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
          <header className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              {analysisData?.company?.logo_url && (
                <div className="w-20 h-20 rounded-2xl bg-white dark:bg-slate-900 shadow-xl p-2 border border-slate-100 dark:border-slate-800 flex items-center justify-center overflow-hidden">
                  <img 
                    src={analysisData.company.logo_url.startsWith('http') 
                      ? analysisData.company.logo_url 
                      : `http://localhost:8000${analysisData.company.logo_url}`} 
                    alt={ticker} 
                    className="max-w-full max-h-full object-contain" 
                  />
                </div>
              )}
              <div className="space-y-1">
                <div className="flex items-center gap-3">
                  <h2 className="text-3xl font-bold text-slate-900 dark:text-slate-50 flex items-center gap-3">
                    <span className="text-finance-500">{ticker}</span>
                    {analysisData?.company?.name && (
                      <span className="text-slate-400 font-normal text-xl opacity-60">| {analysisData.company.name}</span>
                    )}
                  </h2>
                  {analysisData?.company?.sector && (
                    <span className="px-2.5 py-1 rounded-md bg-finance-100 dark:bg-finance-900/30 text-finance-600 dark:text-finance-400 text-[10px] font-black uppercase tracking-widest border border-finance-200 dark:border-finance-800/50">
                      {analysisData.company.sector}
                    </span>
                  )}
                  {analysisData?.company?.industry && (
                    <span className="px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 text-[10px] font-black uppercase tracking-widest border border-slate-200 dark:border-slate-700/50">
                      {analysisData.company.industry}
                    </span>
                  )}
                  {analysisData?.company?.website && (
                    <a 
                      href={analysisData.company.website} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-slate-400 hover:text-finance-500"
                    >
                      <Globe className="w-5 h-5" />
                    </a>
                  )}
                </div>
                {analysisData?.company?.mission && (
                  <p className="text-sm italic text-slate-500 dark:text-slate-400 font-medium max-w-2xl leading-relaxed">
                    "{analysisData.company.mission}"
                  </p>
                )}
              </div>
            </div>
            <button 
              onClick={() => { setShowReport(false); setAnalysisData(null); }}
              className="text-sm font-medium text-slate-500 hover:text-slate-900 dark:hover:text-slate-100 transition-colors"
            >
              ← Back to search
            </button>
          </header>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 relative">
            {/* Status indicator for background ingestion */}
            {analysisData?.status === "processing" && (
              <div className="absolute top-0 right-0 -mt-10 flex items-center gap-2 px-3 py-1.5 bg-finance-50 dark:bg-finance-900/20 border border-finance-100 dark:border-finance-800 rounded-full animate-in fade-in duration-500">
                <Loader2 className="w-3.5 h-3.5 text-finance-500 animate-spin" />
                <span className="text-[10px] font-bold text-finance-600 dark:text-finance-400 uppercase tracking-wider">Agents are fetching deep data...</span>
              </div>
            )}

            {/* Left Column: Brand & Market Stats */}
            <div className="lg:col-span-1 space-y-8">
              <section className="bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <Globe className="w-4 h-4 text-blue-500" />
                  Business Brief
                </h3>
                <div className="prose prose-sm dark:prose-invert">
                  {!analysisData?.company?.description ? (
                    <div className="space-y-2 animate-pulse">
                      <div className="h-3 w-full bg-slate-100 dark:bg-slate-800 rounded" />
                      <div className="h-3 w-5/6 bg-slate-100 dark:bg-slate-800 rounded" />
                    </div>
                  ) : (
                    <>
                      <p className="text-slate-600 dark:text-slate-400 text-[11px] leading-relaxed">
                        {isBriefExpanded 
                          ? analysisData?.company?.description 
                          : (analysisData?.company?.description?.length > 300 
                              ? `${analysisData.company.description.substring(0, 300)}...` 
                              : analysisData?.company?.description) || "Description not available."}
                      </p>
                      {analysisData?.company?.description?.length > 300 && (
                        <button 
                          onClick={() => setIsBriefExpanded(!isBriefExpanded)}
                          className="mt-2 text-[10px] font-bold text-finance-500 hover:text-finance-600 uppercase tracking-wider flex items-center gap-1"
                        >
                          {isBriefExpanded ? "Show Less ↑" : "Read More ↓"}
                        </button>
                      )}
                    </>
                  )}
                </div>
              </section>

              <section className="bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800">
                <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-green-500" />
                  Key Valuation Stats
                </h3>
                <div className="space-y-4">
                  <StatRow label="Market Cap" value={analysisData?.company?.market_cap ? formatMarketCap(analysisData.company.market_cap) : "..."} />
                  <StatRow label="Enterprise Value" value={analysisData?.company?.enterprise_value ? formatMarketCap(analysisData.company.enterprise_value) : "..."} />
                  <StatRow label="Shares Out." value={analysisData?.company?.shares_outstanding ? `${(analysisData.company.shares_outstanding / 1e9).toFixed(2)}B` : "..."} />
                  <StatRow label="Industry" value={analysisData?.company?.industry || "..."} />
                </div>
              </section>

              <section className="bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <span className="text-orange-500 flex items-center gap-1">🏢 Peer Universe</span>
                </h3>
                <div className="space-y-3">
                  {analysisData?.competitors?.length ? (
                    analysisData.competitors.map((peer: any) => (
                      <div key={peer.peer_ticker} className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors group">
                        <div className="flex flex-col">
                          <span className="text-xs font-bold text-slate-800 dark:text-slate-200">{peer.peer_ticker}</span>
                          <span className="text-[10px] text-slate-500 truncate max-w-[120px]">{peer.peer_name}</span>
                        </div>
                        <span className="text-[10px] font-mono text-slate-400 group-hover:text-finance-500 transition-colors">
                          {formatMarketCap(peer.market_cap)}
                        </span>
                      </div>
                    ))
                  ) : (
                    analysisData?.status === "processing" ? (
                      <div className="flex items-center gap-2 text-[10px] text-slate-400 italic py-2 animate-pulse">
                        <Loader2 className="w-2.5 h-2.5 animate-spin" /> Identifying peers...
                      </div>
                    ) : (
                      <p className="text-[10px] text-slate-400 italic">No direct peers identified yet.</p>
                    )
                  )}
                </div>
              </section>

              <section className="bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 text-purple-500" />
                  Risk Assessment (SEC)
                </h3>
                <div className="prose prose-sm dark:prose-invert max-h-96 overflow-y-auto pr-2 custom-scrollbar">
                  {!analysisData?.sec_insights?.risk_factors ? (
                    <div className="flex flex-col items-center justify-center py-12 text-center gap-3 animate-pulse">
                      <Database className="w-8 h-8 text-slate-200 dark:text-slate-800" />
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Searching SEC Filings...</p>
                    </div>
                  ) : (
                    <p className="text-slate-600 dark:text-slate-400 whitespace-pre-wrap text-[11px] leading-relaxed">
                      {analysisData.sec_insights.risk_factors}
                    </p>
                  )}
                </div>
              </section>
            </div>

            {/* Right Column: Financials & Charts */}
            <div className="lg:col-span-2 space-y-8">
              <section className="bg-white dark:bg-slate-900 p-6 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-800 overflow-hidden min-h-[400px] flex flex-col justify-center">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-green-500" />
                  Stock Price History (5Y)
                </h3>
                {analysisData?.status === "processing" && (!analysisData.prices || analysisData.prices.length === 0) ? (
                  <div className="flex-1 flex flex-col items-center justify-center py-24 gap-4 animate-in fade-in zoom-in duration-1000">
                    <div className="p-4 bg-finance-50 dark:bg-finance-900/20 rounded-full">
                      <Loader2 className="w-10 h-10 text-finance-500 animate-spin" />
                    </div>
                    <span className="text-sm font-bold text-slate-400 uppercase tracking-widest">Building chart...</span>
                  </div>
                ) : (analysisData?.prices?.length > 0 ? (
                  <PriceChart data={analysisData.prices} ticker={ticker} />
                ) : (
                  <div className="flex-1 flex flex-col items-center justify-center py-24 text-slate-400 italic">
                    No price history available.
                  </div>
                ))}
              </section>

              <section className="bg-white dark:bg-slate-900 p-6 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-800 min-h-[400px] flex flex-col justify-center">
                <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-orange-500" />
                  Financial Statements
                </h3>
                {analysisData?.status === "processing" && (!analysisData.financials || analysisData.financials.length === 0) ? (
                  <div className="flex-1 flex flex-col items-center justify-center py-24 gap-4 animate-in fade-in zoom-in duration-1000">
                    <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-full">
                      <Loader2 className="w-10 h-10 text-orange-500 animate-spin" />
                    </div>
                    <span className="text-sm font-bold text-slate-400 uppercase tracking-widest">Processing financials...</span>
                  </div>
                ) : (analysisData?.financials?.length > 0 ? (
                  <FinancialsView data={analysisData.financials} />
                ) : (
                  <div className="flex-1 flex flex-col items-center justify-center py-24 text-slate-400 italic">
                    No financial statements identified.
                  </div>
                ))}
              </section>
            </div>
          </div>

          {/* Thinking Log Section */}
          <section className="bg-slate-100 dark:bg-slate-900/50 p-6 rounded-2xl border border-dashed border-slate-200 dark:border-slate-800">
            <h3 className="text-xs font-black uppercase tracking-widest text-slate-400 mb-4">
              Agent Thinking Log (Observability)
            </h3>
            <div className="font-mono text-[10px] text-slate-500 space-y-1">
              <p>[System] Analysis fetched from database...</p>
              <p>[Ingestion] Structured phase OK (PostgreSQL)</p>
              <p>[Ingestion] Unstructured phase OK (ChromaDB)</p>
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

const StatRow = ({ label, value }: { label: string; value: string | null }) => (
  <div className="flex justify-between items-center py-2 border-b border-slate-50 dark:border-slate-800/50 last:border-0">
    <span className="text-sm text-slate-500">{label}</span>
    <span className="text-sm font-bold text-slate-800 dark:text-slate-200 tabular-nums">{value}</span>
  </div>
);
