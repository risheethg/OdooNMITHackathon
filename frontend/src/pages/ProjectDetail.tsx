import { useState, useMemo, FormEvent } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { toast } from "sonner";

import { 
  ArrowLeft, 
  Plus, 
  MoreVertical, 
  Calendar, 
  MessageSquare,
  Send,
  Paperclip,
  AlertTriangle,
  Trash2,
  Edit,
  UserPlus,
  X
} from "lucide-react";

// UI Components from shadcn/ui
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
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
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
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
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";

// --- TYPE DEFINITIONS ---
interface User {
    _id: string;
    username: string;
    email: string;
}

interface Project {
  _id: string;
  project_name: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high';
  due_date?: string;
  created_by: string;
  members: string[]; // Still an array of user IDs
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
}

type TaskStatus = "To Do" | "In Progress" | "Done";

// FIXED: Interface now matches the backend Pydantic Task model exactly
interface Task {
    _id: string; // Alias for task_id
    title: string;
    description?: string;
    assignee: string; // User ID
    due_date: string;
    status: TaskStatus;
    project_id: string;
    created_by: string;
    is_deleted: boolean;
    created_at: string;
    updated_at: string;
}

interface TaskCreateData {
    title: string;
    description?: string;
    assignee: string;
    due_date: string;
    status: TaskStatus;
}

interface TaskUpdateData {
    status?: TaskStatus;
}

// --- MOCK DATA (Discussion Panel) ---
const mockDiscussion = [
  { id: 1, user: { name: "Alice", initials: "A" }, message: "Finished wireframes, what do you think?", timestamp: "2 hours ago", replies: [{ id: 2, user: { name: "Bob", initials: "B" }, message: "Looks great!", timestamp: "1 hour ago" }] },
];


// --- API HELPER FUNCTIONS ---
const getAuthHeader = () => {
    const token = localStorage.getItem("authToken");
    if (!token) throw new Error("Authentication token not found.");
    return { Authorization: `Bearer ${token}` };
};

const fetchProjectById = async (projectId: string): Promise<Project> => {
    const response = await axios.get(`http://127.0.0.1:8000/projects/${projectId}`, { headers: getAuthHeader() });
    return response.data.data;
};

const fetchTasksForProject = async (projectId: string): Promise<Task[]> => {
    const response = await axios.get(`http://127.0.0.1:8000/tasks/project/${projectId}`, { headers: getAuthHeader() });
    return response.data.data;
};

const fetchAllUsers = async (): Promise<User[]> => {
    const response = await axios.get('http://127.0.0.1:8000/auth/users/all', { headers: getAuthHeader() });
    return response.data.data;
}

const addMemberToProject = async ({ projectId, userId, email }: { projectId: string; userId: string; email: string; }) => {
    const payload = {
        user_id: userId,
        email: email,
    };
    const response = await axios.post(`http://127.0.0.1:8000/projects/${projectId}/members`, payload, { headers: getAuthHeader() });
    return response.data;
}

const removeMemberFromProject = async ({ projectId, userId }: { projectId: string; userId: string }) => {
    const response = await axios.delete(`http://127.0.0.1:8000/projects/${projectId}/members/${userId}`, { headers: getAuthHeader() });
    return response.data;
}


const createTask = async ({ projectId, taskData }: { projectId: string, taskData: TaskCreateData }) => {
    const response = await axios.post(`http://127.0.0.1:8000/tasks/?project_id=${projectId}`, taskData, { headers: getAuthHeader() });
    return response.data;
};

const updateTask = async ({ taskId, updateData }: { taskId: string, updateData: TaskUpdateData }) => {
    const response = await axios.put(`http://127.0.0.1:8000/tasks/${taskId}`, updateData, { headers: getAuthHeader() });
    return response.data;
};

const deleteTask = async (taskId: string) => {
    const response = await axios.delete(`http://127.0.0.1:8000/tasks/${taskId}`, { headers: getAuthHeader() });
    return response.data;
}

const getInitials = (name: string = "") => name.substring(0, 2).toUpperCase();


// --- MAIN COMPONENT ---
export default function ProjectDetail() {
  const { id: projectId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [isTaskDialogOpen, setIsTaskDialogOpen] = useState(false);
  const [isAddMemberDialogOpen, setIsAddMemberDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [taskToDelete, setTaskToDelete] = useState<Task | null>(null);

  // --- DATA FETCHING ---
  const { data: project, isLoading: isProjectLoading, isError: isProjectError, error: projectError } = useQuery<Project, Error>({
      queryKey: ['project', projectId],
      queryFn: () => fetchProjectById(projectId!),
      enabled: !!projectId, 
  });

  const { data: tasks, isLoading: areTasksLoading } = useQuery<Task[], Error>({
      queryKey: ['tasks', projectId],
      queryFn: () => fetchTasksForProject(projectId!),
      enabled: !!projectId,
  });

  const { data: allUsers, isLoading: areUsersLoading } = useQuery<User[], Error>({
      queryKey: ['allUsers'],
      queryFn: fetchAllUsers
  });

  // --- DATA MUTATIONS ---
  const addMemberMutation = useMutation({
      mutationFn: addMemberToProject,
      onSuccess: () => {
          toast.success("Member added to project!");
          queryClient.invalidateQueries({ queryKey: ['project', projectId] });
      },
      onError: (error: any) => toast.error(error.response?.data?.detail || "Failed to add member."),
  });

  const removeMemberMutation = useMutation({
      mutationFn: removeMemberFromProject,
      onSuccess: () => {
          toast.success("Member removed from project.");
          queryClient.invalidateQueries({ queryKey: ['project', projectId] });
      },
      onError: (error: any) => toast.error(error.response?.data?.detail || "Failed to remove member."),
  });

  const createTaskMutation = useMutation({
      mutationFn: createTask,
      onSuccess: () => {
          toast.success("Task created successfully!");
          queryClient.invalidateQueries({ queryKey: ['tasks', projectId] });
          setIsTaskDialogOpen(false);
      },
      onError: (error: any) => toast.error(error.response?.data?.detail || "Failed to create task."),
  });

  const updateTaskMutation = useMutation({
      mutationFn: updateTask,
      onSuccess: () => {
          toast.success("Task status updated!");
          queryClient.invalidateQueries({ queryKey: ['tasks', projectId] });
      },
      onError: (error: any) => toast.error(error.response?.data?.detail || "Failed to update task."),
  });

  const deleteTaskMutation = useMutation({
      mutationFn: deleteTask,
      onSuccess: () => {
          toast.success("Task deleted.");
          queryClient.invalidateQueries({ queryKey: ['tasks', projectId] });
          setDeleteDialogOpen(false);
          setTaskToDelete(null);
      },
      onError: (error: any) => toast.error(error.response?.data?.detail || "Failed to delete task."),
  })

  // --- EVENT HANDLERS ---
  const handleCreateTaskSubmit = (e: FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      if (!projectId) return;
      const formData = new FormData(e.currentTarget);
      const taskData: TaskCreateData = {
          title: formData.get('title') as string,
          description: formData.get('description') as string,
          assignee: formData.get('assignee') as string,
          due_date: new Date(formData.get('dueDate') as string).toISOString(),
          status: "To Do"
      };
      createTaskMutation.mutate({ projectId, taskData });
  };
  
  const handleChangeStatus = (taskId: string, status: TaskStatus) => {
      updateTaskMutation.mutate({ taskId, updateData: { status }});
  };

  const handleDeleteClick = (task: Task) => {
      setTaskToDelete(task);
      setDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
      if (taskToDelete) {
          deleteTaskMutation.mutate(taskToDelete._id);
      }
  };

  // --- DERIVED STATE & UI HELPERS ---
  const { projectMembers, availableUsersToAdd } = useMemo(() => {
    if (!project || !allUsers) return { projectMembers: [], availableUsersToAdd: [] };
    const memberIds = new Set(project.members);
    const projectMembers = allUsers.filter(user => memberIds.has(user._id));
    const availableUsersToAdd = allUsers.filter(user => !memberIds.has(user._id));
    return { projectMembers, availableUsersToAdd };
  }, [project, allUsers]);

  const tasksByStatus = useMemo(() => {
    const grouped: Record<TaskStatus, Task[]> = {
      "To Do": [],
      "In Progress": [],
      "Done": [],
    };
    tasks?.forEach(task => {
      if (grouped[task.status]) {
        grouped[task.status].push(task);
      }
    });
    return grouped;
  }, [tasks]);

  // --- RENDER LOGIC ---
  if (isProjectLoading) {
    return <div className="p-6"><Skeleton className="h-96 w-full" /></div>;
  }
  if (isProjectError) {
    return (
      <div className="text-center py-10">
          <AlertTriangle className="mx-auto h-12 w-12 text-destructive" />
          <h3 className="mt-2 text-lg font-medium text-destructive">Failed to load project</h3>
          <p className="mt-1 text-sm text-muted-foreground">{projectError.message}</p>
          <Button onClick={() => navigate("/dashboard")} className="mt-4">Go Back</Button>
      </div>
    );
  }

  const renderTaskColumn = (title: TaskStatus, tasksInColumn: Task[]) => (
    <div className="space-y-4">
        <div className="flex items-center justify-between"><h3 className="font-semibold text-foreground">{title}</h3><Badge variant="secondary">{tasksInColumn.length}</Badge></div>
        <div className="space-y-3">
            {areTasksLoading ? <Skeleton className="h-24 w-full" /> : tasksInColumn.map((task) => {
                const assignee = projectMembers.find(m => m._id === task.assignee);
                const assigneeName = assignee?.username || 'Unknown';
              return (
              <Card key={task._id} className={`card-gradient border-0 shadow-md hover-lift cursor-pointer ${task.status === 'Done' ? 'opacity-70' : ''}`}>
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <CardTitle className={`text-sm font-medium line-clamp-2 ${task.status === 'Done' ? 'line-through' : ''}`}>{task.title}</CardTitle>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild><Button variant="ghost" size="icon" className="h-6 w-6 shrink-0"><MoreVertical className="w-3 h-3" /></Button></DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem disabled> <Edit className="mr-2 h-4 w-4" /> Edit Task</DropdownMenuItem><DropdownMenuSeparator/>
                        {task.status !== 'To Do' && <DropdownMenuItem onClick={() => handleChangeStatus(task._id, 'To Do')}>Move to To Do</DropdownMenuItem>}
                        {task.status !== 'In Progress' && <DropdownMenuItem onClick={() => handleChangeStatus(task._id, 'In Progress')}>Move to In Progress</DropdownMenuItem>}
                        {task.status !== 'Done' && <DropdownMenuItem onClick={() => handleChangeStatus(task._id, 'Done')}>Move to Done</DropdownMenuItem>}<DropdownMenuSeparator/>
                        <DropdownMenuItem className="text-destructive focus:text-destructive focus:bg-destructive/10" onClick={() => handleDeleteClick(task)}><Trash2 className="mr-2 h-4 w-4" /> Delete Task</DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </CardHeader>
                <CardContent className="pt-0 space-y-3">
                  <p className="text-xs text-muted-foreground line-clamp-2">{task.description}</p>
                   <div className="flex items-center gap-2"><Calendar className="w-3 h-3 text-muted-foreground" /><span className="text-xs text-muted-foreground">Due: {new Date(task.due_date).toLocaleDateString()}</span></div>
                   <div className="flex items-center gap-2">
                       <Avatar className="w-5 h-5"><AvatarFallback className="text-xs">{getInitials(assigneeName)}</AvatarFallback></Avatar>
                       <span className="text-xs text-muted-foreground truncate" title={assigneeName}>Assigned to: {assigneeName}</span>
                   </div>
                </CardContent>
              </Card>
            )})}
        </div>
      </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate("/dashboard")}><ArrowLeft className="w-4 h-4" /></Button>
        <div className="flex-1"><h1 className="text-3xl font-bold text-foreground">{project?.project_name}</h1><p className="text-muted-foreground mt-1">{project?.description}</p></div>
        {/* Add Task Dialog Trigger */}
        <Dialog open={isTaskDialogOpen} onOpenChange={setIsTaskDialogOpen}>
          <DialogTrigger asChild><Button className="primary-gradient text-primary-foreground shadow-md"><Plus className="w-4 h-4 mr-2" />Add Task</Button></DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader><DialogTitle>Create New Task</DialogTitle><DialogDescription>Add a new task to this project.</DialogDescription></DialogHeader>
            <form onSubmit={handleCreateTaskSubmit}>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2"><Label htmlFor="title">Title</Label><Input id="title" name="title" required placeholder="Enter task title..." /></div>
                  <div className="grid gap-2"><Label htmlFor="description">Description</Label><Textarea id="description" name="description" placeholder="Enter task description..." /></div>
                  <div className="grid gap-2"><Label htmlFor="assignee">Assignee</Label>
                    <Select name="assignee" required>
                      <SelectTrigger><SelectValue placeholder="Select a team member" /></SelectTrigger>
                      <SelectContent>{projectMembers.map(member => <SelectItem key={member._id} value={member._id}>{member.username}</SelectItem>)}</SelectContent>
                    </Select>
                  </div>
                  <div className="grid gap-2"><Label htmlFor="dueDate">Due Date</Label><Input id="dueDate" name="dueDate" type="date" required /></div>
                </div>
                <DialogFooter><Button type="submit" className="primary-gradient" disabled={createTaskMutation.isPending}>{createTaskMutation.isPending ? "Creating..." : "Create Task"}</Button></DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Task Board */}
        <div className="lg:col-span-2 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {renderTaskColumn("To Do", tasksByStatus["To Do"])}
            {renderTaskColumn("In Progress", tasksByStatus["In Progress"])}
            {renderTaskColumn("Done", tasksByStatus["Done"])}
          </div>
        </div>

        {/* Right Panel: Members & Discussion */}
        <div className="space-y-6">
            {/* NEW: Team Members Card */}
            <Card className="card-gradient border-0 shadow-elegant">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <CardTitle className="text-base font-semibold">Team Members</CardTitle>
                    <Dialog open={isAddMemberDialogOpen} onOpenChange={setIsAddMemberDialogOpen}>
                        <DialogTrigger asChild>
                            <Button variant="ghost" size="sm"><UserPlus className="h-4 w-4 mr-2" />Add</Button>
                        </DialogTrigger>
                        <DialogContent>
                            <DialogHeader><DialogTitle>Add Members to Project</DialogTitle></DialogHeader>
                            <div className="space-y-2 py-4 max-h-80 overflow-y-auto">
                                {areUsersLoading && <Skeleton className="h-10 w-full" />}
                                {availableUsersToAdd.map(user => (
                                    <div key={user._id} className="flex items-center justify-between p-2 rounded-md hover:bg-muted">
                                        <div className="flex items-center gap-3">
                                            <Avatar className="w-8 h-8"><AvatarFallback>{getInitials(user.username)}</AvatarFallback></Avatar>
                                            <div>
                                                <p className="text-sm font-medium">{user.username}</p>
                                                <p className="text-xs text-muted-foreground">{user.email}</p>
                                            </div>
                                        </div>
                                        <Button size="sm" onClick={() => addMemberMutation.mutate({ projectId: projectId!, userId: user._id, email: user.email })} disabled={addMemberMutation.isPending}>Add</Button>
                                    </div>
                                ))}
                                {!areUsersLoading && availableUsersToAdd.length === 0 && <p className="text-center text-sm text-muted-foreground py-4">All users are already in this project.</p>}
                            </div>
                        </DialogContent>
                    </Dialog>
                </CardHeader>
                <CardContent className="space-y-3">
                    {projectMembers.map(member => (
                        <div key={member._id} className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <Avatar className="w-8 h-8"><AvatarFallback>{getInitials(member.username)}</AvatarFallback></Avatar>
                                <div><p className="text-sm font-medium">{member.username}</p><p className="text-xs text-muted-foreground">{member.email}</p></div>
                            </div>
                            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => removeMemberMutation.mutate({ projectId: projectId!, userId: member._id })} disabled={removeMemberMutation.isPending}><X className="h-4 w-4"/></Button>
                        </div>
                    ))}
                </CardContent>
            </Card>

            {/* Discussion Panel (Mock Data) */}
            <div className="space-y-4">
                <div className="flex items-center gap-2"><MessageSquare className="w-5 h-5 text-primary" /><h3 className="font-semibold text-foreground">Project Discussion</h3></div>
                <Card className="card-gradient border-0 shadow-elegant"><CardContent className="p-4 max-h-96 overflow-y-auto">{/* Mock UI */} </CardContent></Card>
                <div className="space-y-2">{/* Message Input */}</div>
            </div>
        </div>
      </div>
      
      {/* Delete Task Dialog */}
       <AlertDialog open={isDeleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
            <AlertDialogContent>
                <AlertDialogHeader>
                    <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                    <AlertDialogDescription>
                        This will permanently delete the task. This action cannot be undone.
                    </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction 
                        onClick={confirmDelete} 
                        className="bg-destructive text-destructive-foreground hover:bg-destructive/90" 
                        disabled={deleteTaskMutation.isPending}
                    >
                        {deleteTaskMutation.isPending ? "Deleting..." : "Delete Task"}
                    </AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
       </AlertDialog>
    </div>
  );
}

