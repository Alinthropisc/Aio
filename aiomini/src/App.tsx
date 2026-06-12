import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { HomePage } from "./pages/Home";
import { SettingsPage } from "./pages/Settings";
import { NotificationsPage } from "./pages/Notifications";
import { BottomNav } from "./components/BottomNav";

export function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen flex-col">
        <div className="flex-1 overflow-y-auto pb-16">
          <Routes>
            <Route path="/" element={<Navigate to="/home" replace />} />
            <Route path="/home" element={<HomePage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/notifications" element={<NotificationsPage />} />
          </Routes>
        </div>
        <BottomNav />
      </div>
    </BrowserRouter>
  );
}
