"use client";

import { useState } from "react";
import { Search, Loader2, ArrowRight } from "lucide-react";

export default function Home() {
  const [company, setCompany] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!company.trim()) return;
    
    setIsSubmitting(true);
    // TODO: Connect to backend API
    console.log("Generating report for:", company);
    
    // Simulate API call
    setTimeout(() => setIsSubmitting(false), 2000);
  };

  return (
    <main className="flex min-height-100vh flex-col items-center justify-center p-6 sm:p-24 relative overflow-hidden">
      {/* Decorative background elements */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-finance-400/10 rounded-full blur-3xl -z-10 animate-pulse" />
      <div className="absolute bottom-0 right-1/4 w-64 h-64 bg-finance-600/10 rounded-full blur-3xl -z-10" />

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
          <form 
            onSubmit={handleSubmit}
            className="group relative"
          >
            <div className="absolute -inset-0.5 bg-gradient-to-r from-finance-400 to-finance-600 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200" />
            
            <div className="relative flex items-center bg-white dark:bg-slate-900 rounded-2xl p-1.5 shadow-2xl">
              <div className="pl-4 text-slate-400">
                <Search className="w-5 h-5" />
              </div>
              
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
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span className="hidden sm:inline">Analysing...</span>
                  </>
                ) : (
                  <>
                    <span className="hidden sm:inline">Generate Report</span>
                    <span className="sm:hidden">Go</span>
                    <ArrowRight className="w-5 h-5 group-hover/btn:translate-x-1 transition-transform" />
                  </>
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

      <footer className="absolute bottom-8 text-slate-400 text-xs font-medium tracking-widest uppercase">
        © 2026 Finance Copilot AI
      </footer>
    </main>
  );
}
