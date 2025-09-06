import { useState } from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

// Import Pages and Layouts
import { AppLayout } from "./components/layout/AppLayout";
import Dashboard from "./pages/Dashboard";
import ProjectDetail from "./pages/ProjectDetail";
import NotFound from "./pages/NotFound";
import LoginPage from "./pages/Login";

const queryClient = new QueryClient();

// This is a wrapper for your protected routes
const ProtectedRoutes = () => {
  // Check for the auth token in localStorage
  const isAuthenticated = !!localStorage.getItem('authToken');

  // If the user is authenticated, render the AppLayout which contains the main app.
  // The AppLayout will use an <Outlet> from react-router-dom to render the nested routes.
  // If not authenticated, redirect them to the /login page.
  return isAuthenticated ? <AppLayout /> : <Navigate to="/login" />;
};


function App() {
  // This state is crucial to trigger a re-render when the auth status changes.
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(
    !!localStorage.getItem("authToken")
  );

  const handleLoginSuccess = (token: string) => {
    localStorage.setItem("authToken", token);
    setIsAuthenticated(true);
  };

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            {/* The Login route is now aware of the authentication state */}
            <Route
              path="/login"
              element={
                isAuthenticated ? (
                  // If the user is authenticated, redirect them from /login to the main dashboard
                  <Navigate to="/" />
                ) : (
                  // Otherwise, show the LoginPage
                  <LoginPage onLoginSuccess={handleLoginSuccess} />
                )
              }
            />

            {/* All main application routes are now children of the ProtectedRoutes element */}
            <Route path="/" element={<ProtectedRoutes />}>
              <Route index element={<Dashboard />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="projects/:id" element={<ProjectDetail />} />
            </Route>

            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;

