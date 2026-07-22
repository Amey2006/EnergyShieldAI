import React, { useState } from "react";
import { analyzeNews } from "../api";

export default function NewsTestInput() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleAnalyze() {
    if (!text.trim()) return;
    setLoading(true);
    try {
      const data = await analyzeNews(text);
      setResult(data);
    } catch (e) {
      setResult({ error: e.message });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <textarea
        className="news-test"
        placeholder="Paste a news paragraph to test corridor tagging, sentiment, and RAG retrieval..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button className="analyze-btn" onClick={handleAnalyze} disabled={loading}>
        {loading ? "Analyzing..." : "Analyze"}
      </button>

      {result && !result.error && (
        <div style={{ marginTop: 12 }}>
          <div className="stat-row">
            <span className="label">Corridor</span>
            <span className="value">{result.corridor}</span>
          </div>
          <div className="stat-row">
            <span className="label">Sentiment score</span>
            <span className="value">{result.sentiment_score}</span>
          </div>
          <div className="stat-row">
            <span className="label">Disruption keywords</span>
            <span className="value">{result.disruption_keywords.join(", ") || "none"}</span>
          </div>
          {result.related_existing_context?.length > 0 && (
            <div style={{ marginTop: 8 }}>
              <div className="corridor-name" style={{ marginBottom: 6 }}>Related existing context</div>
              {result.related_existing_context.map((r, i) => (
                <div className="news-item" key={i}>{r.text.slice(0, 160)}...</div>
              ))}
            </div>
          )}
        </div>
      )}
      {result?.error && <div className="empty-state">Error: {result.error}</div>}
    </div>
  );
}
