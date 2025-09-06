import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, ListChecks } from "lucide-react";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface ProjectStats {
  member_count: number;
  total_tasks_in_project: number;
  task_status_breakdown: { [key: string]: number };
}

const COLORS = {
    'To Do': '#8884d8',
    'In Progress': '#82ca9d',
    'Done': '#ffc658',
    'Blocked': '#ff8042',
};

const ProjectDashboard = () => {
  const { projectId } = useParams<{ projectId: string }>();

  const { data: stats, isLoading, error } = useQuery<ProjectStats>({
    queryKey: ["projectStats", projectId],
    queryFn: () => api.get(`/stats/project/${projectId}`).then((res) => res.data.data),
    enabled: !!projectId,
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading project statistics. You might not be a member of this project.</div>;
  if (!stats) return <div>No statistics available for this project.</div>;

  const taskData = Object.entries(stats.task_status_breakdown).map(([name, value]) => ({
    name,
    value,
  }));

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Project Dashboard</h1>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Team Members</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.member_count}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Tasks</CardTitle>
            <ListChecks className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_tasks_in_project}</div>
          </CardContent>
        </Card>
      </div>
      <div className="mt-6">
        <Card>
          <CardHeader>
            <CardTitle>Task Status Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            {taskData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={taskData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {taskData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[entry.name as keyof typeof COLORS] || '#000000'} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : <p>No tasks in this project yet.</p>}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ProjectDashboard;