import { useState } from "react";
import type { FormEvent } from "react";
import { Search } from "lucide-react";

interface Props {
  onSubmit: (ticker: string) => void;
  loading?: boolean;
  placeholder?: string;
  defaultValue?: string;
}

export default function TickerInput({
  onSubmit,
  loading = false,
  placeholder = "Enter ticker symbol (e.g. AAPL)",
  defaultValue = "",
}: Props) {
  const [value, setValue] = useState(defaultValue);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const t = value.trim().toUpperCase();
    if (t) onSubmit(t);
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
        <input
          className="input-field pl-10"
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value.toUpperCase())}
          placeholder={placeholder}
          maxLength={10}
        />
      </div>
      <button type="submit" className="btn-primary" disabled={loading || !value.trim()}>
        {loading ? (
          <span className="flex items-center gap-2">
            <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            Loading…
          </span>
        ) : (
          "Analyze"
        )}
      </button>
    </form>
  );
}
