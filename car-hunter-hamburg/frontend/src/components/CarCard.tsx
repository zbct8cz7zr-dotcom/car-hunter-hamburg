import { Link } from "react-router-dom";
import { Gauge, Fuel, MapPin, ChevronRight } from "lucide-react";
import type { Car } from "../types/car";
import { parseAiAnalysis } from "../types/car";
import ScoreStamp from "./ScoreStamp";

export default function CarCard({ car }: { car: Car }) {
  const analysis = parseAiAnalysis(car);
  return (
    <Link
      to={`/annonces/${car.id}`}
      className="w-full text-left bg-white border border-[#DEDACE] hover:border-navy transition-colors group block"
    >
      <div className="flex items-stretch">
        <div className="flex-1 p-4 min-w-0">
          <div className="flex items-baseline justify-between gap-2">
            <h3 className="font-semibold text-[15px] truncate text-navy">
              {car.brand} {car.model}
            </h3>
            {car.year && <span className="font-mono text-[13px] text-[#6B6558] shrink-0">{car.year}</span>}
          </div>

          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-2 text-[12.5px] text-[#4A463D]">
            <span className="inline-flex items-center gap-1">
              <Gauge size={13} strokeWidth={1.75} /> {car.mileage_km.toLocaleString("de-DE")} km
            </span>
            {car.fuel_type && (
              <span className="inline-flex items-center gap-1">
                <Fuel size={13} strokeWidth={1.75} /> {car.fuel_type}
              </span>
            )}
            {car.location && (
              <span className="inline-flex items-center gap-1">
                <MapPin size={13} strokeWidth={1.75} /> {car.location}
                {car.distance_from_hamburg_km != null ? ` · ${Math.round(car.distance_from_hamburg_km)} km` : ""}
              </span>
            )}
          </div>

          <div className="flex items-baseline gap-2 mt-3">
            <span className="font-mono text-xl font-bold text-ink">{car.price.toLocaleString("de-DE")} €</span>
          </div>
          {analysis && (
            <div className="text-[10px] uppercase tracking-[0.12em] mt-1.5 font-medium" style={{ color: "#6B6558" }}>
              {analysis.label}
            </div>
          )}
        </div>

        <div className="flex flex-col items-center justify-center gap-2 px-4 border-l border-[#EAE6DA] shrink-0">
          {car.score != null && <ScoreStamp score={car.score} />}
          <ChevronRight size={16} className="text-[#B5AF9E] group-hover:text-navy transition-colors" />
        </div>
      </div>
    </Link>
  );
}
