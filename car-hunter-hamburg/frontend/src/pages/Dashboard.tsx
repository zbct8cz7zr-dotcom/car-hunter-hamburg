import { useState } from "react";
import { Ship, Sparkles, RefreshCw } from "lucide-react";
import { useSettings } from "../hooks/useSettings";
import { useCars } from "../hooks/useCars";
import StatCard from "../components/StatCard";
import CarCard from "../components/CarCard";
import { triggerScrape } from "../api/cars";

export default function Dashboard() {
  const { settings, loading: settingsLoading } = useSettings();
  const { cars, total, loading, error, reload } = useCars(settings, { sort: "score", order: "desc" });
  const [scraping, setScraping] = useState(false);
  const [scrapeMessage, setScrapeMessage] = useState<string | null>(null);

  const excellent = cars.filter((c) => (c.score ?? 0) >= 90).length;
  const avgPrice = cars.length ? Math.round(cars.reduce((s, c) => s + c.price, 0) / cars.length) : 0;
  const savings = cars.reduce((s, c) => {
    // Approximation : économie = écart entre prix moyen du lot et prix de l'annonce, si favorable
    return s + Math.max(0, avgPrice - c.price);
  }, 0);

  const handleScrape = async () => {
    setScraping(true);
    setScrapeMessage(null);
    try {
      const result = await triggerScrape();
      setScrapeMessage(
        `${result.new_listings} nouvelle(s), ${result.updated_prices} prix mis à jour` +
          (result.blocked_sources.length ? ` — ⚠ ${result.blocked_sources.length} source(s) bloquée(s)` : "")
      );
      reload();
    } catch (e) {
      setScrapeMessage("Erreur lors de l'actualisation");
    } finally {
      setScraping(false);
    }
  };

  return (
    <div className="min-h-screen bg-paper text-ink pb-16">
      <header className="px-5 pt-6 pb-5 text-paper bg-navy">
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-center gap-2">
            <Ship size={18} strokeWidth={1.75} />
            <span className="text-[10.5px] uppercase tracking-[0.2em] opacity-70">Hambourg · Manifeste du jour</span>
          </div>
          <button
            onClick={handleScrape}
            disabled={scraping}
            className="flex items-center gap-1.5 text-[11.5px] px-2.5 py-1.5 border border-white/30 hover:border-white/60 transition-colors disabled:opacity-50"
          >
            <RefreshCw size={13} className={scraping ? "animate-spin" : ""} /> Actualiser
          </button>
        </div>
        <h1 className="text-2xl font-bold tracking-tight">Car Hunter Hamburg</h1>

        <div className="grid grid-cols-2 gap-2.5 mt-5">
          <StatCard icon={Ship} label="Annonces actives" value={total} accent="#F5F3EE" />
          <StatCard icon={Sparkles} label="Opportunités ★" value={excellent} accent="#C8842E" />
        </div>
      </header>

      <main className="px-5 py-5 max-w-2xl mx-auto">
        {scrapeMessage && (
          <div className="text-[12.5px] bg-white border border-[#DEDACE] px-3.5 py-2.5 mb-4">{scrapeMessage}</div>
        )}

        <div className="flex items-center justify-between mb-3">
          <div className="bg-white border border-[#DEDACE] px-3.5 py-2 flex-1 mr-2.5">
            <div className="text-[9.5px] uppercase tracking-[0.1em] text-[#6B6558]">Économie potentielle</div>
            <div className="font-mono text-lg font-bold text-good">{savings.toLocaleString("de-DE")} €</div>
          </div>
          <div className="bg-white border border-[#DEDACE] px-3.5 py-2 flex-1">
            <div className="text-[9.5px] uppercase tracking-[0.1em] text-[#6B6558]">Prix moyen</div>
            <div className="font-mono text-lg font-bold text-navy">{avgPrice.toLocaleString("de-DE")} €</div>
          </div>
        </div>

        <h2 className="text-[11px] uppercase tracking-[0.15em] text-[#6B6558] mt-6 mb-3">Meilleures opportunités</h2>

        {settingsLoading || loading ? (
          <p className="text-[13px] text-[#9A9483] text-center py-8">Chargement…</p>
        ) : error ? (
          <p className="text-[13px] text-bad text-center py-8">{error}</p>
        ) : cars.length === 0 ? (
          <div className="bg-white border border-dashed border-[#DEDACE] p-8 text-center">
            <p className="text-[13.5px] text-[#6B6558]">
              Aucune annonce pour l'instant. Lance une actualisation ou vérifie tes critères.
            </p>
          </div>
        ) : (
          <div className="space-y-2.5">
            {cars.slice(0, 5).map((car) => (
              <CarCard key={car.id} car={car} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
