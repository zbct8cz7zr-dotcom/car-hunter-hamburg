const TIERS = [
  { min: 95, color: "#3F6B4E" },
  { min: 90, color: "#3F6B4E" },
  { min: 80, color: "#C8842E" },
  { min: 70, color: "#C8842E" },
  { min: 0, color: "#A8442F" },
];

export function tierColorFor(score: number): string {
  return TIERS.find((t) => score >= t.min)!.color;
}

export default function ScoreStamp({ score, size = "md" }: { score: number; size?: "md" | "lg" }) {
  const color = tierColorFor(score);
  const big = size === "lg";
  return (
    <div
      className={`inline-flex flex-col items-center justify-center border-2 rotate-[-2deg] ${
        big ? "px-4 py-2" : "px-3 py-1.5"
      }`}
      style={{ borderColor: color, color }}
    >
      <span className={`font-mono font-bold tracking-tight ${big ? "text-3xl" : "text-xl"}`}>{score}</span>
      <span className="font-mono text-[9px] tracking-[0.15em] leading-none mt-0.5">/100</span>
    </div>
  );
}
