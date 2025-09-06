import React, { useState } from 'react';
import axios from 'axios';
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

// A simple SVG icon for the logo that uses your theme's primary color
const Logo = () => (
    <svg className="w-12 h-12 mx-auto text-primary" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14.59V7.41a1 1 0 0 1 1.71-.71l4.59 4.59a1 1 0 0 1 0 1.41l-4.59 4.59a1 1 0 0 1-1.71-.7z" />
    </svg>
);

interface LoginPageProps {
  onLoginSuccess: (token: string) => void;
}

export default function LoginPage({ onLoginSuccess }: LoginPageProps) {
    const [isSigningUp, setIsSigningUp] = useState(false);

    // State for form inputs
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        const backendUrl = 'http://127.0.0.1:8000/api';
        const endpoint = isSigningUp ? `${backendUrl}/register` : `${backendUrl}/login`;

        try {
            const payload = isSigningUp
                ? { name, email, password }
                : { username: email, password };

            const response = await axios.post(endpoint, payload);
            const responseData = response.data; // The outer JSON object from your backend
            console.log('Success!', responseData);

            // Handle successful login
            if (!isSigningUp && responseData.status === 'success' && responseData.data.access_token) {
                onLoginSuccess(responseData.data.access_token);
            } 
            // Handle successful registration
            else if (isSigningUp && responseData.status === 'success') {
                alert(responseData.message || 'Sign Up Successful! Please log in.');
                setIsSigningUp(false); // Switch to login form
                // Clear fields for login
                setName('');
                setEmail('');
                setPassword('');
            }
            // Handle cases where the response is successful but doesn't match expected structure
            else {
                 setError('Received an unexpected response from the server.');
            }

        } catch (err: any) {
            console.error('Authentication failed:', err);
            // Updated error handling to look for the message in your specific backend response structure
            const errorMessage = err.response?.data?.message || err.response?.data?.detail || 'An error occurred. Please try again.';
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
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
                        {isSigningUp && (
                            <div className="space-y-2">
                                <Label htmlFor="name">Name</Label>
                                <Input
                                    id="name"
                                    name="name"
                                    type="text"
                                    required
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    placeholder="Your Name"
                                    disabled={loading}
                                />
                            </div>
                        )}
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

                        {error && <p className="text-sm text-destructive text-center">{error}</p>}

                        <Button type="submit" disabled={loading} className="w-full">
                            {loading ? 'Processing...' : (isSigningUp ? 'Create Account' : 'Login')}
                        </Button>
                    </form>
                </CardContent>
                <CardFooter className="flex justify-center">
                    <p className="text-sm text-muted-foreground">
                        {isSigningUp ? 'Already have an account?' : "Don't have an account?"}
                        <Button variant="link" onClick={() => { setIsSigningUp(!isSigningUp); setError(''); }} className="font-medium">
                            {isSigningUp ? 'Login' : 'Sign Up'}
                        </Button>
                    </p>
                </CardFooter>
            </Card>
        </div>
    );
}

