interface Props {
  label?: string;
}

export default function LoadingSpinner({ label = "Loading…" }: Props) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16">
      <div className="w-10 h-10 border-4 border-slate-700 border-t-brand-500 rounded-full animate-spin" />
      <p className="text-sm text-slate-400">{label}</p>
    </div>
  );
}
