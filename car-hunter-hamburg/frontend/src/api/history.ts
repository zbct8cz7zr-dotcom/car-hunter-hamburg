import { api } from "./client";
import type { Car } from "../types/car";

export interface PriceHistoryEntry {
  id: number;
  car_id: number;
  old_price: number;
  new_price: number;
  date: string;
  car_brand: string;
  car_model: string;
}

export function fetchPriceDrops(): Promise<PriceHistoryEntry[]> {
  return api.get<PriceHistoryEntry[]>("/api/history/price-drops");
}

export function fetchRemovedCars(): Promise<Car[]> {
  return api.get<Car[]>("/api/history/removed");
}
