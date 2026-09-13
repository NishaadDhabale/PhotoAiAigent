import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import AppLayout from "./components/layout/AppLayout";
import DuplicatesPage from "./pages/DuplicatesPage";
import PhotosPage from "./pages/PhotosPage";
import PeoplePage from "./pages/PeoplePage";
import TimelinePage from "./pages/TimelinePage";
import PlacesPage from "./pages/PlacesPage";
import AgentPage from "./pages/AgentPage";
import OrganizationPage from "./pages/OrganizationPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Navigate to="/photos" replace />} />
          <Route path="/duplicates" element={<DuplicatesPage />} />
          <Route path="/photos" element={<PhotosPage />} />
          <Route path="/people" element={<PeoplePage />} />
          <Route path="/timeline" element={<TimelinePage />} />
          <Route path="/places" element={<PlacesPage />} />
          <Route path="/agent" element={<AgentPage />} />
          <Route path="/organization" element={<OrganizationPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}