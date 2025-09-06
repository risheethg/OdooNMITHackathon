import { useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { 
  LayoutDashboard, 
  FolderOpen, 
  Users, 
  Settings,
  Plus,
  Bell,
  BarChartHorizontal,
  ChevronLeft,
  ChevronRight
} from "lucide-react";
import {
  Sidebar as SidebarPrimitive,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarTrigger,
  useSidebar,
} from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";

const navigationItems = [
  { title: "Dashboard", url: "/", icon: LayoutDashboard },
  { title: "Analytics", url: "/analytics", icon: BarChartHorizontal },
  { title: "Projects", url: "/projects", icon: FolderOpen },
  { title: "Team", url: "/team", icon: Users },
  { title: "Settings", url: "/settings", icon: Settings },
];

export function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const location = useLocation();
  const currentPath = location.pathname;

  const isActive = (path: string) => currentPath === path;
  const getNavClasses = ({ isActive }: { isActive: boolean }) =>
    isActive 
      ? "bg-primary text-primary-foreground font-medium shadow-md" 
      : "hover:bg-muted/50 text-muted-foreground hover:text-foreground";

  return (
    <SidebarPrimitive className={`${isCollapsed ? "w-16" : "w-64"} border-r bg-card transition-all duration-300`}>
      <div className="p-4 border-b">
        <div className="flex items-center gap-3">
          {!isCollapsed && (
            <>
              <div className="w-8 h-8 primary-gradient rounded-lg flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-sm">S</span>
              </div>
              <div>
                <h2 className="font-bold text-lg text-foreground">SynergySphere</h2>
                <p className="text-xs text-muted-foreground">Team Collaboration</p>
              </div>
            </>
          )}
          {isCollapsed && (
            <div className="w-8 h-8 primary-gradient rounded-lg flex items-center justify-center mx-auto">
              <span className="text-primary-foreground font-bold text-sm">S</span>
            </div>
          )}
        </div>
      </div>

      <SidebarContent className="p-4">
        {!isCollapsed && (
          <Button className="w-full mb-6 primary-gradient text-primary-foreground hover:opacity-90 shadow-md">
            <Plus className="w-4 h-4 mr-2" />
            New Project
          </Button>
        )}
        
        <SidebarGroup>
          <SidebarGroupLabel className="text-xs uppercase tracking-wider text-muted-foreground mb-2">
            Navigation
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navigationItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild className="mb-1">
                    <NavLink 
                      to={item.url} 
                      end 
                      className={({ isActive }) => 
                        `flex items-center px-3 py-2 rounded-lg transition-all duration-200 ${getNavClasses({ isActive })}`
                      }
                    >
                      <item.icon className="w-5 h-5 mr-3 flex-shrink-0" />
                      {!isCollapsed && <span className="font-medium">{item.title}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <div className="p-4 border-t mt-auto">
        <Button 
          variant="ghost" 
          size="icon"
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="w-full"
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </Button>
      </div>
    </SidebarPrimitive>
  );
}