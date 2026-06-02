import { FormEvent, useState } from "react";

type TickerSearchProps = {
  ticker: string;
  isLoading: boolean;
  onSearch: (ticker: string) => Promise<void>;
};

export function TickerSearch({ ticker, isLoading, onSearch }: TickerSearchProps) {
  const [value, setValue] = useState(ticker);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSearch(value);
  }

  return (
    <form className="ticker-search" onSubmit={handleSubmit}>
      <label htmlFor="ticker">Ticker symbol</label>
      <div>
        <input
          id="ticker"
          value={value}
          onChange={(event) => setValue(event.target.value.toUpperCase())}
          placeholder="MSFT"
          maxLength={8}
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? "Analyzing..." : "Analyze"}
        </button>
      </div>
      <p>Try MSFT, KO, JNJ, or any symbol with sample fallback data.</p>
    </form>
  );
}
