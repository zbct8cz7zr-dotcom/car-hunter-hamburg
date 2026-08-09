import { api } from "./client";
import type { Car, CarListResponse } from "../types/car";
import type { UserSettings } from "../types/settings";

export interface CarFilters {
  budget_max?: number;
  km_max?: number;
  radius_km?: number;
  fuel_types?: string;
  brands?: string;
  min_score?: number;
  sort?: "score" | "price" | "mileage_km" | "date_added";
  order?: "asc" | "desc";
}

function filtersFromSettings(settings: UserSettings): CarFilters {
  return {
    budget_max: settings.budget_max,
    km_max: settings.km_max,
    radius_km: settings.radius_km,
    fuel_types: settings.fuel_types,
    brands: settings.favorite_brands,
  };
}

export function fetchCars(filters: CarFilters = {}): Promise<CarListResponse> {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== "") params.set(key, String(value));
  });
  const qs = params.toString();
  return api.get<CarListResponse>(`/api/cars${qs ? `?${qs}` : ""}`);
}

export function fetchCarsForSettings(settings: UserSettings, extra: CarFilters = {}): Promise<CarListResponse> {
  return fetchCars({ ...filtersFromSettings(settings), ...extra });
}

export function fetchCar(id: number): Promise<Car> {
  return api.get<Car>(`/api/cars/${id}`);
}

export function hideCar(id: number): Promise<{ status: string }> {
  return api.delete(`/api/cars/${id}`);
}

export interface ScrapeRunResult {
  new_listings: number;
  updated_prices: number;
  deactivated: number;
  blocked_sources: string[];
}

export function triggerScrape(): Promise<ScrapeRunResult> {
  return api.post<ScrapeRunResult>("/api/scrape/run");
}
