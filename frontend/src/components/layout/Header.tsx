import { useEffect } from "react";
import { Bell, Search, User, LogOut, Settings } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import axios, { AxiosError } from 'axios';

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

// Define the User type to match your backend's Pydantic model
interface UserData {
  _id: string;
  username: string;
  email: string;
  is_active: boolean;
}

// Interface to define the props the component accepts
interface HeaderProps {
  onLogout: () => void;
}

// Data fetching function for react-query to get the current user
const fetchCurrentUser = async (): Promise<UserData> => {
    const token = localStorage.getItem("authToken");
    if (!token) {
        // This will cause the query to fail if no token is found
        throw new Error("No authentication token found.");
    }

    const response = await axios.get('http://127.0.0.1:8000/auth/users/me', {
        headers: {
            // Include the JWT token in the Authorization header
            Authorization: `Bearer ${token}`
        }
    });
    
    // The actual user object is nested inside the `data` property of your ResponseModel
    return response.data.data;
};

// Helper function to generate initials from a username for the Avatar
const getInitials = (name: string = "") => {
    // Takes the first character of the first word.
    return name.charAt(0).toUpperCase() || 'U';
};

export function Header({ onLogout }: HeaderProps) {
    const { data: user, isLoading, isError, error } = useQuery<UserData, AxiosError>({
        queryKey: ['currentUser'], // A unique key for this query in react-query cache
        queryFn: fetchCurrentUser,
        staleTime: 1000 * 60 * 15, // Cache user data for 15 minutes
        retry: 1, // Only retry the request once on failure
    });
    
    // This effect listens for authentication errors from the query.
    // If the token is invalid (401), it logs the user out automatically.
    useEffect(() => {
        if (isError && error.response?.status === 401) {
            onLogout();
        }
    }, [isError, error, onLogout]);

    // --- RENDER LOGIC ---

    // 1. Loading State
    if (isLoading) {
        return (
            <header className="border-b bg-card px-6 py-4">
                <div className="flex items-center justify-between">
                    <div className="relative max-w-md w-full flex-1">
                       {/* Placeholder for search */}
                    </div>
                    <div className="flex items-center gap-3">
                        <Skeleton className="h-9 w-9 rounded-full" />
                        <div className="flex items-center gap-2">
                          <Skeleton className="h-10 w-10 rounded-full" />
                          <div className="hidden sm:block">
                              <Skeleton className="h-4 w-24" />
                              <Skeleton className="h-3 w-32 mt-1" />
                          </div>
                        </div>
                    </div>
                </div>
            </header>
        );
    }
    
    // 2. Error State
    if (isError) {
        return (
             <header className="border-b bg-card px-6 py-4">
               <div className="flex items-center justify-end w-full">
                  <p className="text-sm text-destructive mr-4">Session expired.</p>
                  <Button onClick={onLogout} variant="destructive">Login Again</Button>
               </div>
             </header>
        );
    }
    
    // 3. Success State
    return (
        <header className="border-b bg-card px-6 py-4">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4 flex-1">
                    <div className="relative max-w-md w-full">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                        <Input
                            placeholder="Search projects, tasks, or team members..."
                            className="pl-10 bg-muted/50 border-0 focus:bg-background"
                        />
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <Button variant="ghost" size="icon" className="relative">
                        <Bell className="w-5 h-5" />
                        <Badge variant="destructive" className="absolute -top-1 -right-1 w-5 h-5 p-0 flex items-center justify-center text-xs">3</Badge>
                    </Button>

                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="flex items-center gap-2 px-2 h-auto py-1">
                                <Avatar className="w-8 h-8">
                                    <AvatarImage src="" alt={user?.username} />
                                    <AvatarFallback className="bg-primary text-primary-foreground text-sm">
                                        {getInitials(user?.username)}
                                    </AvatarFallback>
                                </Avatar>
                                <div className="text-left hidden sm:block">
                                    <p className="text-sm font-medium capitalize">{user?.username || 'User'}</p>
                                    <p className="text-xs text-muted-foreground">{user?.email || 'No email'}</p>
                                </div>
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="w-56">
                            <DropdownMenuLabel>My Account</DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem>
                                <User className="mr-2 h-4 w-4" />
                                <span>Profile</span>
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                                <Settings className="mr-2 h-4 w-4" />
                                <span>Settings</span>
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem onClick={onLogout} className="text-destructive focus:bg-destructive/10 focus:text-destructive cursor-pointer">
                                <LogOut className="mr-2 h-4 w-4" />
                                <span>Sign out</span>
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                </div>
            </div>
        </header>
    );
}
