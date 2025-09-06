import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";
import { SidebarProvider } from "@/components/ui/sidebar";

// The props interface is needed to accept the logout function from App.tsx
interface AppLayoutProps {
  onLogout: () => void;
}

export function AppLayout({ onLogout }: AppLayoutProps) {
  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-background">
        {/* The Sidebar is now correctly positioned on the left */}
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* The Header is now at the top of the main content area */}
          <Header onLogout={onLogout} />
          <main className="flex-1 p-6 overflow-y-auto">
            <Outlet />
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}

