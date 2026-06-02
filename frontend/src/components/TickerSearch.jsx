import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client.js";
import { useTicker } from "../context/TickerContext.jsx";
import { fmtPct } from "../utils/format.js";

export default function TickerSearch({ autoFocus = false }) {
  const [input, setInput] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const { loadTicker, loading, error } = useTicker();
  const navigate = useNavigate();

  useEffect(() => {
    api
      .directory()
      .then(setSuggestions)
      .catch(() => setSuggestions([]));
  }, []);

  const go = async (sym) => {
    const target = (sym || input).trim().toUpperCase();
    if (!target) return;
    const data = await loadTicker(target);
    if (data) navigate(`/overview/${target}`);
  };

  return (
    <div>
      <form
        className="search-box"
        onSubmit={(e) => {
          e.preventDefault();
          go();
        }}
      >
        <input
          autoFocus={autoFocus}
          placeholder="Enter a ticker symbol (e.g. JNJ, KO, MSFT)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          aria-label="Ticker symbol"
        />
        <button className="btn" type="submit" disabled={loading || !input.trim()}>
          {loading ? "Loading…" : "Evaluate"}
        </button>
      </form>

      {error && <div className="error" style={{ marginTop: "0.8rem" }}>{error}</div>}

      {suggestions.length > 0 && (
        <>
          <p className="muted" style={{ margin: "1rem 0 0.2rem", fontSize: "0.82rem" }}>
            Try a sample dividend grower:
          </p>
          <div className="chips">
            {suggestions.map((s) => (
              <button
                key={s.ticker}
                className="chip"
                type="button"
                onClick={() => go(s.ticker)}
                title={`${s.name} · yield ${fmtPct(s.dividend_yield)}`}
              >
                {s.ticker} · {fmtPct(s.dividend_yield)}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
