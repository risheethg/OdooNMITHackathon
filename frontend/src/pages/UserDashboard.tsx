import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FolderKanban, ListChecks } from "lucide-react";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface UserStats {
  projects_count: number;
  assigned_tasks_count: number;
  task_status_breakdown: { [key: string]: number };
}

const COLORS = {
    'To Do': '#8884d8',
    'In Progress': '#82ca9d',
    'Done': '#ffc658',
    'Blocked': '#ff8042',
};

const UserDashboard = () => {
  const { data: stats, isLoading, error } = useQuery<UserStats>({
    queryKey: ["userStats"],
    queryFn: () => api.get("/stats/user/me").then((res) => res.data.data),
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading statistics.</div>;
  if (!stats) return <div>No statistics available.</div>;

  const taskData = Object.entries(stats.task_status_breakdown).map(([name, value]) => ({
    name,
    value,
  }));

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">My Dashboard</h1>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">My Projects</CardTitle>
            <FolderKanban className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.projects_count}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Assigned Tasks</CardTitle>
            <ListChecks className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.assigned_tasks_count}</div>
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
            ) : <p>No tasks assigned to you yet.</p>}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default UserDashboard;