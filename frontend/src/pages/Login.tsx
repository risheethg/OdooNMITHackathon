import React, { useState } from 'react';
import axios from 'axios';
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle
} from "@/components/ui/card";
import { AlertCircle } from "lucide-react";

// A simple SVG icon for the logo that uses your theme's primary color
const Logo = () => (
    <svg className="w-12 h-12 mx-auto text-primary" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14.59V7.41a1 1 0 0 1 1.71-.71l4.59 4.59a1 1 0 0 1 0 1.41l-4.59 4.59a1 1 0 0 1-1.71-.7z" />
    </svg>
);

// A styled component for displaying form errors elegantly
const FormError = ({ message }: { message: string | null }) => {
    if (!message) return null;
    return (
        <div className="flex items-center gap-x-2 rounded-md bg-destructive/15 p-3 text-sm text-destructive">
            <AlertCircle className="h-4 w-4" />
            <p>{message}</p>
        </div>
    );
};


interface LoginPageProps {
  onLoginSuccess: (token: string) => void;
}

export default function LoginPage({ onLoginSuccess }: LoginPageProps) {
    const [isSigningUp, setIsSigningUp] = useState(false);

    // State for form inputs
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        const backendUrl = 'http://127.0.0.1:8000';

        try {
            let response;
            if (isSigningUp) {
                // --- SIGN UP ---
                const endpoint = `${backendUrl}/auth/register`;
                const payload = { username, email, password };
                response = await axios.post(endpoint, payload);
                
                toast.success(response.data.message || 'Sign Up Successful! Please log in.');
                setIsSigningUp(false);
                
                // Keep username for login convenience, clear other fields
                setPassword('');
                setEmail('');

            } else {
                // --- LOGIN ---
                const endpoint = `${backendUrl}/auth/login`;
                const params = new URLSearchParams();
                // **FIX:** Use the `username` state for the login request, not `email`.
                params.append('username', username);
                params.append('password', password);

                response = await axios.post(endpoint, params, {
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                });

                const responseData = response.data;
                if (responseData.status === 'success' && responseData.data.access_token) {
                    toast.success(responseData.message || "Login successful!");
                    onLoginSuccess(responseData.data.access_token);
                } else {
                    throw new Error('Received an unexpected response from the server.');
                }
            }

        } catch (err: any) {
            console.error('Authentication failed:', err);
            const errorMessage = err.response?.data?.message || err.response?.data?.detail || 'An unknown error occurred. Please try again.';
            setError(errorMessage);
            toast.error(errorMessage);
        } finally {
            setLoading(false);
        }
    };
    
    const toggleFormType = () => {
        setIsSigningUp(!isSigningUp);
        setError(null);
        setUsername('');
        setEmail('');
        setPassword('');
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-background font-sans px-4">
            <Card className="w-full max-w-md">
                <CardHeader className="text-center">
                    <Logo />
                    <CardTitle className="mt-4">SynergySphere</CardTitle>
                    <CardDescription>
                        {isSigningUp ? 'Create an account to start collaborating' : 'Welcome back! Please sign in.'}
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form className="space-y-4" onSubmit={handleSubmit}>
                        {/* **FIX:** Username field is now used for both login and signup */}
                        <div className="space-y-2">
                            <Label htmlFor="username">Username</Label>
                            <Input
                                id="username"
                                name="username"
                                type="text"
                                autoComplete="username"
                                required
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                placeholder={isSigningUp ? "Choose a username" : "Enter your username"}
                                disabled={loading}
                            />
                        </div>

                        {/* Email field is now ONLY shown during signup */}
                        {isSigningUp && (
                            <div className="space-y-2">
                                <Label htmlFor="email">Email</Label>
                                <Input
                                    id="email"
                                    name="email"
                                    type="email"
                                    autoComplete="email"
                                    required
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="you@example.com"
                                    disabled={loading}
                                />
                            </div>
                        )}

                        <div className="space-y-2">
                             <div className="flex items-center justify-between">
                                <Label htmlFor="password">Password</Label>
                                {!isSigningUp && (
                                    <a href="#" className="text-sm font-medium text-primary underline-offset-4 hover:underline">
                                        Forgot Password?
                                    </a>
                                )}
                            </div>
                            <Input
                                id="password"
                                name="password"
                                type="password"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="••••••••"
                                disabled={loading}
                            />
                        </div>
                        
                        <FormError message={error} />

                        <Button type="submit" disabled={loading} className="w-full">
                            {loading ? 'Processing...' : (isSigningUp ? 'Create Account' : 'Login')}
                        </Button>
                    </form>
                </CardContent>
                <CardFooter className="flex justify-center">
                    <p className="text-sm text-muted-foreground">
                        {isSigningUp ? 'Already have an account?' : "Don't have an account?"}
                        <Button variant="link" onClick={toggleFormType} className="font-medium" type="button">
                            {isSigningUp ? 'Login' : 'Sign Up'}
                        </Button>
                    </p>
                </CardFooter>
            </Card>
        </div>
    );
}

