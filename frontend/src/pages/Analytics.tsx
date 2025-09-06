import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { api } from "@/lib/api";

const projectData = [
    { name: 'Project Alpha', tasks: 40, members: 20 },
    { name: 'Project Beta', tasks: 30, members: 15 },
    { name: 'Project Gamma', tasks: 50, members: 25 },
    { name: 'Project Delta', tasks: 20, members: 10 },
];

const taskStatusData = [
    { name: 'To Do', value: 400 },
    { name: 'In Progress', value: 300 },
    { name: 'Done', value: 300 },
    { name: 'Blocked', value: 200 },
];

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

const Analytics = () => {
    // Example of fetching real data if you have an endpoint
    // const { data, isLoading, error } = useQuery({
    //     queryKey: ['analyticsData'],
    //     queryFn: () => api.get('/stats/analytics').then(res => res.data.data)
    // });

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-3xl font-bold mb-6">Application Analytics</h1>
            <div className="grid gap-6 md:grid-cols-2">
                <Card>
                    <CardHeader>
                        <CardTitle>Projects Overview</CardTitle>
                        <CardDescription>Tasks and Members per Project</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={projectData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Bar dataKey="tasks" fill="#8884d8" />
                                <Bar dataKey="members" fill="#82ca9d" />
                            </BarChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader>
                        <CardTitle>Task Status Distribution</CardTitle>
                        <CardDescription>Overall status of tasks across all projects</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie data={taskStatusData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} fill="#8884d8" label>
                                    {taskStatusData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default Analytics;