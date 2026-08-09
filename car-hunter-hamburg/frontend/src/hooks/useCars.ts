import { useEffect, useState, useCallback } from "react";
import type { Car } from "../types/car";
import type { UserSettings } from "../types/settings";
import { fetchCarsForSettings, type CarFilters } from "../api/cars";

export function useCars(settings: UserSettings | null, extra: CarFilters = {}) {
  const [cars, setCars] = useState<Car[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const extraKey = JSON.stringify(extra);

  const reload = useCallback(() => {
    if (!settings) return;
    setLoading(true);
    setError(null);
    fetchCarsForSettings(settings, JSON.parse(extraKey))
      .then((res) => {
        setCars(res.items);
        setTotal(res.total);
      })
      .catch((e) => setError(e.message ?? "Erreur de chargement des annonces"))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [settings, extraKey]);

  useEffect(() => {
    reload();
  }, [reload]);

  return { cars, total, loading, error, reload };
}
