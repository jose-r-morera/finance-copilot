"use client";

import { useState, useEffect, useRef } from "react";
import { Search, Loader2 } from "lucide-react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface Company {
  ticker: string;
  name: string;
  cik: string;
}

interface SearchBoxProps {
  onSelect: (company: Company) => void;
  disabled?: boolean;
}

export function SearchBox({ onSelect, disabled }: SearchBoxProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Company[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(async () => {
      if (query.trim().length < 1) {
        setResults([]);
        setIsOpen(false);
        return;
      }

      setIsLoading(true);
      try {
        const url = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/search/companies?q=${encodeURIComponent(query)}&limit=5`;
        const res = await fetch(url);
        if (res.ok) {
          const data = await res.json();
          setResults(data);
          setIsOpen(true);
          setSelectedIndex(0); // Default to first match
        }
      } catch (error) {
        console.error("Search failed:", error);
      } finally {
        setIsLoading(false);
      }
    }, 200);

    return () => clearTimeout(timer);
  }, [query]);

  // Click outside listener
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      setSelectedIndex(prev => Math.min(prev + 1, results.length - 1));
    } else if (e.key === "ArrowUp") {
      setSelectedIndex(prev => Math.max(prev - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (selectedIndex >= 0 && results[selectedIndex]) {
        onSelect(results[selectedIndex]);
        setIsOpen(false);
        setQuery(results[selectedIndex].ticker);
      } else if (results.length > 0) {
        onSelect(results[0]);
        setIsOpen(false);
        setQuery(results[0].ticker);
      }
    } else if (e.key === "Escape") {
      setIsOpen(false);
    }
  };

  return (
    <div className="relative w-full group" ref={containerRef}>
      <div className="absolute -inset-0.5 bg-gradient-to-r from-finance-400 to-finance-600 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200" />
      <div className="relative flex items-center bg-white dark:bg-slate-900 rounded-2xl p-1.5 shadow-2xl">
        <div className="pl-4 text-slate-400">
          {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
        </div>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => query.length > 0 && setIsOpen(true)}
          placeholder="Search company (e.g. NVIDIA, Apple)..."
          className="w-full bg-transparent border-none focus:ring-0 text-lg py-4 px-4 text-slate-700 dark:text-slate-200 placeholder:text-slate-400 outline-none"
          disabled={disabled}
        />
      </div>

      {/* Autocomplete Results */}
      {isOpen && results.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-2 p-1 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border border-white/20 dark:border-slate-800 rounded-2xl shadow-2xl z-[100] overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
          {results.map((company, index) => (
            <button
              key={company.ticker}
              className={cn(
                "w-full text-left px-4 py-3 rounded-xl transition-all duration-200 flex items-center justify-between group/item",
                selectedIndex === index
                  ? "bg-finance-500 text-white shadow-lg"
                  : "hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300"
              )}
              onClick={() => {
                onSelect(company);
                setQuery(company.ticker);
                setIsOpen(false);
              }}
              onMouseEnter={() => setSelectedIndex(index)}
            >
              <div className="flex flex-col">
                <span className="font-bold tracking-tight">{company.name}</span>
                <span className={cn(
                  "text-xs font-mono uppercase opacity-70",
                  selectedIndex === index ? "text-white" : "text-finance-500"
                )}>
                  {company.ticker}
                </span>
              </div>
              <div className={cn(
                "opacity-0 group-hover/item:opacity-100 transition-opacity",
                selectedIndex === index ? "text-white" : "text-slate-400"
              )}>
                CIK: {company.cik}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
