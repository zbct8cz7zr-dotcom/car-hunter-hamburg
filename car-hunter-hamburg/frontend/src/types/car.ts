export interface Car {
  id: number;
  source: string;
  brand: string;
  model: string;
  year: number | null;
  price: number;
  mileage_km: number;
  fuel_type: string | null;
  transmission: string | null;
  location: string | null;
  distance_from_hamburg_km: number | null;
  url: string;
  power_kw: number | null;
  owners_count: number | null;
  consumption_l_100km: number | null;
  image_url: string | null;
  score: number | null;
  ai_analysis: string | null; // JSON stringifié — voir parseAiAnalysis()
  is_active: boolean;
  date_added: string;
  date_last_seen: string;
}

export interface AiAnalysis {
  label: string;
  recommendation: string;
  strengths: string[];
  watch: string[];
}

export function parseAiAnalysis(car: Car): AiAnalysis | null {
  if (!car.ai_analysis) return null;
  try {
    return JSON.parse(car.ai_analysis) as AiAnalysis;
  } catch {
    return null;
  }
}

export interface CarListResponse {
  total: number;
  items: Car[];
}
