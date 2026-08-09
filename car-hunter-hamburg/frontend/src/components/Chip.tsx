import { Check } from "lucide-react";
import type { ReactNode } from "react";

export default function Chip({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="text-[12.5px] px-3 py-1.5 border font-medium transition-colors inline-flex items-center gap-1.5"
      style={{
        borderColor: active ? "#152A44" : "#DEDACE",
        backgroundColor: active ? "#152A44" : "white",
        color: active ? "#F5F3EE" : "#6B6558",
      }}
    >
      {active && <Check size={12} />}
      {children}
    </button>
  );
}
