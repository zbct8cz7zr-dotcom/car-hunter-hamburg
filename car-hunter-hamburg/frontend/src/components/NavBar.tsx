import { NavLink } from "react-router-dom";
import { LayoutDashboard, List, SlidersHorizontal, History } from "lucide-react";

const TABS = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/annonces", label: "Annonces", icon: List, end: false },
  { to: "/historique", label: "Historique", icon: History, end: false },
  { to: "/parametres", label: "Critères", icon: SlidersHorizontal, end: false },
];

export default function NavBar() {
  return (
    <nav className="sticky bottom-0 bg-navy text-paper border-t border-white/10 flex">
      {TABS.map(({ to, label, icon: Icon, end }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          className={({ isActive }) =>
            `flex-1 flex flex-col items-center gap-1 py-2.5 text-[10.5px] uppercase tracking-wide transition-opacity ${
              isActive ? "opacity-100" : "opacity-55"
            }`
          }
        >
          <Icon size={18} strokeWidth={1.75} />
          {label}
        </NavLink>
      ))}
    </nav>
  );
}
