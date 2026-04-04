"use client";

import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from "recharts";
import { TrendingUp, TrendingDown, Minus, Info, Calculator, Layers } from "lucide-react";

interface ForecastData {
    status: string;
    ticker: string;
    scenarios: any[];
}

export const ForecastView = ({ ticker }: { ticker: string }) => {
    const [data, setData] = useState<ForecastData | null>(null);
    const [loading, setLoading] = useState(true);
    const [selectedScenario, setSelectedScenario] = useState("BASE");
    const [sensitivity, setSensitivity] = useState<any>(null);

    useEffect(() => {
        let isMounted = true;
        let timeoutId: NodeJS.Timeout;

        const fetchData = async () => {
            if (!ticker) {
                if (isMounted) setLoading(false);
                return;
            }

            let shouldWait = false;
            try {
                const response = await fetch(`http://localhost:8000/api/v1/modeling/${ticker}/forecast`);
                if (response.ok) {
                    const result = await response.json();
                    if (isMounted) {
                        setData(result);

                        // If still processing, poll again in 3 seconds
                        if (result.status === "processing") {
                            shouldWait = true;
                            timeoutId = setTimeout(fetchData, 3000);
                        }
                    }
                }

                if (isMounted && !shouldWait) {
                    const sensResponse = await fetch(`http://localhost:8000/api/v1/modeling/${ticker}/sensitivity`);
                    if (sensResponse.ok) {
                        const sensResult = await sensResponse.json();
                        setSensitivity(sensResult);
                    }
                }
            } catch (error) {
                console.error("Failed to fetch forecast data", error);
            } finally {
                if (isMounted && !shouldWait) setLoading(false);
            }
        };

        setLoading(true);
        fetchData();

        return () => {
            isMounted = false;
            if (timeoutId) clearTimeout(timeoutId);
        };
    }, [ticker]);

    if (loading) return (
        <div className="flex flex-col items-center justify-center p-12 gap-4 animate-pulse">
            <Calculator className="w-12 h-12 text-slate-200" />
            <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Running Scenario Simulations...</span>
        </div>
    );

    if (!data || !data.scenarios || data.scenarios.length === 0) return (
        <div className="flex flex-col items-center justify-center p-12 gap-4 text-slate-400 italic">
            <Minus className="w-8 h-8 opacity-20" />
            <p className="text-sm">Modeling data unavailable for this ticker.</p>
        </div>
    );

    const currentScenario = data.scenarios.find(s => s.scenario_type === selectedScenario) || data.scenarios[0];

    const renderReasoningWithLinks = (text: string) => {
        if (!text) return null;
        const parts = text.split(/(\[.*?\]\(.*?\))/g);
        return parts.map((part, i) => {
            const match = part.match(/\[(.*?)\]\((.*?)\)/);
            if (match) {
                return (
                    <a
                        key={i}
                        href={match[2]}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-finance-500 hover:text-finance-600 underline font-medium"
                    >
                        {match[1]}
                    </a>
                );
            }
            return part;
        });
    };

    return (
        <div className="space-y-8 animate-in fade-in duration-700">
            {/* Fallback Banner */}
            {currentScenario.is_fallback && (
                <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/50 p-4 rounded-3xl flex items-center gap-4 text-amber-800 dark:text-amber-200 border-dashed">
                    <div className="p-2 bg-amber-100 dark:bg-amber-800/50 rounded-xl">
                        <Info size={18} className="text-amber-600 dark:text-amber-400" />
                    </div>
                    <div>
                        <p className="text-[10px] font-black uppercase tracking-[0.2em]">Deterministic Model Active</p>
                        <p className="text-[11px] opacity-70 leading-relaxed mt-0.5">The AI reasoning engine is currently offline. Showing standard projections based on 4-year historical trends.</p>
                    </div>
                </div>
            )}

            {/* Scenario Selector */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Layers className="w-4 h-4 text-finance-500" />
                    <h3 className="text-lg font-bold">Modeling Engine</h3>
                </div>
                <div className="flex p-1 bg-slate-100 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
                    {["BEAR", "BASE", "BULL"].map((s) => (
                        <button
                            key={s}
                            onClick={() => setSelectedScenario(s)}
                            className={`px-4 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-wider transition-all ${
                                selectedScenario === s
                                ? "bg-white dark:bg-slate-900 text-finance-600 shadow-sm"
                                : "text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
                            }`}
                        >
                            {s}
                        </button>
                    ))}
                </div>
            </div>

            {/* Valuation Card */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="md:col-span-1 bg-gradient-to-br from-finance-500 to-finance-700 p-6 rounded-3xl text-white shadow-xl shadow-finance-500/20 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
                        <Calculator size={80} />
                    </div>
                    <p className="text-[10px] font-bold uppercase tracking-[0.2em] opacity-80 mb-1">Intrinsic Value</p>
                    <h4 className="text-4xl font-black mb-4">
                        ${currentScenario.intrinsic_value?.toFixed(2) || "N/A"}
                    </h4>
                    <div className="space-y-3">
                        <div className="flex justify-between text-[11px] font-medium border-b border-white/10 pb-2">
                            <span className="opacity-70">WACC</span>
                            <span>{(currentScenario.wacc * 100).toFixed(1)}%</span>
                        </div>
                        <div className="flex justify-between text-[11px] font-medium border-b border-white/10 pb-2">
                            <span className="opacity-70">Terminal Growth</span>
                            <span>{(currentScenario.terminal_growth * 100).toFixed(1)}%</span>
                        </div>
                        <div className="flex justify-between text-[11px] font-medium">
                            <span className="opacity-70">Rev. Growth</span>
                            <span>{(currentScenario.revenue_growth * 100).toFixed(1)}%</span>
                        </div>
                    </div>
                </div>

                {/* Chart */}
                <div className="md:col-span-2 bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-100 dark:border-slate-800 shadow-sm min-h-[300px]">
                    <h5 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-6 flex items-center gap-2">
                        <TrendingUp className="w-3 h-3" />
                        5-Year Forecast: {selectedScenario}
                    </h5>
                    <ResponsiveContainer width="100%" height={240}>
                        <BarChart data={currentScenario.projections}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F020" />
                            <XAxis dataKey="year" fontSize={11} tickLine={false} axisLine={false} />
                            <YAxis fontSize={11} tickLine={false} axisLine={false} tickFormatter={(val) => `$${(val / 1e9).toFixed(1)}B`} />
                            <Tooltip
                                contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)', fontSize: '12px' }}
                                formatter={(val: any) => [`$${(val / 1e9).toFixed(2)}B`, ""]}
                            />
                            <Legend iconType="circle" />
                            <Bar dataKey="revenue" name="Revenue" fill="#6366f1" radius={[4, 4, 0, 0]} barSize={20} />
                            <Bar dataKey="ebitda" name="EBITDA" fill="#fb923c" radius={[4, 4, 0, 0]} barSize={20} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Sensitivity & Breakdown */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Sensitivity Matrix */}
                <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl border border-slate-100 dark:border-slate-800 shadow-sm">
                    <h5 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-6">Valuation Sensitivity (PV/Share)</h5>
                    {sensitivity && (
                        <div className="overflow-x-auto">
                            <table className="w-full text-[10px]">
                                <thead>
                                    <tr>
                                        <th className="p-2 border-b border-slate-50 dark:border-slate-800">Growth \ WACC</th>
                                        {sensitivity.wacc_labels.map((l: string) => (
                                            <th key={l} className="p-2 border-b border-slate-50 dark:border-slate-800 text-slate-500">{l}</th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {sensitivity.growth_labels.map((g: string, i: number) => (
                                        <tr key={g}>
                                            <td className="p-2 border-r border-slate-50 dark:border-slate-800 font-bold text-slate-500">{g}</td>
                                            {sensitivity.matrix.map((row: any, j: number) => {
                                                const cell = row[i];
                                                const isBase = j === 1 && i === 1;
                                                return (
                                                    <td key={j} className={`p-3 text-center transition-colors ${
                                                        isBase ? "bg-finance-500 text-white font-bold" : "hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300"
                                                    }`}>
                                                        ${cell.value}
                                                    </td>
                                                );
                                            })}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>

                {/* Analysis Notes */}
                <div className="bg-slate-50 dark:bg-slate-800/30 p-6 rounded-3xl border border-dashed border-slate-200 dark:border-slate-700">
                    <h5 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                        <Info size={14} />
                        Agent Reasoning & Context
                    </h5>
                    <div className="space-y-4 text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">
                        <div className="flex gap-3">
                            <div className="p-1.5 rounded-lg bg-finance-100 dark:bg-finance-900/30 text-finance-600 h-fit">
                                <Calculator size={12} />
                            </div>
                            <div>
                                <p className="font-bold text-slate-800 dark:text-slate-200 mb-1">Scenario Basis:</p>
                                <div className="whitespace-pre-wrap">
                                    {renderReasoningWithLinks(currentScenario.assumptions_reasoning) || "Standard historical extrapolation based on 4-year trend line."}
                                </div>
                            </div>
                            {currentScenario.modeling_thoughts && (
                                <div className="pt-2 border-t border-slate-200 dark:border-slate-800 mt-2">
                                    <p className="font-bold text-slate-800 dark:text-slate-200 mb-1">Analyst Thoughts:</p>
                                    <p className="italic text-slate-500 dark:text-slate-400">{currentScenario.modeling_thoughts}</p>
                                </div>
                            )}
                            {currentScenario.data_sources && currentScenario.data_sources.length > 0 && (
                                <div className="pt-2 border-t border-slate-200 dark:border-slate-800 mt-2">
                                    <p className="font-bold text-slate-800 dark:text-slate-200 mb-1 flex items-center gap-1 opacity-50 uppercase tracking-tighter">
                                        <Layers size={10} /> Core Sources
                                    </p>
                                    <div className="flex flex-wrap gap-2 mt-1">
                                        {currentScenario.data_sources.map((url: string, idx: number) => (
                                            <a
                                                key={idx}
                                                href={url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="px-2 py-0.5 bg-white dark:bg-slate-800 rounded border border-slate-100 dark:border-slate-700 text-[9px] font-bold hover:border-finance-300 hover:text-finance-600 transition-all text-slate-500"
                                            >
                                                SEC FILING #{idx + 1}
                                            </a>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                </div>
                </div>
            </div>
        </div>
    );
};
