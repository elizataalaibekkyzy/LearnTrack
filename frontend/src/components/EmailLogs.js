import React, { useState, useEffect } from "react";
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  Paper,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Chip,
  Pagination,
  Dialog,
  DialogTitle,
  DialogContent,
  Grid,
  CircularProgress,
  Alert,
  Button,
  useTheme,
  useMediaQuery,
} from "@mui/material";
import {
  Email as EmailIcon,
  Close as CloseIcon,
  Person as PersonIcon,
  Business as BusinessIcon,
} from "@mui/icons-material";
import apiService from "../services/api";

function EmailLogs() {
  const [logs, setLogs] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedLog, setSelectedLog] = useState(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));

  useEffect(() => {
    fetchLogs();
  }, [page]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const response = await apiService.getEmailLogs(page, 10);
      setLogs(response.data.logs);
      setTotalPages(response.data.total_pages);
      setError(null);
    } catch (err) {
      setError("Failed to load email logs");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getEmailTypeIcon = (type) => {
    return type === "user_reminder" ? <PersonIcon /> : <BusinessIcon />;
  };

  const getStatusTypeColor = (statusType) => {
    switch (statusType) {
      case "needs reminder":
        return "error";
      case "progressed":
        return "info";
      case "started":
        return "warning";
      case "completed":
        return "success";
      default:
        return "default";
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
        <Button variant="contained" onClick={fetchLogs}>
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
          Email Logs
        </Typography>
        <Typography variant="body1" color="textSecondary">
          View all sent email notifications and reminders
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={5}>
          <Paper>
            <List sx={{ maxHeight: "600px", overflow: "auto" }}>
              {logs.map((log, index) => (
                <ListItemButton
                  key={index}
                  selected={selectedLog === log}
                  onClick={() => setSelectedLog(log)}
                  sx={{
                    borderBottom: "1px solid #ecf0f1",
                    "&.Mui-selected": {
                      backgroundColor: "rgba(102, 126, 234, 0.1)",
                      borderLeft: "4px solid #667eea",
                    },
                  }}
                >
                  <ListItemIcon>{getEmailTypeIcon(log.type)}</ListItemIcon>
                  <ListItemText
                    primary={log.to}
                    secondary={formatDate(log.timestamp)}
                    primaryTypographyProps={{ variant: "body2" }}
                    secondaryTypographyProps={{ variant: "caption" }}
                  />
                </ListItemButton>
              ))}
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={7}>
          {selectedLog ? (
            <Card>
              <CardHeader
                title="Email Details"
                action={
                  <Button
                    size="small"
                    onClick={() => setSelectedLog(null)}
                    startIcon={<CloseIcon />}
                  />
                }
              />
              <CardContent>
                <Grid container spacing={2} sx={{ mb: 2 }}>
                  <Grid item xs={12}>
                    <Typography variant="caption" color="textSecondary">
                      To
                    </Typography>
                    <Typography variant="body2">{selectedLog.to}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="caption" color="textSecondary">
                      From
                    </Typography>
                    <Typography variant="body2">{selectedLog.from}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="caption" color="textSecondary">
                      Sent
                    </Typography>
                    <Typography variant="body2">
                      {formatDate(selectedLog.timestamp)}
                    </Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="caption" color="textSecondary">
                      Type
                    </Typography>
                    <Typography variant="body2">{selectedLog.type}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="caption" color="textSecondary">
                      Subject
                    </Typography>
                    <Typography variant="body2">
                      {selectedLog.subject}
                    </Typography>
                  </Grid>
                  {selectedLog.status_type && (
                    <Grid item xs={12}>
                      <Chip
                        label={selectedLog.status_type}
                        color={getStatusTypeColor(selectedLog.status_type)}
                        size="small"
                      />
                    </Grid>
                  )}
                  {selectedLog.course_ids && (
                    <Grid item xs={12}>
                      <Typography variant="caption" color="textSecondary">
                        Courses
                      </Typography>
                      <Box
                        sx={{
                          display: "flex",
                          gap: 1,
                          flexWrap: "wrap",
                          mt: 1,
                        }}
                      >
                        {selectedLog.course_ids.map((courseId) => (
                          <Chip
                            key={courseId}
                            label={courseId}
                            size="small"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    </Grid>
                  )}
                </Grid>

                <Box sx={{ mt: 3, pt: 2, borderTop: "1px solid #ecf0f1" }}>
                  <Typography
                    variant="subtitle2"
                    sx={{ fontWeight: 600, mb: 1 }}
                  >
                    Email Body
                  </Typography>
                  <Box
                    sx={{
                      backgroundColor: "#f8f9fa",
                      p: 2,
                      borderRadius: 1,
                      fontFamily: "monospace",
                      fontSize: "0.875rem",
                      lineHeight: 1.6,
                      maxHeight: "300px",
                      overflow: "auto",
                      whiteSpace: "pre-wrap",
                      wordWrap: "break-word",
                    }}
                  >
                    {selectedLog.body}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          ) : (
            <Paper sx={{ p: 3, textAlign: "center" }}>
              <EmailIcon sx={{ fontSize: 48, color: "#ccc", mb: 1 }} />
              <Typography color="textSecondary">
                Select an email to view details
              </Typography>
            </Paper>
          )}
        </Grid>
      </Grid>

      {totalPages > 1 && (
        <Box sx={{ display: "flex", justifyContent: "center", mt: 3 }}>
          <Pagination
            count={totalPages}
            page={page}
            onChange={(e, value) => setPage(value)}
          />
        </Box>
      )}

      {logs.length === 0 && (
        <Box sx={{ textAlign: "center", py: 6 }}>
          <Typography color="textSecondary">
            No email logs found. Run the reminder job to generate emails.
          </Typography>
        </Box>
      )}
    </Box>
  );
}

export default EmailLogs;
