import { useEffect, useState } from "react";
import { useSettings } from "../hooks/useSettings";
import Chip from "../components/Chip";
import { csvToList, listToCsv } from "../types/settings";

const ALL_FUELS = ["essence", "hybride", "diesel", "électrique"];
const ALL_BRANDS = ["toyota", "honda", "mazda", "hyundai", "kia", "volkswagen", "skoda"];

export default function SettingsPage() {
  const { settings, loading, save } = useSettings();
  const [budgetMax, setBudgetMax] = useState(10000);
  const [kmMax, setKmMax] = useState(150000);
  const [radiusKm, setRadiusKm] = useState(100);
  const [fuels, setFuels] = useState<string[]>([]);
  const [brands, setBrands] = useState<string[]>([]);
  const [notifyEmail, setNotifyEmail] = useState(true);
  const [notifyTelegram, setNotifyTelegram] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (!settings) return;
    setBudgetMax(settings.budget_max);
    setKmMax(settings.km_max);
    setRadiusKm(settings.radius_km);
    setFuels(csvToList(settings.fuel_types));
    setBrands(csvToList(settings.favorite_brands));
    setNotifyEmail(settings.notify_email);
    setNotifyTelegram(settings.notify_telegram);
  }, [settings]);

  const toggle = (list: string[], setList: (l: string[]) => void, val: string) => {
    setList(list.includes(val) ? list.filter((v) => v !== val) : [...list, val]);
  };

  const handleSave = async () => {
    await save({
      budget_max: budgetMax,
      km_max: kmMax,
      radius_km: radiusKm,
      fuel_types: listToCsv(fuels),
      favorite_brands: listToCsv(brands),
      notify_email: notifyEmail,
      notify_telegram: notifyTelegram,
    });
    setSaved(true);
    setTimeout(() => setSaved(false), 1500);
  };

  if (loading) return <p className="text-center py-10 text-[13px] text-[#9A9483]">Chargement…</p>;

  return (
    <div className="min-h-screen bg-paper text-ink pb-20">
      <header className="px-5 pt-6 pb-4 text-paper bg-navy">
        <h1 className="text-xl font-bold tracking-tight">Critères de recherche</h1>
      </header>

      <main className="p-5 max-w-2xl mx-auto space-y-6">
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-[11px] uppercase tracking-[0.15em] text-[#6B6558]">Budget maximum</label>
            <span className="font-mono text-[15px] font-bold text-navy">{budgetMax.toLocaleString("de-DE")} €</span>
          </div>
          <input
            type="range" min={2000} max={25000} step={500}
            value={budgetMax}
            onChange={(e) => setBudgetMax(Number(e.target.value))}
            className="w-full accent-navy"
          />
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-[11px] uppercase tracking-[0.15em] text-[#6B6558]">Kilométrage maximum</label>
            <span className="font-mono text-[15px] font-bold text-navy">{kmMax.toLocaleString("de-DE")} km</span>
          </div>
          <input
            type="range" min={20000} max={250000} step={5000}
            value={kmMax}
            onChange={(e) => setKmMax(Number(e.target.value))}
            className="w-full accent-navy"
          />
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-[11px] uppercase tracking-[0.15em] text-[#6B6558]">Rayon autour de Hambourg</label>
            <span className="font-mono text-[15px] font-bold text-navy">{radiusKm} km</span>
          </div>
          <input
            type="range" min={5} max={200} step={5}
            value={radiusKm}
            onChange={(e) => setRadiusKm(Number(e.target.value))}
            className="w-full accent-navy"
          />
        </div>

        <div>
          <label className="text-[11px] uppercase tracking-[0.15em] text-[#6B6558] block mb-2">Carburant</label>
          <div className="flex flex-wrap gap-2">
            {ALL_FUELS.map((f) => (
              <Chip key={f} active={fuels.includes(f)} onClick={() => toggle(fuels, setFuels, f)}>
                {f}
              </Chip>
            ))}
          </div>
        </div>

        <div>
          <label className="text-[11px] uppercase tracking-[0.15em] text-[#6B6558] block mb-2">Marques favorites</label>
          <div className="flex flex-wrap gap-2">
            {ALL_BRANDS.map((b) => (
              <Chip key={b} active={brands.includes(b)} onClick={() => toggle(brands, setBrands, b)}>
                {b}
              </Chip>
            ))}
          </div>
        </div>

        <div>
          <label className="text-[11px] uppercase tracking-[0.15em] text-[#6B6558] block mb-2">Notifications</label>
          <div className="flex flex-wrap gap-2">
            <Chip active={notifyEmail} onClick={() => setNotifyEmail(!notifyEmail)}>Email</Chip>
            <Chip active={notifyTelegram} onClick={() => setNotifyTelegram(!notifyTelegram)}>Telegram</Chip>
          </div>
        </div>

        <button
          onClick={handleSave}
          className="w-full py-3 font-medium tracking-wide uppercase text-[13px] bg-navy text-paper"
        >
          {saved ? "Enregistré ✓" : "Enregistrer les critères"}
        </button>
      </main>
    </div>
  );
}
