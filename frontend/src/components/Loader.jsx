export default function Loader({ label = "Loading…" }) {
  return (
    <div className="loader-wrap">
      <span className="loader" />
      <span>{label}</span>
    </div>
  );
}
