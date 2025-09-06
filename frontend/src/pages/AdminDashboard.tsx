import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, FolderKanban, ListChecks } from "lucide-react";

interface GlobalStats {
  total_users: number;
  total_projects: number;
  total_tasks: number;
}

const AdminDashboard = () => {
  const { data: stats, isLoading, error } = useQuery<GlobalStats>({
    queryKey: ["globalStats"],
    queryFn: () => api.get("/stats/overview").then((res) => res.data.data),
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading statistics.</div>;
  if (!stats) return <div>No statistics available.</div>;

  const statItems = [
    { title: "Total Users", value: stats.total_users, icon: Users },
    { title: "Total Projects", value: stats.total_projects, icon: FolderKanban },
    { title: "Total Tasks", value: stats.total_tasks, icon: ListChecks },
  ];

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Admin Dashboard</h1>
      <div className="grid gap-4 md:grid-cols-3">
        {statItems.map((item) => (
          <Card key={item.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{item.title}</CardTitle>
              <item.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{item.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default AdminDashboard;