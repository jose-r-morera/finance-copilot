# Demo Video Script: Finance Copilot (3 Minutes)

**Total Estimated Time:** 180 Seconds
**Tone:** Professional, Technical, Narrative-driven.

---

### **0:00 - 0:30 | Introduction & The Problem**
**[Visual: Dashboard showing BBVA or AAPL data]**
"This is Finance Copilot. In high-stakes financial analysis, trust is the only currency. But most AI tools today provide projections as 'black boxes'—you get a number, but you don't know why or where it came from. For a DCF valuation, that's dangerous. We built Finance Copilot to solve the transparency gap in AI-driven modeling."

### **0:30 - 1:15 | The Pipeline: From SEC to Vector Store**
**[Visual: Switch to Terminal or Ingestion logs]**
"The magic starts with our pipeline. We don't just scrape; we ingest. Our engine targets the SEC EDGAR system specifically, pulling 10-Ks and 10-Qs. Crucially, we preserve metadata. Every chunk of text in our ChromaDB vector store knows exactly which filing it came from, documented down to the URL. This allows us to bridge the gap between raw data and AI reasoning."

### **1:15 - 2:00 | The Modeling Engine: Gemini 2.5 & RAG**
**[Visual: Close-up of the "Modeling Engine" card in UI]**
"When you run a forecast, our Modeling Agent (now upgraded to Gemini 2.5 Flash) uses RAG to pull context from those filings. It identifies growth drivers, margin risks, and terminal assumptions. Look here: the 'Analyst Thoughts' section shows you the AI’s step-by-step logic. And these 'Core Sources'? They aren't just names—they are clickable links that take you directly to the SEC filing used for that specific assumption."

### **2:00 - 2:40 | Resilience & Technical Architecture**
**[Visual: Code snippet of EmbeddingService or ModelingAgent fallback]**
"Technically, we've optimized for resilience. We have a hybrid LLM setup supporting Gemini and OpenAI. But more importantly, we bypass API instability with a local, GPU-accelerated embedding engine. If you're running this on an RTX 4070, like we are, the embeddings for thousands of pages happen locally and instantly. And if the AI is offline? Our system automatically triggers a deterministic fallback model, clearly marked in the UI, so the analyst is never left in the dark."

### **2:40 - 3:00 | Conclusion & Impact**
**[Visual: Full dashboard view]**
"Finance Copilot isn't just a calculator; it's a transparent partner. It gives analysts the speed of AI with the auditability of a traditional spreadsheet. By combining agentic reasoning with cited data sources, we're making AI-powered finance truly professional-grade. Thank you."

---
**Key Scenes to Film:**
1. Dashboard landing page.
2. The "Enriching Data" loading state.
3. Clicking a source link and seeing it open the SEC filing.
4. The "Analyst Thoughts" section.
5. (Optional) The "Deterministic Model Active" banner by disabling the API key.
