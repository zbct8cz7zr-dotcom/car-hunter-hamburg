export interface UserSettings {
  id: number;
  budget_max: number;
  km_max: number;
  radius_km: number;
  fuel_types: string; // CSV, ex: "essence,hybride"
  favorite_brands: string; // CSV, ex: "toyota,honda"
  notify_email: boolean;
  notify_telegram: boolean;
  daily_summary_hour: number;
  instant_alert_score_threshold: number;
}

export type UserSettingsUpdate = Partial<Omit<UserSettings, "id">>;

export function csvToList(csv: string): string[] {
  return csv
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

export function listToCsv(list: string[]): string {
  return list.join(",");
}
