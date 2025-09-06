import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { 
  ArrowLeft, 
  Plus, 
  MoreVertical, 
  Calendar, 
  Clock,
  MessageSquare,
  Send,
  Paperclip
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
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
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const mockTasks = [
  {
    id: 1,
    title: "Design new landing page",
    description: "Create wireframes and mockups for the new homepage",
    assignee: { name: "Alice Johnson", initials: "AJ" },
    dueDate: "2024-01-12",
    status: "todo",
    priority: "high"
  },
  {
    id: 2,
    title: "Implement user authentication",
    description: "Set up login/signup functionality with proper security",
    assignee: { name: "Bob Smith", initials: "BS" },
    dueDate: "2024-01-15",
    status: "in-progress",
    priority: "high"
  },
  {
    id: 3,
    title: "Write API documentation",
    description: "Document all endpoints with examples",
    assignee: { name: "Carol Davis", initials: "CD" },
    dueDate: "2024-01-18",
    status: "done",
    priority: "medium"
  }
];

const mockDiscussion = [
  {
    id: 1,
    user: { name: "Alice Johnson", initials: "AJ" },
    message: "Just finished the initial wireframes. What do you think about the new layout?",
    timestamp: "2 hours ago",
    replies: [
      {
        id: 2,
        user: { name: "Bob Smith", initials: "BS" },
        message: "Looks great! I especially like the simplified navigation.",
        timestamp: "1 hour ago"
      }
    ]
  },
  {
    id: 3,
    user: { name: "Carol Davis", initials: "CD" },
    message: "The API documentation is now complete. All endpoints are documented with examples.",
    timestamp: "4 hours ago",
    replies: []
  }
];

export default function ProjectDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [newMessage, setNewMessage] = useState("");
  const [isTaskDialogOpen, setIsTaskDialogOpen] = useState(false);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "todo": return "bg-muted text-muted-foreground";
      case "in-progress": return "bg-accent text-accent-foreground";
      case "done": return "bg-success text-success-foreground";
      default: return "bg-muted text-muted-foreground";
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high": return "bg-destructive text-destructive-foreground";
      case "medium": return "bg-warning text-warning-foreground";
      case "low": return "bg-secondary text-secondary-foreground";
      default: return "bg-muted text-muted-foreground";
    }
  };

  const tasksByStatus = {
    todo: mockTasks.filter(task => task.status === "todo"),
    "in-progress": mockTasks.filter(task => task.status === "in-progress"),
    done: mockTasks.filter(task => task.status === "done")
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button 
          variant="ghost" 
          size="icon"
          onClick={() => navigate("/dashboard")}
        >
          <ArrowLeft className="w-4 h-4" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-foreground">Website Redesign</h1>
          <p className="text-muted-foreground mt-1">
            Redesigning the company website with modern UI/UX
          </p>
        </div>
        <Dialog open={isTaskDialogOpen} onOpenChange={setIsTaskDialogOpen}>
          <DialogTrigger asChild>
            <Button className="primary-gradient text-primary-foreground shadow-md">
              <Plus className="w-4 h-4 mr-2" />
              Add Task
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Create New Task</DialogTitle>
              <DialogDescription>
                Add a new task to this project. Fill in the details below.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="title">Title</Label>
                <Input id="title" placeholder="Enter task title..." />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="description">Description</Label>
                <Textarea id="description" placeholder="Enter task description..." />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="assignee">Assignee</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Select assignee" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="alice">Alice Johnson</SelectItem>
                    <SelectItem value="bob">Bob Smith</SelectItem>
                    <SelectItem value="carol">Carol Davis</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="dueDate">Due Date</Label>
                <Input id="dueDate" type="date" />
              </div>
            </div>
            <DialogFooter>
              <Button type="submit" className="primary-gradient text-primary-foreground">
                Create Task
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Task Board */}
        <div className="lg:col-span-2 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* To Do Column */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-foreground">To Do</h3>
                <Badge variant="secondary">{tasksByStatus.todo.length}</Badge>
              </div>
              <div className="space-y-3">
                {tasksByStatus.todo.map((task) => (
                  <Card key={task.id} className="card-gradient border-0 shadow-md hover-lift cursor-pointer">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <CardTitle className="text-sm font-medium line-clamp-2">
                          {task.title}
                        </CardTitle>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" className="h-6 w-6">
                              <MoreVertical className="w-3 h-3" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem>Edit Task</DropdownMenuItem>
                            <DropdownMenuItem>Move to In Progress</DropdownMenuItem>
                            <DropdownMenuItem className="text-destructive">
                              Delete Task
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-0 space-y-3">
                      <p className="text-xs text-muted-foreground line-clamp-2">
                        {task.description}
                      </p>
                      <div className="flex items-center justify-between">
                        <Badge className={`text-xs ${getPriorityColor(task.priority)}`}>
                          {task.priority}
                        </Badge>
                        <div className="flex items-center gap-2">
                          <Calendar className="w-3 h-3 text-muted-foreground" />
                          <span className="text-xs text-muted-foreground">{task.dueDate}</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <Avatar className="w-6 h-6">
                          <AvatarFallback className="bg-primary text-primary-foreground text-xs">
                            {task.assignee.initials}
                          </AvatarFallback>
                        </Avatar>
                        <span className="text-xs text-muted-foreground">{task.assignee.name}</span>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            {/* In Progress Column */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-foreground">In Progress</h3>
                <Badge variant="secondary">{tasksByStatus["in-progress"].length}</Badge>
              </div>
              <div className="space-y-3">
                {tasksByStatus["in-progress"].map((task) => (
                  <Card key={task.id} className="card-gradient border-0 shadow-md hover-lift cursor-pointer">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <CardTitle className="text-sm font-medium line-clamp-2">
                          {task.title}
                        </CardTitle>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" className="h-6 w-6">
                              <MoreVertical className="w-3 h-3" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem>Edit Task</DropdownMenuItem>
                            <DropdownMenuItem>Move to Done</DropdownMenuItem>
                            <DropdownMenuItem className="text-destructive">
                              Delete Task
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-0 space-y-3">
                      <p className="text-xs text-muted-foreground line-clamp-2">
                        {task.description}
                      </p>
                      <div className="flex items-center justify-between">
                        <Badge className={`text-xs ${getPriorityColor(task.priority)}`}>
                          {task.priority}
                        </Badge>
                        <div className="flex items-center gap-2">
                          <Calendar className="w-3 h-3 text-muted-foreground" />
                          <span className="text-xs text-muted-foreground">{task.dueDate}</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <Avatar className="w-6 h-6">
                          <AvatarFallback className="bg-primary text-primary-foreground text-xs">
                            {task.assignee.initials}
                          </AvatarFallback>
                        </Avatar>
                        <span className="text-xs text-muted-foreground">{task.assignee.name}</span>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            {/* Done Column */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-foreground">Done</h3>
                <Badge variant="secondary">{tasksByStatus.done.length}</Badge>
              </div>
              <div className="space-y-3">
                {tasksByStatus.done.map((task) => (
                  <Card key={task.id} className="card-gradient border-0 shadow-md hover-lift cursor-pointer opacity-75">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <CardTitle className="text-sm font-medium line-clamp-2 line-through">
                          {task.title}
                        </CardTitle>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" className="h-6 w-6">
                              <MoreVertical className="w-3 h-3" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem>Edit Task</DropdownMenuItem>
                            <DropdownMenuItem>Move to In Progress</DropdownMenuItem>
                            <DropdownMenuItem className="text-destructive">
                              Delete Task
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-0 space-y-3">
                      <p className="text-xs text-muted-foreground line-clamp-2">
                        {task.description}
                      </p>
                      <div className="flex items-center justify-between">
                        <Badge className={`text-xs ${getPriorityColor(task.priority)}`}>
                          {task.priority}
                        </Badge>
                        <div className="flex items-center gap-2">
                          <Calendar className="w-3 h-3 text-muted-foreground" />
                          <span className="text-xs text-muted-foreground">{task.dueDate}</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <Avatar className="w-6 h-6">
                          <AvatarFallback className="bg-primary text-primary-foreground text-xs">
                            {task.assignee.initials}
                          </AvatarFallback>
                        </Avatar>
                        <span className="text-xs text-muted-foreground">{task.assignee.name}</span>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Discussion Panel */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-primary" />
            <h3 className="font-semibold text-foreground">Project Discussion</h3>
          </div>
          
          <Card className="card-gradient border-0 shadow-elegant">
            <CardContent className="p-4 space-y-4 max-h-96 overflow-y-auto">
              {mockDiscussion.map((message) => (
                <div key={message.id} className="space-y-3">
                  <div className="flex gap-3">
                    <Avatar className="w-8 h-8 flex-shrink-0">
                      <AvatarFallback className="bg-primary text-primary-foreground text-xs">
                        {message.user.initials}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-foreground">
                          {message.user.name}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {message.timestamp}
                        </span>
                      </div>
                      <p className="text-sm text-foreground">{message.message}</p>
                      
                      {/* Replies */}
                      {message.replies.map((reply) => (
                        <div key={reply.id} className="ml-4 mt-3 flex gap-3">
                          <Avatar className="w-6 h-6 flex-shrink-0">
                            <AvatarFallback className="bg-secondary text-secondary-foreground text-xs">
                              {reply.user.initials}
                            </AvatarFallback>
                          </Avatar>
                          <div className="flex-1 space-y-1">
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-medium text-foreground">
                                {reply.user.name}
                              </span>
                              <span className="text-xs text-muted-foreground">
                                {reply.timestamp}
                              </span>
                            </div>
                            <p className="text-sm text-foreground">{reply.message}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Message Input */}
          <div className="space-y-2">
            <Textarea
              placeholder="Type your message..."
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              className="resize-none"
              rows={3}
            />
            <div className="flex justify-between items-center">
              <Button variant="ghost" size="icon">
                <Paperclip className="w-4 h-4" />
              </Button>
              <Button className="primary-gradient text-primary-foreground">
                <Send className="w-4 h-4 mr-2" />
                Send
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}