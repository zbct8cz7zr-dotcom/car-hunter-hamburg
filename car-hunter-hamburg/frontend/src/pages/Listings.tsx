import { useState } from "react";
import { useSettings } from "../hooks/useSettings";
import { useCars } from "../hooks/useCars";
import CarCard from "../components/CarCard";

const SORTS: { key: "score" | "price" | "mileage_km"; label: string }[] = [
  { key: "score", label: "Score" },
  { key: "price", label: "Prix" },
  { key: "mileage_km", label: "Km" },
];

export default function Listings() {
  const { settings, loading: settingsLoading, error: settingsError, reload: reloadSettings } = useSettings();
  const [sort, setSort] = useState<"score" | "price" | "mileage_km">("score");
  const order = sort === "price" || sort === "mileage_km" ? "asc" : "desc";
  const { cars, total, loading, error } = useCars(settings, { sort, order });

  return (
    <div className="min-h-screen bg-paper text-ink pb-20">
      <header className="px-5 pt-6 pb-4 text-paper bg-navy">
        <h1 className="text-xl font-bold tracking-tight">Annonces</h1>
        <p className="text-[11.5px] opacity-70 mt-1">
          {total} annonce{total !== 1 ? "s" : ""} correspondant à tes critères
        </p>
      </header>

      <main className="px-5 py-5 max-w-2xl mx-auto">
        <div className="flex justify-end gap-1 mb-3">
          {SORTS.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => setSort(key)}
              className="text-[11px] px-2.5 py-1 border font-mono uppercase tracking-wide transition-colors"
              style={{
                borderColor: sort === key ? "#152A44" : "#DEDACE",
                backgroundColor: sort === key ? "#152A44" : "white",
                color: sort === key ? "#F5F3EE" : "#6B6558",
              }}
            >
              {label}
            </button>
          ))}
        </div>

        {settingsLoading ? (
          <p className="text-[13px] text-[#9A9483] text-center py-8">Chargement…</p>
        ) : settingsError ? (
          <div className="bg-white border border-bad p-6 text-center">
            <p className="text-[13px] text-bad mb-3">
              Impossible de joindre le serveur : {settingsError}
            </p>
            <button
              onClick={reloadSettings}
              className="text-[12.5px] font-medium px-3 py-1.5 border border-bad text-bad"
            >
              Réessayer
            </button>
          </div>
        ) : loading ? (
          <p className="text-[13px] text-[#9A9483] text-center py-8">Chargement…</p>
        ) : error ? (
          <p className="text-[13px] text-bad text-center py-8">{error}</p>
        ) : cars.length === 0 ? (
          <div className="bg-white border border-dashed border-[#DEDACE] p-8 text-center">
            <p className="text-[13.5px] text-[#6B6558]">Aucune annonce ne correspond à ces critères.</p>
          </div>
        ) : (
          <div className="space-y-2.5">
            {cars.map((car) => (
              <CarCard key={car.id} car={car} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
