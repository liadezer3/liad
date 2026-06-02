import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Loader from "../components/Loader.jsx";
import ScoreGauge from "../components/ScoreGauge.jsx";
import { api } from "../api/client.js";
import { useActiveTicker } from "../hooks/useActiveTicker.js";
import { ratingClass, scoreColor } from "../utils/format.js";

function FactorBar({ factor }) {
  return (
    <div>
      <div className="factor">
        <span className="fname">{factor.name}</span>
        <div className="bar-track">
          <div
            className="bar-fill"
            style={{
              width: `${factor.score}%`,
              background: scoreColor(factor.score),
            }}
          />
        </div>
        <span className="fscore">{Math.round(factor.score)}</span>
        <span className="fdetail">
          {factor.detail}{" "}
          <span className="muted">· weight {Math.round(factor.weight * 100)}%</span>
        </span>
      </div>
    </div>
  );
}

export default function AnalysisPage() {
  const { detail, loading, error, symbol } = useActiveTicker();
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [analysisErr, setAnalysisErr] = useState(null);

  useEffect(() => {
    if (!detail) return;
    let cancelled = false;
    setBusy(true);
    setAnalysisErr(null);
    setResult(null);
    api
      .dividendSafety(detail.ticker)
      .then((r) => !cancelled && setResult(r))
      .catch((e) => !cancelled && setAnalysisErr(e.message))
      .finally(() => !cancelled && setBusy(false));
    return () => {
      cancelled = true;
    };
  }, [detail]);

  if (loading) return <div className="page"><Loader label={`Loading ${symbol}…`} /></div>;
  if (error)
    return (
      <div className="page">
        <div className="error">{error}</div>
        <p style={{ marginTop: "1rem" }}>
          <Link className="btn ghost" to="/">← Back to search</Link>
        </p>
      </div>
    );
  if (!detail) return <div className="page"><Loader /></div>;

  return (
    <div className="page">
      <div className="page-head">
        <span className="eyebrow">AI Analysis</span>
        <h1>Dividend-safety score · {detail.ticker}</h1>
        <p>
          An AI prompt layer reviews {detail.name}'s historical balance sheets and
          cash-flow trends to grade how safe — and sustainable — the dividend is.
        </p>
      </div>

      {busy && <Loader label="Analyzing balance sheets…" />}
      {analysisErr && <div className="error">{analysisErr}</div>}

      {result && (
        <>
          <div className="grid cols-2">
            <div
              className="card"
              style={{ display: "flex", alignItems: "center", gap: "1.4rem" }}
            >
              <ScoreGauge score={result.safety_score} />
              <div>
                <span className={`badge ${ratingClass(result.rating)}`}>
                  {result.rating}
                </span>
                <h3 style={{ margin: "0.6rem 0 0.3rem" }}>Dividend Safety</h3>
                <p className="muted" style={{ margin: 0, fontSize: "0.85rem" }}>
                  Engine:{" "}
                  <strong style={{ color: "var(--text)" }}>
                    {result.engine === "llm" ? `LLM (${result.model})` : "Heuristic model"}
                  </strong>
                </p>
              </div>
            </div>

            <div className="card">
              <h3 style={{ fontSize: "1rem" }}>Summary</h3>
              <p className="muted" style={{ marginBottom: 0 }}>{result.summary}</p>
            </div>
          </div>

          <div className="grid cols-2" style={{ marginTop: "1.1rem" }}>
            <div className="card">
              <h3 style={{ fontSize: "1rem" }}>
                <span className="badge good">Strengths</span>
              </h3>
              <ul className="feature-list">
                {result.strengths.map((s, i) => (
                  <li key={i}>
                    <span className="tick">✓</span>
                    <span>{s}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="card">
              <h3 style={{ fontSize: "1rem" }}>
                <span className="badge bad">Risks</span>
              </h3>
              <ul className="feature-list">
                {result.risks.map((r, i) => (
                  <li key={i}>
                    <span className="tick" style={{ color: "var(--danger)" }}>!</span>
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {result.factors.length > 0 && (
            <>
              <div className="section-title">
                <h2>Contributing factors</h2>
              </div>
              <div className="card">
                {result.factors.map((f, i) => (
                  <FactorBar key={i} factor={f} />
                ))}
              </div>
            </>
          )}
        </>
      )}

      <div className="row" style={{ marginTop: "1.6rem" }}>
        <Link className="btn ghost" to={`/overview/${detail.ticker}`}>← Overview</Link>
        <Link className="btn ghost" to={`/valuation/${detail.ticker}`}>Valuation</Link>
      </div>
    </div>
  );
}
