import type { LucideIcon } from "lucide-react";

export default function StatCard({
  icon: Icon,
  label,
  value,
  accent,
}: {
  icon: LucideIcon;
  label: string;
  value: string | number;
  accent: string;
}) {
  return (
    <div className="bg-white border border-[#DEDACE] p-4 flex items-start gap-3">
      <Icon size={20} strokeWidth={1.75} style={{ color: accent }} className="mt-0.5 shrink-0" />
      <div>
        <div className="font-mono text-2xl font-bold leading-none text-ink">{value}</div>
        <div className="text-[11px] uppercase tracking-[0.1em] text-[#6B6558] mt-1.5">{label}</div>
      </div>
    </div>
  );
}
