'use client'

import React, { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Switch,
  FormControlLabel,
  FormGroup,
  Divider,
  Card,
  CardContent,
  Alert,
  Chip
} from '@mui/material'
import {
  DarkMode as DarkModeIcon,
  LightMode as LightModeIcon,
  Accessibility as AccessibilityIcon,
  Notifications as NotificationsIcon,
  Palette as PaletteIcon
} from '@mui/icons-material'

// Brand colors
const brandColors = {
  darkBlue: '#2C425A',
  darkOrange: '#F05323',
  lightBlueGray: '#E4E5ED'
}

export default function SettingsPage() {
  // State for settings
  const [darkMode, setDarkMode] = useState(false)
  const [highContrast, setHighContrast] = useState(false)
  const [largeText, setLargeText] = useState(false)
  const [notifications, setNotifications] = useState(true)
  const [soundAlerts, setSoundAlerts] = useState(false)

  return (
    <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 1200, mx: 'auto' }}>
      {/* Page Header */}
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h4"
          sx={{
            fontWeight: 700,
            color: brandColors.darkBlue,
            mb: 1
          }}
        >
          Settings
        </Typography>
        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
          Customize your BETS experience
        </Typography>
      </Box>

      {/* Info Alert */}
      <Alert severity="info" sx={{ mb: 3 }}>
        Settings are saved locally in your browser and will persist across
        sessions.
      </Alert>

      {/* Appearance Settings */}
      <Card sx={{ mb: 3, boxShadow: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <PaletteIcon
              sx={{ mr: 1.5, color: brandColors.darkOrange, fontSize: 28 }}
            />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Appearance
            </Typography>
            <Chip
              label="Coming Soon"
              size="small"
              sx={{ ml: 2 }}
              color="warning"
            />
          </Box>
          <Divider sx={{ mb: 2 }} />

          <FormGroup>
            <FormControlLabel
              control={
                <Switch
                  checked={darkMode}
                  onChange={(e) => setDarkMode(e.target.checked)}
                  color="primary"
                />
              }
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {darkMode ? (
                    <DarkModeIcon fontSize="small" />
                  ) : (
                    <LightModeIcon fontSize="small" />
                  )}
                  <Typography variant="body1">Dark Mode</Typography>
                </Box>
              }
            />
            <Typography
              variant="caption"
              sx={{ ml: 4, mt: -0.5, mb: 2, color: 'text.secondary' }}
            >
              Switch between light and dark themes for comfortable viewing
            </Typography>
          </FormGroup>
        </CardContent>
      </Card>

      {/* Accessibility Settings */}
      <Card sx={{ mb: 3, boxShadow: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <AccessibilityIcon
              sx={{ mr: 1.5, color: brandColors.darkOrange, fontSize: 28 }}
            />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Accessibility
            </Typography>
            <Chip
              label="Coming Soon"
              size="small"
              sx={{ ml: 2 }}
              color="warning"
            />
          </Box>
          <Divider sx={{ mb: 2 }} />

          <FormGroup>
            <FormControlLabel
              control={
                <Switch
                  checked={highContrast}
                  onChange={(e) => setHighContrast(e.target.checked)}
                  color="primary"
                />
              }
              label="High Contrast Mode"
            />
            <Typography
              variant="caption"
              sx={{ ml: 4, mt: -0.5, mb: 2, color: 'text.secondary' }}
            >
              Increase contrast for better visibility
            </Typography>

            <FormControlLabel
              control={
                <Switch
                  checked={largeText}
                  onChange={(e) => setLargeText(e.target.checked)}
                  color="primary"
                />
              }
              label="Large Text"
            />
            <Typography
              variant="caption"
              sx={{ ml: 4, mt: -0.5, mb: 1, color: 'text.secondary' }}
            >
              Increase text size for easier reading
            </Typography>
          </FormGroup>
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card sx={{ mb: 3, boxShadow: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <NotificationsIcon
              sx={{ mr: 1.5, color: brandColors.darkOrange, fontSize: 28 }}
            />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Notifications
            </Typography>
          </Box>
          <Divider sx={{ mb: 2 }} />

          <FormGroup>
            <FormControlLabel
              control={
                <Switch
                  checked={notifications}
                  onChange={(e) => setNotifications(e.target.checked)}
                  color="primary"
                />
              }
              label="Enable Notifications"
            />
            <Typography
              variant="caption"
              sx={{ ml: 4, mt: -0.5, mb: 2, color: 'text.secondary' }}
            >
              Receive alerts for critical H5N1 cases and outbreaks
            </Typography>

            <FormControlLabel
              control={
                <Switch
                  checked={soundAlerts}
                  onChange={(e) => setSoundAlerts(e.target.checked)}
                  color="primary"
                  disabled={!notifications}
                />
              }
              label="Sound Alerts"
            />
            <Typography
              variant="caption"
              sx={{ ml: 4, mt: -0.5, mb: 1, color: 'text.secondary' }}
            >
              Play sound when critical alerts are triggered
            </Typography>
          </FormGroup>
        </CardContent>
      </Card>

      {/* System Information */}
      <Paper sx={{ p: 3, backgroundColor: brandColors.lightBlueGray }}>
        <Typography
          variant="subtitle2"
          sx={{ color: brandColors.darkBlue, fontWeight: 600, mb: 2 }}
        >
          System Information
        </Typography>
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', sm: 'auto 1fr' },
            gap: 1.5
          }}
        >
          <Typography variant="body2" sx={{ fontWeight: 500 }}>
            Version:
          </Typography>
          <Typography variant="body2">1.0.0 - Prototype</Typography>

          <Typography variant="body2" sx={{ fontWeight: 500 }}>
            Product:
          </Typography>
          <Typography variant="body2">
            BETS - Bio-Event Tracking System
          </Typography>

          <Typography variant="body2" sx={{ fontWeight: 500 }}>
            Company:
          </Typography>
          <Typography variant="body2">core4ce</Typography>

          <Typography variant="body2" sx={{ fontWeight: 500 }}>
            Last Updated:
          </Typography>
          <Typography variant="body2">
            {new Date().toLocaleDateString()}
          </Typography>
        </Box>
      </Paper>
    </Box>
  )
}
