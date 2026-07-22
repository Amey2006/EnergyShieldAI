import React from "react";

function sentimentTag(score) {
  if (score > 0.2) return { label: "positive", color: "#3ecf8e" };
  if (score < -0.2) return { label: "negative", color: "#e5484d" };
  return { label: "neutral", color: "#8b98a3" };
}

export default function NewsFeed({ news }) {
  const articles = news?.articles || [];

  if (articles.length === 0) {
    return <div className="empty-state">No news yet — start orchestrator.py</div>;
  }

  return (
    <div style={{ maxHeight: 340, overflowY: "auto" }}>
      {articles.slice(0, 20).map((a, i) => {
        const sentiment = sentimentTag(a.sentiment_score);
        return (
          <div className="news-item" key={i}>
            <div>{a.title}</div>
            <div className="meta">
              <span className="tag">{a.corridor}</span>
              <span className="tag" style={{ color: sentiment.color, borderColor: sentiment.color }}>
                {sentiment.label}
              </span>
              {a.source} · {a.published}
            </div>
          </div>
        );
      })}
    </div>
  );
}
