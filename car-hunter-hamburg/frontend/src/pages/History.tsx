import { useEffect, useState } from "react";
import { TrendingDown, TrendingUp, EyeOff } from "lucide-react";
import { fetchPriceDrops, fetchRemovedCars, type PriceHistoryEntry } from "../api/history";
import type { Car } from "../types/car";

export default function History() {
  const [entries, setEntries] = useState<PriceHistoryEntry[]>([]);
  const [removed, setRemoved] = useState<Car[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchPriceDrops(), fetchRemovedCars()])
      .then(([e, r]) => {
        setEntries(e);
        setRemoved(r);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-paper text-ink pb-20">
      <header className="px-5 pt-6 pb-4 text-paper bg-navy">
        <h1 className="text-xl font-bold tracking-tight">Historique</h1>
        <p className="text-[11.5px] opacity-70 mt-1">Évolution des prix et annonces retirées</p>
      </header>

      <main className="p-5 max-w-2xl mx-auto space-y-6">
        {loading ? (
          <p className="text-[13px] text-[#9A9483] text-center py-8">Chargement…</p>
        ) : (
          <>
            <section>
              <h2 className="text-[11px] uppercase tracking-[0.15em] text-[#6B6558] mb-3">Changements de prix récents</h2>
              {entries.length === 0 ? (
                <p className="text-[13px] text-[#9A9483]">
                  Aucun changement de prix pour l'instant — reviens après quelques cycles de scraping.
                </p>
              ) : (
                <div className="space-y-2">
                  {entries.map((e) => {
                    const dropped = e.new_price < e.old_price;
                    return (
                      <div key={e.id} className="bg-white border border-[#DEDACE] p-3 flex items-center justify-between">
                        <div>
                          <div className="text-[13.5px] font-medium text-navy">
                            {e.car_brand} {e.car_model}
                          </div>
                          <div className="text-[11px] text-[#9A9483] mt-0.5">
                            {new Date(e.date).toLocaleDateString("fr-FR")}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-mono text-[11px] text-[#9A9483] line-through">
                            {e.old_price.toLocaleString("de-DE")} €
                          </div>
                          <div
                            className={`font-mono text-[14px] font-bold flex items-center gap-1 ${
                              dropped ? "text-good" : "text-bad"
                            }`}
                          >
                            {dropped ? <TrendingDown size={13} /> : <TrendingUp size={13} />}
                            {e.new_price.toLocaleString("de-DE")} €
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </section>

            <section>
              <h2 className="text-[11px] uppercase tracking-[0.15em] text-[#6B6558] mb-3">Annonces retirées récemment</h2>
              {removed.length === 0 ? (
                <p className="text-[13px] text-[#9A9483]">Aucune annonce retirée détectée pour l'instant.</p>
              ) : (
                <div className="space-y-2">
                  {removed.map((car) => (
                    <div key={car.id} className="bg-white border border-[#DEDACE] p-3 flex items-center gap-3">
                      <EyeOff size={15} className="text-[#9A9483] shrink-0" />
                      <div className="min-w-0">
                        <div className="text-[13.5px] font-medium text-navy truncate">
                          {car.brand} {car.model}
                        </div>
                        <div className="text-[11px] text-[#9A9483]">
                          Dernier prix : {car.price.toLocaleString("de-DE")} €
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </>
        )}
      </main>
    </div>
  );
}
