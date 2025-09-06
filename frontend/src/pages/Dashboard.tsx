import { useState, FormEvent } from "react";
import { Plus, Calendar, Users, Clock, MoreVertical, Trash2, Edit, AlertTriangle } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import axios from 'axios';
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

// UI Components from shadcn/ui
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Skeleton } from "@/components/ui/skeleton";


// --- TYPE DEFINITIONS ---
// These should match your Pydantic models for type safety
interface TeamMember {
  user_id: string;
  username: string;
  role: string;
}

interface Project {
  _id: string;
  name: string;
  description: string;
  status: 'active' | 'completed' | 'on_hold';
  priority: 'low' | 'medium' | 'high';
  owner_id: string;
  team_members: TeamMember[];
  due_date: string; // Assuming ISO string format
  // Add other fields from your model as needed
  progress?: number; // Optional, can be calculated on frontend or backend
}

// --- API HELPER FUNCTIONS ---

// Helper to get the auth token safely
const getAuthHeader = () => {
    const token = localStorage.getItem("authToken");
    if (!token) throw new Error("Authentication token not found.");
    return { Authorization: `Bearer ${token}` };
};

// Function to fetch all projects for the current user
const fetchUserProjects = async (): Promise<Project[]> => {
    const response = await axios.get('http://127.0.0.1:8000/projects/', {
        headers: getAuthHeader()
    });
    // The actual projects array is nested in response.data.data.projects
    return response.data.data.projects;
};

// Function to create a new project
const createProject = async (projectData: { name: string; description: string; due_date: string; priority: string; }) => {
    const response = await axios.post('http://127.0.0.1:8000/projects/', projectData, {
        headers: getAuthHeader()
    });
    return response.data;
};

// Function to delete a project
const deleteProject = async (projectId: string) => {
    const response = await axios.delete(`http://127.0.0.1:8000/projects/${projectId}`, {
        headers: getAuthHeader()
    });
    return response.data;
};

// --- HELPER & STYLING FUNCTIONS ---

const getPriorityColor = (priority: string) => {
    switch (priority) {
        case "high": return "bg-destructive/80 text-destructive-foreground";
        case "medium": return "bg-yellow-500/80 text-white";
        case "low": return "bg-green-500/80 text-white";
        default: return "bg-muted text-muted-foreground";
    }
};

const getInitials = (name: string = "") => name.charAt(0).toUpperCase() || 'U';


// --- MAIN DASHBOARD COMPONENT ---

export default function Dashboard() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    const [isCreateModalOpen, setCreateModalOpen] = useState(false);
    const [isDeleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [projectToDelete, setProjectToDelete] = useState<string | null>(null);

    // --- DATA FETCHING (using react-query) ---
    const { data: projects, isLoading, isError, error } = useQuery<Project[], Error>({
        queryKey: ['userProjects'],
        queryFn: fetchUserProjects,
    });

    // --- DATA MUTATIONS (using react-query) ---
    
    // Mutation for creating a project
    const createProjectMutation = useMutation({
        mutationFn: createProject,
        onSuccess: (data) => {
            toast.success(data.message || "Project created successfully!");
            queryClient.invalidateQueries({ queryKey: ['userProjects'] }); // Refetch projects
            setCreateModalOpen(false); // Close the modal
        },
        onError: (error: any) => {
            const errorMessage = error.response?.data?.detail || "Failed to create project.";
            toast.error(errorMessage);
        }
    });

    // Mutation for deleting a project
    const deleteProjectMutation = useMutation({
        mutationFn: deleteProject,
        onSuccess: (data) => {
            toast.success(data.message || "Project deleted successfully!");
            queryClient.invalidateQueries({ queryKey: ['userProjects'] }); // Refetch
            setDeleteDialogOpen(false);
            setProjectToDelete(null);
        },
        onError: (error: any) => {
            const errorMessage = error.response?.data?.detail || "Failed to delete project.";
            toast.error(errorMessage);
        }
    });

    const handleCreateSubmit = (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);
        const newProject = {
            name: formData.get('name') as string,
            description: formData.get('description') as string,
            due_date: new Date(formData.get('due_date') as string).toISOString(),
            priority: formData.get('priority') as string,
        };
        createProjectMutation.mutate(newProject);
    };

    const handleDeleteClick = (projectId: string) => {
        setProjectToDelete(projectId);
        setDeleteDialogOpen(true);
    };

    const confirmDelete = () => {
        if (projectToDelete) {
            deleteProjectMutation.mutate(projectToDelete);
        }
    };

    // --- RENDER LOGIC ---

    const renderProjectGrid = () => {
        if (isLoading) {
            return (
                <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                    {Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-64 rounded-lg" />)}
                </div>
            );
        }

        if (isError) {
            return (
                <div className="text-center py-10 bg-destructive/10 rounded-lg">
                    <AlertTriangle className="mx-auto h-12 w-12 text-destructive" />
                    <h3 className="mt-2 text-lg font-medium text-destructive">Failed to load projects</h3>
                    <p className="mt-1 text-sm text-destructive-foreground">{error.message}</p>
                </div>
            );
        }
        
        if (!projects || projects.length === 0) {
            return (
                <div className="text-center py-16 border-2 border-dashed rounded-lg">
                    <h3 className="text-xl font-medium text-foreground">No Projects Found</h3>
                    <p className="mt-2 text-muted-foreground">Get started by creating your first project.</p>
                </div>
            );
        }

        return (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                {projects.map((project) => (
                    <Card
                        key={project._id}
                        className="card-gradient border-0 shadow-elegant hover-lift transition-transform duration-300"
                    >
                        <CardHeader className="pb-4 cursor-pointer" onClick={() => navigate(`/projects/${project._id}`)}>
                            <div className="flex items-start justify-between">
                                <div className="space-y-2">
                                    <CardTitle className="text-lg font-semibold text-foreground line-clamp-1">{project.name}</CardTitle>
                                    <Badge className={`text-xs capitalize ${getPriorityColor(project.priority)}`}>{project.priority}</Badge>
                                </div>
                                <DropdownMenu>
                                    <DropdownMenuTrigger asChild>
                                        <Button variant="ghost" size="icon" className="h-8 w-8" onClick={(e) => e.stopPropagation()}>
                                            <MoreVertical className="w-4 h-4" />
                                        </Button>
                                    </DropdownMenuTrigger>
                                    <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()}>
                                        <DropdownMenuItem><Edit className="mr-2 h-4 w-4" />Edit Project</DropdownMenuItem>
                                        <DropdownMenuSeparator />
                                        <DropdownMenuItem className="text-destructive focus:text-destructive focus:bg-destructive/10" onClick={() => handleDeleteClick(project._id)}>
                                            <Trash2 className="mr-2 h-4 w-4" />Delete Project
                                        </DropdownMenuItem>
                                    </DropdownMenuContent>
                                </DropdownMenu>
                            </div>
                        </CardHeader>
                        <CardContent className="space-y-4 cursor-pointer" onClick={() => navigate(`/projects/${project._id}`)}>
                            <p className="text-sm text-muted-foreground line-clamp-2 h-10">{project.description}</p>
                            <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                <div className="flex items-center gap-1">
                                    <Calendar className="w-4 h-4" />
                                    <span>Due {new Date(project.due_date).toLocaleDateString()}</span>
                                </div>
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-1">
                                    <Users className="w-4 h-4 text-muted-foreground" />
                                    <span className="text-sm text-muted-foreground">Team</span>
                                </div>
                                <div className="flex -space-x-2">
                                    {project.team_members.slice(0, 3).map((member) => (
                                        <Avatar key={member.user_id} className="w-8 h-8 border-2 border-background">
                                            <AvatarImage src="" alt={member.username} />
                                            <AvatarFallback className="bg-primary text-primary-foreground text-xs">{getInitials(member.username)}</AvatarFallback>
                                        </Avatar>
                                    ))}
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>
        );
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
                    <p className="text-muted-foreground mt-1">Welcome back! Here's an overview of your projects.</p>
                </div>
                 <Dialog open={isCreateModalOpen} onOpenChange={setCreateModalOpen}>
                    <DialogTrigger asChild>
                        <Button className="primary-gradient text-primary-foreground shadow-md hover:opacity-90">
                            <Plus className="w-4 h-4 mr-2" />
                            New Project
                        </Button>
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-[425px]">
                        <DialogHeader>
                            <DialogTitle>Create New Project</DialogTitle>
                            <DialogDescription>Fill in the details below to start a new project.</DialogDescription>
                        </DialogHeader>
                        <form onSubmit={handleCreateSubmit}>
                            <div className="grid gap-4 py-4">
                                <div className="grid grid-cols-4 items-center gap-4">
                                    <Label htmlFor="name" className="text-right">Name</Label>
                                    <Input id="name" name="name" required className="col-span-3" />
                                </div>
                                <div className="grid grid-cols-4 items-center gap-4">
                                    <Label htmlFor="description" className="text-right">Description</Label>
                                    <Textarea id="description" name="description" required className="col-span-3" />
                                </div>
                                <div className="grid grid-cols-4 items-center gap-4">
                                    <Label htmlFor="due_date" className="text-right">Due Date</Label>
                                    <Input id="due_date" name="due_date" type="date" required className="col-span-3" />
                                </div>
                                 <div className="grid grid-cols-4 items-center gap-4">
                                    <Label htmlFor="priority" className="text-right">Priority</Label>
                                    <select id="priority" name="priority" required className="col-span-3 border border-input bg-background h-10 rounded-md px-3 py-2 text-sm">
                                        <option value="low">Low</option>
                                        <option value="medium">Medium</option>
                                        <option value="high">High</option>
                                    </select>
                                </div>
                            </div>
                            <DialogFooter>
                                <Button type="submit" disabled={createProjectMutation.isPending}>
                                    {createProjectMutation.isPending ? 'Creating...' : 'Create Project'}
                                </Button>
                            </DialogFooter>
                        </form>
                    </DialogContent>
                </Dialog>
            </div>

            {/* Placeholder Stats Cards - Can be wired up later */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                 <Card className="card-gradient border-0 shadow-elegant hover-lift">
                     <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-muted-foreground">Total Projects</CardTitle></CardHeader>
                     <CardContent><div className="text-2xl font-bold text-foreground">{projects?.length || 0}</div></CardContent>
                 </Card>
                 <Card className="card-gradient border-0 shadow-elegant hover-lift">
                    <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-muted-foreground">Active Tasks</CardTitle></CardHeader>
                    <CardContent><div className="text-2xl font-bold text-foreground">--</div></CardContent>
                 </Card>
            </div>
            
            {/* Dynamic Projects Grid */}
            <div>
                <h2 className="text-xl font-semibold text-foreground mb-4">Your Projects</h2>
                {renderProjectGrid()}
            </div>

            {/* Delete Confirmation Dialog */}
            <AlertDialog open={isDeleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                        <AlertDialogDescription>
                            This action cannot be undone. This will permanently delete the project and all of its related data.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction onClick={confirmDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90" disabled={deleteProjectMutation.isPending}>
                            {deleteProjectMutation.isPending ? 'Deleting...' : 'Yes, delete project'}
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>

        </div>
    );
}
