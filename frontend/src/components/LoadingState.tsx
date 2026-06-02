type LoadingStateProps = {
  message?: string;
};

export function LoadingState({ message = "Loading analysis..." }: LoadingStateProps) {
  return (
    <div className="loading-card" role="status">
      <div className="spinner" aria-hidden="true" />
      <p>{message}</p>
    </div>
  );
}
