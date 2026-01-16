import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Chip,
  CircularProgress,
  Alert,
  Button,
  Avatar,
} from "@mui/material";
import {
  ArrowBack as ArrowBackIcon,
  CheckCircle as CheckCircleIcon,
  School as SchoolIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  Schedule as ScheduleIcon,
  PlayArrow as PlayArrowIcon,
  Done as DoneIcon,
} from "@mui/icons-material";
import apiService from "../services/api";

function UserDetail() {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [statuses, setStatuses] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchUserData();
  }, [userId]);

  const fetchUserData = async () => {
    try {
      setLoading(true);
      const [userRes, statusRes, summaryRes] = await Promise.all([
        apiService.getUser(userId),
        apiService.getUserStatus(userId),
        apiService.getUserSummary(userId),
      ]);

      setUser(userRes.data);
      setStatuses(statusRes.data);
      setSummary(summaryRes.data);
      setError(null);
    } catch (err) {
      setError("Failed to load user data");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusChipColor = (status) => {
    switch (status) {
      case "completed":
        return "success";
      case "progressed":
        return "info";
      case "started":
        return "warning";
      case "needs reminder":
        return "error";
      default:
        return "default";
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "completed":
        return <CheckCircleIcon sx={{ fontSize: 18 }} />;
      case "progressed":
        return <TrendingUpIcon sx={{ fontSize: 18 }} />;
      case "started":
        return <PlayArrowIcon sx={{ fontSize: 18 }} />;
      case "needs reminder":
        return <WarningIcon sx={{ fontSize: 18 }} />;
      default:
        return <ScheduleIcon sx={{ fontSize: 18 }} />;
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
        <Button variant="contained" onClick={fetchUserData}>
          Retry
        </Button>
      </Box>
    );
  }

  if (!user) {
    return <Alert severity="warning">User not found</Alert>;
  }

  return (
    <Box>
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate("/users")}
        sx={{ mb: 3 }}
      >
        Back to Users
      </Button>

      <Card sx={{ mb: 3, backgroundColor: "#f9f9f9" }}>
        <CardContent>
          <Box sx={{ display: "flex", gap: 3, alignItems: "flex-start" }}>
            <Avatar
              sx={{
                width: 80,
                height: 80,
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                fontSize: 32,
                fontWeight: 600,
              }}
            >
              {user.name.charAt(0).toUpperCase()}
            </Avatar>

            <Box sx={{ flex: 1 }}>
              <Typography variant="h5" sx={{ fontWeight: 600, mb: 1 }}>
                {user.name}
              </Typography>
              <Typography
                variant="body2"
                color="textSecondary"
                sx={{ mb: 0.5 }}
              >
                {user.email}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Manager: {user.manager_email} | Hired:{" "}
                {new Date(user.hire_date).toLocaleDateString()}
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {summary && (
        <Grid container spacing={2} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: "center" }}>
                <SchoolIcon
                  sx={{
                    fontSize: 40,
                    color: "#667eea",
                    mb: 1,
                  }}
                />
                <Typography variant="h5" sx={{ fontWeight: 600 }}>
                  {summary.total_courses}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Total Courses
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: "center" }}>
                <CheckCircleIcon
                  sx={{
                    fontSize: 40,
                    color: "#4caf50",
                    mb: 1,
                  }}
                />
                <Typography
                  variant="h5"
                  sx={{ fontWeight: 600, color: "#4caf50" }}
                >
                  {summary.completed}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Completed
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: "center" }}>
                <TrendingUpIcon
                  sx={{
                    fontSize: 40,
                    color: "#2196f3",
                    mb: 1,
                  }}
                />
                <Typography
                  variant="h5"
                  sx={{ fontWeight: 600, color: "#2196f3" }}
                >
                  {summary.in_progress}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  In Progress
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: "center" }}>
                <WarningIcon
                  sx={{
                    fontSize: 40,
                    color: "#f44336",
                    mb: 1,
                  }}
                />
                <Typography
                  variant="h5"
                  sx={{ fontWeight: 600, color: "#f44336" }}
                >
                  {summary.needs_reminder}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Needs Attention
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
        Course Status Details
      </Typography>

      <Box sx={{ display: "grid", gap: 2 }}>
        {statuses.map((status) => (
          <Card key={status.course_id}>
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
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                    {status.course_id}
                  </Typography>
                  <Chip
                    icon={getStatusIcon(status.status)}
                    label={status.status}
                    color={getStatusChipColor(status.status)}
                    size="small"
                  />
                </Box>
                {status.days_overdue > 0 && (
                  <Chip
                    icon={<WarningIcon />}
                    label={`${status.days_overdue} days overdue`}
                    color="error"
                    variant="outlined"
                    size="small"
                  />
                )}
              </Box>

              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                {status.message}
              </Typography>

              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Box>
                    <Typography variant="caption" color="textSecondary">
                      Enrolled
                    </Typography>
                    <Typography variant="body2">
                      {new Date(
                        status.enrollment.enrollment_date
                      ).toLocaleDateString()}
                    </Typography>
                  </Box>
                </Grid>

                {status.enrollment.start_date && (
                  <Grid item xs={12} sm={6}>
                    <Box>
                      <Typography variant="caption" color="textSecondary">
                        Started
                      </Typography>
                      <Typography variant="body2">
                        {new Date(
                          status.enrollment.start_date
                        ).toLocaleDateString()}
                      </Typography>
                    </Box>
                  </Grid>
                )}

                {status.enrollment.completion_date && (
                  <Grid item xs={12} sm={6}>
                    <Box>
                      <Typography variant="caption" color="textSecondary">
                        Completed
                      </Typography>
                      <Typography variant="body2">
                        {new Date(
                          status.enrollment.completion_date
                        ).toLocaleDateString()}
                      </Typography>
                    </Box>
                  </Grid>
                )}

                <Grid item xs={12} sm={6}>
                  <Box>
                    <Typography variant="caption" color="textSecondary">
                      Deadline
                    </Typography>
                    <Typography variant="body2">
                      {status.schedule.days_to_complete} days | Batch{" "}
                      {status.schedule.batch}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        ))}
      </Box>
    </Box>
  );
}

export default UserDetail;
