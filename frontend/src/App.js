import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  useMediaQuery,
  useTheme,
  IconButton,
} from "@mui/material";
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  BarChart as BarChartIcon,
  Email as EmailIcon,
  Menu as MenuIcon,
  School as SchoolIcon,
} from "@mui/icons-material";
import { useNavigate, useLocation } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import UserList from "./components/UserList";
import UserDetail from "./components/UserDetail";
import EmailLogs from "./components/EmailLogs";
import Stats from "./components/Stats";

function AppContent() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  const menuItems = [
    { label: "Dashboard", path: "/", icon: <DashboardIcon /> },
    { label: "Users", path: "/users", icon: <PeopleIcon /> },
    { label: "Statistics", path: "/stats", icon: <BarChartIcon /> },
    { label: "Email Logs", path: "/emails", icon: <EmailIcon /> },
  ];

  const handleNavigate = (path) => {
    navigate(path);
    setMobileOpen(false);
  };

  const drawerContent = (
    <List>
      {menuItems.map((item) => (
        <ListItem
          key={item.path}
          disablePadding
          selected={location.pathname === item.path}
        >
          <ListItemButton
            onClick={() => handleNavigate(item.path)}
            selected={location.pathname === item.path}
            sx={{
              backgroundColor:
                location.pathname === item.path
                  ? "rgba(102, 126, 234, 0.1)"
                  : "transparent",
              "&.Mui-selected": {
                backgroundColor: "rgba(102, 126, 234, 0.1)",
                "& .MuiListItemIcon-root": {
                  color: "#667eea",
                },
                "& .MuiListItemText-primary": {
                  color: "#667eea",
                  fontWeight: 600,
                },
              },
            }}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItemButton>
        </ListItem>
      ))}
    </List>
  );

  return (
    <Box sx={{ display: "flex", minHeight: "100vh", flexDirection: "column" }}>
      <AppBar
        position="static"
        sx={{
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
        }}
      >
        <Toolbar>
          {isMobile && (
            <IconButton
              color="inherit"
              onClick={() => setMobileOpen(!mobileOpen)}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}
          <SchoolIcon sx={{ mr: 1, fontSize: 28 }} />
          <Typography variant="h5" sx={{ flexGrow: 1, fontWeight: 600 }}>
            LearnTrack
          </Typography>
          <Typography
            variant="caption"
            sx={{ display: { xs: "none", sm: "block" } }}
          >
            Learning & Development Management
          </Typography>
        </Toolbar>
      </AppBar>

      <Box sx={{ display: "flex", flex: 1 }}>
        {!isMobile && (
          <Drawer
            variant="permanent"
            sx={{
              width: 240,
              flexShrink: 0,
              "& .MuiDrawer-paper": {
                width: 240,
                boxSizing: "border-box",
                marginTop: 0,
              },
            }}
          >
            {drawerContent}
          </Drawer>
        )}

        {isMobile && (
          <Drawer
            anchor="left"
            open={mobileOpen}
            onClose={() => setMobileOpen(false)}
          >
            {drawerContent}
          </Drawer>
        )}

        <Container
          maxWidth="xl"
          sx={{
            flex: 1,
            py: 3,
            display: "flex",
            flexDirection: "column",
          }}
        >
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/users" element={<UserList />} />
            <Route path="/users/:userId" element={<UserDetail />} />
            <Route path="/stats" element={<Stats />} />
            <Route path="/emails" element={<EmailLogs />} />
          </Routes>
        </Container>
      </Box>

      <Box
        component="footer"
        sx={{
          backgroundColor: "#f5f5f5",
          py: 3,
          textAlign: "center",
          borderTop: "1px solid #ecf0f1",
        }}
      >
        <Typography variant="body2" color="textSecondary">
          LearnTrack © 2026 | Built for L&D Technical Interview
        </Typography>
      </Box>
    </Box>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
