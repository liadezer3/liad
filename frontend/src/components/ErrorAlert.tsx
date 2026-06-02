import { AlertTriangle } from "lucide-react";

interface Props {
  message: string;
}

export default function ErrorAlert({ message }: Props) {
  return (
    <div className="flex items-start gap-3 bg-red-900/20 border border-red-800/50 rounded-xl p-4 text-red-300">
      <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
      <p className="text-sm">{message}</p>
    </div>
  );
}
