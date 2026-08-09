import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Listings from "./pages/Listings";
import CarDetail from "./pages/CarDetail";
import History from "./pages/History";
import SettingsPage from "./pages/Settings";
import NavBar from "./components/NavBar";

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex flex-col min-h-screen">
        <div className="flex-1">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/annonces" element={<Listings />} />
            <Route path="/annonces/:id" element={<CarDetail />} />
            <Route path="/historique" element={<History />} />
            <Route path="/parametres" element={<SettingsPage />} />
          </Routes>
        </div>
        <NavBar />
      </div>
    </BrowserRouter>
  );
}
