import { api } from "./client";
import type { UserSettings, UserSettingsUpdate } from "../types/settings";

export function fetchSettings(): Promise<UserSettings> {
  return api.get<UserSettings>("/api/settings");
}

export function updateSettings(update: UserSettingsUpdate): Promise<UserSettings> {
  return api.patch<UserSettings>("/api/settings", update);
}
