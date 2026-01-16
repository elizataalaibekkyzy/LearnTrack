import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Grid,
  Card,
  CardContent,
  CardActionArea,
  Typography,
  Box,
  LinearProgress,
  Chip,
  CircularProgress,
  Alert,
  Button,
} from "@mui/material";
import {
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from "@mui/icons-material";
import apiService from "../services/api";

function Dashboard() {
  const [dashboardData, setDashboardData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const response = await apiService.getDashboard();
      setDashboardData(response.data);
      setError(null);
    } catch (err) {
      setError(
        "Failed to load dashboard data. Make sure the API server is running."
      );
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (needsAttentionCount) => {
    if (needsAttentionCount === 0) return "success";
    if (needsAttentionCount <= 2) return "warning";
    return "error";
  };

  const getStatusIcon = (needsAttentionCount) => {
    if (needsAttentionCount === 0)
      return <CheckCircleIcon sx={{ color: "#4caf50" }} />;
    if (needsAttentionCount <= 2)
      return <WarningIcon sx={{ color: "#ff9800" }} />;
    return <ErrorIcon sx={{ color: "#f44336" }} />;
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
        <Button variant="contained" onClick={fetchDashboard}>
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
          Dashboard Overview
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Real-time view of all users' learning progress
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {dashboardData.map((user) => (
          <Grid item xs={12} sm={6} md={4} key={user.user_id}>
            <Card
              onClick={() => navigate(`/users/${user.user_id}`)}
              sx={{
                height: "100%",
                cursor: "pointer",
                transition: "all 0.3s ease",
                "&:hover": {
                  transform: "translateY(-8px)",
                  boxShadow: "0 12px 24px rgba(0,0,0,0.15)",
                },
              }}
            >
              <CardActionArea sx={{ height: "100%" }}>
                <CardContent>
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "flex-start",
                      mb: 2,
                    }}
                  >
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {user.name}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {user.email}
                      </Typography>
                    </Box>
                    {getStatusIcon(user.needs_attention_count)}
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        mb: 1,
                      }}
                    >
                      <Typography variant="caption">Progress</Typography>
                      <Typography variant="caption" sx={{ fontWeight: 600 }}>
                        {Math.round(user.progress_percentage)}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={user.progress_percentage}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: "#ecf0f1",
                        "& .MuiLinearProgress-bar": {
                          borderRadius: 4,
                          background:
                            "linear-gradient(90deg, #667eea 0%, #764ba2 100%)",
                        },
                      }}
                    />
                  </Box>

                  <Grid container spacing={1} sx={{ mb: 2 }}>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="textSecondary">
                        Total Courses
                      </Typography>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {user.summary.total_courses}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="textSecondary">
                        Completed
                      </Typography>
                      <Typography
                        variant="h6"
                        sx={{ fontWeight: 600, color: "#4caf50" }}
                      >
                        {user.summary.completed}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="textSecondary">
                        In Progress
                      </Typography>
                      <Typography
                        variant="h6"
                        sx={{ fontWeight: 600, color: "#2196f3" }}
                      >
                        {user.summary.in_progress}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="textSecondary">
                        Needs Attention
                      </Typography>
                      <Typography
                        variant="h6"
                        sx={{ fontWeight: 600, color: "#f44336" }}
                      >
                        {user.needs_attention_count}
                      </Typography>
                    </Grid>
                  </Grid>

                  {user.needs_attention_count > 0 && (
                    <Chip
                      icon={<WarningIcon />}
                      label={`${user.needs_attention_count} course${
                        user.needs_attention_count !== 1 ? "s" : ""
                      } need attention`}
                      color="error"
                      size="small"
                      variant="outlined"
                      sx={{ width: "100%" }}
                    />
                  )}
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>

      {dashboardData.length === 0 && (
        <Box sx={{ textAlign: "center", py: 6 }}>
          <Typography color="textSecondary">
            No users found. Make sure the data files are loaded.
          </Typography>
        </Box>
      )}
    </Box>
  );
}

export default Dashboard;
