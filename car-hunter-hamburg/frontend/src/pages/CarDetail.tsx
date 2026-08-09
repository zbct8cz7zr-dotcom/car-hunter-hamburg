import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, ExternalLink, EyeOff } from "lucide-react";
import type { Car } from "../types/car";
import { parseAiAnalysis } from "../types/car";
import { fetchCar, hideCar } from "../api/cars";
import ScoreStamp, { tierColorFor } from "../components/ScoreStamp";

export default function CarDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [car, setCar] = useState<Car | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    fetchCar(Number(id))
      .then(setCar)
      .catch(() => setError("Annonce introuvable"))
      .finally(() => setLoading(false));
  }, [id]);

  const handleHide = async () => {
    if (!car) return;
    await hideCar(car.id);
    navigate("/annonces");
  };

  if (loading) return <p className="text-center py-10 text-[13px] text-[#9A9483]">Chargement…</p>;
  if (error || !car) return <p className="text-center py-10 text-[13px] text-bad">{error ?? "Erreur"}</p>;

  const analysis = parseAiAnalysis(car);
  const tierColor = car.score != null ? tierColorFor(car.score) : "#6B6558";

  return (
    <div className="min-h-screen bg-paper text-ink pb-16">
      <div className="sticky top-0 bg-navy text-paper px-5 py-4 flex items-center gap-3 z-10">
        <button onClick={() => navigate(-1)} className="opacity-80 hover:opacity-100">
          <ArrowLeft size={20} />
        </button>
        <div className="min-w-0">
          <div className="text-[10px] uppercase tracking-[0.15em] opacity-70">Fiche véhicule</div>
          <h1 className="text-lg font-semibold truncate">
            {car.brand} {car.model} {car.year ? `· ${car.year}` : ""}
          </h1>
        </div>
      </div>

      <div className="p-5 max-w-2xl mx-auto space-y-5">
        <div className="flex items-center justify-between">
          {car.score != null ? <ScoreStamp score={car.score} size="lg" /> : <span />}
          <div className="text-right">
            <div className="font-mono text-2xl font-bold text-ink">{car.price.toLocaleString("de-DE")} €</div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-2 text-center">
          {[
            ["Kilométrage", `${car.mileage_km.toLocaleString("de-DE")} km`],
            ["Carburant", car.fuel_type ?? "—"],
            ["Boîte", car.transmission ?? "—"],
          ].map(([label, val]) => (
            <div key={label} className="bg-white border border-[#DEDACE] py-2.5 px-1">
              <div className="font-mono text-[13px] font-semibold text-navy">{val}</div>
              <div className="text-[9.5px] uppercase tracking-[0.1em] text-[#6B6558] mt-1">{label}</div>
            </div>
          ))}
        </div>

        {analysis && analysis.strengths.length > 0 && (
          <div>
            <div className="text-[11px] uppercase tracking-[0.15em] font-medium mb-2 text-good">Points forts</div>
            <ul className="space-y-1.5">
              {analysis.strengths.map((s, i) => (
                <li key={i} className="text-[13.5px] flex gap-2 text-ink">
                  <span className="text-good">✓</span> {s}
                </li>
              ))}
            </ul>
          </div>
        )}

        {analysis && analysis.watch.length > 0 && (
          <div>
            <div className="text-[11px] uppercase tracking-[0.15em] font-medium mb-2 text-amber">À surveiller</div>
            <ul className="space-y-1.5">
              {analysis.watch.map((w, i) => (
                <li key={i} className="text-[13.5px] flex gap-2 text-ink">
                  <span className="text-amber">⚠</span> {w}
                </li>
              ))}
            </ul>
          </div>
        )}

        {analysis && (
          <div className="border-2 px-4 py-3 flex items-center justify-between" style={{ borderColor: tierColor }}>
            <span className="font-mono text-[13px] font-bold tracking-wide" style={{ color: tierColor }}>
              {analysis.label}
            </span>
          </div>
        )}

        <div className="flex gap-2 pt-2">
          <a
            href={car.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 flex items-center justify-center gap-2 py-3 bg-navy text-paper font-medium text-[13px] uppercase tracking-wide"
          >
            Voir l'annonce <ExternalLink size={15} />
          </a>
          <button
            onClick={handleHide}
            className="px-4 py-3 border border-[#DEDACE] text-[#6B6558] hover:border-bad hover:text-bad transition-colors"
            title="Masquer cette annonce"
          >
            <EyeOff size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
