import { useState } from "react";
import { Plus, Calendar, Users, Clock, MoreVertical } from "lucide-react";
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
} from "@/components/ui/dropdown-menu";
import { useNavigate } from "react-router-dom";

const mockProjects = [
  {
    id: 1,
    name: "Website Redesign",
    description: "Redesigning the company website with modern UI/UX",
    progress: 75,
    tasks: { total: 24, completed: 18 },
    members: [
      { id: 1, name: "Alice Johnson", avatar: "", initials: "AJ" },
      { id: 2, name: "Bob Smith", avatar: "", initials: "BS" },
      { id: 3, name: "Carol Davis", avatar: "", initials: "CD" },
    ],
    dueDate: "2024-01-15",
    status: "active",
    priority: "high"
  },
  {
    id: 2,
    name: "Mobile App Development",
    description: "Creating a new mobile application for customer engagement",
    progress: 45,
    tasks: { total: 32, completed: 14 },
    members: [
      { id: 4, name: "David Wilson", avatar: "", initials: "DW" },
      { id: 5, name: "Emma Brown", avatar: "", initials: "EB" },
    ],
    dueDate: "2024-02-28",
    status: "active",
    priority: "medium"
  },
  {
    id: 3,
    name: "Database Migration",
    description: "Migrating legacy database to new cloud infrastructure",
    progress: 90,
    tasks: { total: 16, completed: 14 },
    members: [
      { id: 6, name: "Frank Miller", avatar: "", initials: "FM" },
      { id: 7, name: "Grace Lee", avatar: "", initials: "GL" },
      { id: 8, name: "Henry Clark", avatar: "", initials: "HC" },
    ],
    dueDate: "2024-01-10",
    status: "active",
    priority: "high"
  },
];

export default function Dashboard() {
  const navigate = useNavigate();

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high": return "bg-destructive text-destructive-foreground";
      case "medium": return "bg-warning text-warning-foreground";
      case "low": return "bg-secondary text-secondary-foreground";
      default: return "bg-muted text-muted-foreground";
    }
  };

  const getProgressColor = (progress: number) => {
    if (progress >= 75) return "bg-success";
    if (progress >= 50) return "bg-warning";
    return "bg-destructive";
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Welcome back! Here's what's happening with your projects.
          </p>
        </div>
        <Button className="primary-gradient text-primary-foreground shadow-md hover:opacity-90">
          <Plus className="w-4 h-4 mr-2" />
          New Project
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="card-gradient border-0 shadow-elegant hover-lift">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Projects</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">12</div>
            <p className="text-xs text-success mt-1">+2 from last month</p>
          </CardContent>
        </Card>

        <Card className="card-gradient border-0 shadow-elegant hover-lift">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Active Tasks</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">72</div>
            <p className="text-xs text-warning mt-1">18 due this week</p>
          </CardContent>
        </Card>

        <Card className="card-gradient border-0 shadow-elegant hover-lift">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Team Members</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">24</div>
            <p className="text-xs text-success mt-1">+3 new members</p>
          </CardContent>
        </Card>

        <Card className="card-gradient border-0 shadow-elegant hover-lift">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Completion Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">84%</div>
            <p className="text-xs text-success mt-1">Above target</p>
          </CardContent>
        </Card>
      </div>

      {/* Projects Grid */}
      <div>
        <h2 className="text-xl font-semibold text-foreground mb-4">Active Projects</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {mockProjects.map((project) => (
            <Card 
              key={project.id} 
              className="card-gradient border-0 shadow-elegant hover-lift cursor-pointer"
              onClick={() => navigate(`/projects/${project.id}`)}
            >
              <CardHeader className="pb-4">
                <div className="flex items-start justify-between">
                  <div className="space-y-2">
                    <CardTitle className="text-lg font-semibold text-foreground line-clamp-1">
                      {project.name}
                    </CardTitle>
                    <Badge className={`text-xs ${getPriorityColor(project.priority)}`}>
                      {project.priority.toUpperCase()}
                    </Badge>
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <MoreVertical className="w-4 h-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem>Edit Project</DropdownMenuItem>
                      <DropdownMenuItem>View Details</DropdownMenuItem>
                      <DropdownMenuItem className="text-destructive">
                        Delete Project
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground line-clamp-2">
                  {project.description}
                </p>

                {/* Progress */}
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Progress</span>
                    <span className="font-medium text-foreground">{project.progress}%</span>
                  </div>
                  <Progress 
                    value={project.progress} 
                    className={`h-2 ${getProgressColor(project.progress)}`}
                  />
                </div>

                {/* Tasks */}
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    <span>{project.tasks.completed}/{project.tasks.total} tasks</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    <span>Due {project.dueDate}</span>
                  </div>
                </div>

                {/* Team Members */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1">
                    <Users className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">Team</span>
                  </div>
                  <div className="flex -space-x-2">
                    {project.members.slice(0, 3).map((member) => (
                      <Avatar key={member.id} className="w-8 h-8 border-2 border-background">
                        <AvatarImage src={member.avatar} alt={member.name} />
                        <AvatarFallback className="bg-primary text-primary-foreground text-xs">
                          {member.initials}
                        </AvatarFallback>
                      </Avatar>
                    ))}
                    {project.members.length > 3 && (
                      <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center border-2 border-background">
                        <span className="text-xs text-muted-foreground">
                          +{project.members.length - 3}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}