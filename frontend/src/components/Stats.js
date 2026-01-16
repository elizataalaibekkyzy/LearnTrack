import React, { useState, useEffect } from "react";
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Paper,
  List,
  ListItem,
  ListItemText,
} from "@mui/material";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import {
  People as PeopleIcon,
  School as SchoolIcon,
  Assignment as AssignmentIcon,
  CheckCircle as CheckCircleIcon,
  PlayArrow as PlayArrowIcon,
} from "@mui/icons-material";
import apiService from "../services/api";

function Stats() {
  const [stats, setStats] = useState(null);
  const [dashboardData, setDashboardData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [runningJob, setRunningJob] = useState(false);
  const [jobResult, setJobResult] = useState(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const [statsRes, dashboardRes] = await Promise.all([
        apiService.getStats(),
        apiService.getDashboard(),
      ]);
      setStats(statsRes.data);
      setDashboardData(dashboardRes.data);
      setError(null);
    } catch (err) {
      setError("Failed to load statistics");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const runReminderJob = async () => {
    try {
      setRunningJob(true);
      setJobResult(null);
      const response = await apiService.runJob();
      setJobResult(response.data);
      // Refresh stats after job runs
      await fetchStats();
    } catch (err) {
      setJobResult({ success: false, error: "Failed to run job" });
    } finally {
      setRunningJob(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
        <Button variant="contained" onClick={fetchStats}>
          Retry
        </Button>
      </Box>
    );
  }

  if (!stats) return null;

  // Prepare chart data
  const courseStatusData = [
    { name: "Completed", value: stats.completed_courses, color: "#4caf50" },
    { name: "In Progress", value: stats.courses_in_progress, color: "#2196f3" },
    {
      name: "Needs Attention",
      value: stats.courses_needing_attention,
      color: "#f44336",
    },
  ];

  const userProgressData = dashboardData.map((user) => ({
    name: user.name.split(" ")[0], // First name only
    completed: user.summary.completed,
    inProgress: user.summary.in_progress,
    needsAttention: user.summary.needs_reminder,
  }));

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
          System Statistics
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Overall system metrics and insights
        </Typography>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={2} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: "center" }}>
              <PeopleIcon sx={{ fontSize: 40, color: "#667eea", mb: 1 }} />
              <Typography variant="h5" sx={{ fontWeight: 600 }}>
                {stats.total_users}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Total Users
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: "center" }}>
              <SchoolIcon sx={{ fontSize: 40, color: "#667eea", mb: 1 }} />
              <Typography variant="h5" sx={{ fontWeight: 600 }}>
                {stats.total_courses}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Available Courses
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: "center" }}>
              <AssignmentIcon sx={{ fontSize: 40, color: "#667eea", mb: 1 }} />
              <Typography variant="h5" sx={{ fontWeight: 600 }}>
                {stats.total_enrollments}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Total Enrollments
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card
            sx={{
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            }}
          >
            <CardContent sx={{ textAlign: "center" }}>
              <CheckCircleIcon sx={{ fontSize: 40, color: "white", mb: 1 }} />
              <Typography variant="h5" sx={{ fontWeight: 600, color: "white" }}>
                {Math.round(stats.completion_rate)}%
              </Typography>
              <Typography
                variant="caption"
                sx={{ color: "rgba(255,255,255,0.9)" }}
              >
                Completion Rate
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts Section */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Course Status Distribution" />
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={courseStatusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) =>
                      `${name}: ${(percent * 100).toFixed(0)}%`
                    }
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {courseStatusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="User Progress Overview" />
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={userProgressData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="completed" fill="#4caf50" name="Completed" />
                  <Bar dataKey="inProgress" fill="#2196f3" name="In Progress" />
                  <Bar
                    dataKey="needsAttention"
                    fill="#f44336"
                    name="Needs Attention"
                  />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Job Control */}
      <Card>
        <CardHeader title="Run Reminder Job" avatar={<PlayArrowIcon />} />
        <CardContent>
          <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
            Manually trigger the daily reminder job to send emails to users who
            need attention
          </Typography>
          <Button
            variant="contained"
            size="large"
            onClick={runReminderJob}
            disabled={runningJob}
            sx={{
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              mb: 2,
            }}
          >
            {runningJob ? (
              <>
                <CircularProgress size={20} sx={{ mr: 1, color: "white" }} />
                Running Job...
              </>
            ) : (
              "Run Reminder Job"
            )}
          </Button>

          {jobResult && (
            <Alert
              severity={jobResult.success ? "success" : "error"}
              sx={{ mt: 2 }}
            >
              {jobResult.success ? (
                <Box>
                  <Typography
                    variant="subtitle2"
                    sx={{ fontWeight: 600, mb: 1 }}
                  >
                    ✅ Job Completed Successfully
                  </Typography>
                  <List dense>
                    <ListItem>
                      <ListItemText
                        primary={`Users Processed: ${jobResult.stats.users_processed}`}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary={`Users Needing Reminders: ${jobResult.stats.users_needing_reminders}`}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary={`Reminder Emails Sent: ${jobResult.stats.reminder_emails_sent}`}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary={`Manager Summaries Sent: ${jobResult.stats.manager_summaries_sent}`}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary={`Total Emails Sent: ${jobResult.stats.total_emails_sent}`}
                      />
                    </ListItem>
                  </List>
                </Box>
              ) : (
                <Box>
                  <Typography
                    variant="subtitle2"
                    sx={{ fontWeight: 600, mb: 1 }}
                  >
                    ❌ Job Failed
                  </Typography>
                  <Typography variant="body2">{jobResult.error}</Typography>
                </Box>
              )}
            </Alert>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}

export default Stats;
