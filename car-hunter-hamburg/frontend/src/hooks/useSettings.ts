import { useEffect, useState, useCallback } from "react";
import type { UserSettings, UserSettingsUpdate } from "../types/settings";
import { fetchSettings, updateSettings } from "../api/settings";

export function useSettings() {
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(() => {
    setLoading(true);
    setError(null);
    fetchSettings()
      .then(setSettings)
      .catch((e) => setError(e.message ?? "Erreur de chargement des critères"))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  const save = useCallback(async (update: UserSettingsUpdate) => {
    const updated = await updateSettings(update);
    setSettings(updated);
    return updated;
  }, []);

  return { settings, loading, error, reload, save };
}
