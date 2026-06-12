"use client";

import { NavLink } from "react-router-dom";
import { Home, Settings, Bell } from "lucide-react";

const links = [
  { to: "/home", icon: Home, label: "Home" },
  { to: "/notifications", icon: Bell, label: "Notifications" },
  { to: "/settings", icon: Settings, label: "Settings" },
];

export function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 border-t bg-background pb-[env(safe-area-inset-bottom)]">
      <div className="flex justify-around py-2">
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex flex-col items-center gap-0.5 px-4 py-1 text-xs transition-colors ${
                isActive ? "text-primary" : "text-muted-foreground"
              }`
            }
          >
            <Icon size={22} />
            {label}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
