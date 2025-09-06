import { useState } from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate, Outlet } from "react-router-dom";

// Import Pages and Layouts
import { AppLayout } from "./components/layout/AppLayout";
import Dashboard from "./pages/Dashboard";
import ProjectDetail from "./pages/ProjectDetail";
import NotFound from "./pages/NotFound";
import LoginPage from "./pages/Login";

const queryClient = new QueryClient();

// A component to define the structure of authenticated routes
const ProtectedLayout = ({ onLogout }: { onLogout: () => void }) => (
  <AppLayout onLogout={onLogout}>
    <Outlet />
  </AppLayout>
);

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(
    !!localStorage.getItem("authToken")
  );

  const handleLoginSuccess = (token: string) => {
    localStorage.setItem("authToken", token);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem("authToken");
    setIsAuthenticated(false);
  };

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            {isAuthenticated ? (
              // If authenticated, all routes are rendered within the protected layout
              <Route path="/*" element={<AppLayout onLogout={handleLogout} />}>
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="projects/:id" element={<ProjectDetail />} />
                {/* Default route for authenticated users */}
                <Route index element={<Navigate to="/dashboard" replace />} />
                {/* Redirect from login if already authenticated */}
                <Route path="login" element={<Navigate to="/dashboard" replace />} />
                 {/* Fallback for any other authenticated routes */}
                <Route path="*" element={<NotFound />} />
              </Route>
            ) : (
              // If not authenticated, only login is available
              <>
                <Route
                  path="/login"
                  element={<LoginPage onLoginSuccess={handleLoginSuccess} />}
                />
                {/* Any other path redirects to login */}
                <Route path="*" element={<Navigate to="/login" replace />} />
              </>
            )}
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
