'use client'

import React, { useState, useEffect } from 'react'
import { usePathname } from 'next/navigation'
import Link from 'next/link'
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  useMediaQuery,
  useTheme,
  Tooltip
} from '@mui/material'
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Map as MapIcon,
  Settings as SettingsIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon
} from '@mui/icons-material'

const drawerWidth = 260
const drawerCollapsedWidth = 70

// Brand colors from core4ce
const brandColors = {
  darkBlue: '#2C425A',
  darkOrange: '#F05323',
  lightBlueGray: '#E4E5ED',
  green: '#87AC9F',
  gray: '#DAD5CB',
  teal: '#D0EADF'
}

interface NavItem {
  text: string
  icon: React.ReactElement
  path: string
}

const navItems: NavItem[] = [
  {
    text: 'Dashboard',
    icon: <DashboardIcon />,
    path: '/dashboard'
  },
  {
    text: 'Map View',
    icon: <MapIcon />,
    path: '/map'
  },
  {
    text: 'Settings',
    icon: <SettingsIcon />,
    path: '/settings'
  }
]

export default function RoutesLayout({
  children
}: {
  children: React.ReactNode
}) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const pathname = usePathname()
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))

  // Load collapsed state from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('sidebarCollapsed')
    if (saved !== null) {
      setSidebarCollapsed(saved === 'true')
    }
  }, [])

  // Save collapsed state to localStorage
  useEffect(() => {
    localStorage.setItem('sidebarCollapsed', String(sidebarCollapsed))
  }, [sidebarCollapsed])

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen)
  }

  const handleSidebarToggle = () => {
    setSidebarCollapsed(!sidebarCollapsed)
  }

  const drawer = (
    <Box
      sx={{
        height: '100%',
        backgroundColor: brandColors.darkBlue,
        color: 'white',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      {/* Logo/Branding Section */}
      {!sidebarCollapsed ? (
        <Box
          sx={{
            p: 3,
            display: 'flex',
            flexDirection: 'column',
            gap: 0.5
          }}
        >
          <Typography
            variant="h4"
            sx={{
              fontWeight: 700,
              color: brandColors.darkOrange,
              letterSpacing: '0.5px'
            }}
          >
            BETS
          </Typography>
          <Typography
            variant="caption"
            sx={{
              color: brandColors.lightBlueGray,
              fontSize: '0.7rem',
              letterSpacing: '0.3px'
            }}
          >
            Bio-Event Tracking System
          </Typography>
          <Divider
            sx={{
              mt: 1,
              backgroundColor: brandColors.darkOrange,
              height: 2
            }}
          />
          <Typography
            variant="caption"
            sx={{
              color: brandColors.gray,
              fontSize: '0.65rem',
              mt: 1,
              fontStyle: 'italic'
            }}
          >
            Powered by core4ce
          </Typography>
        </Box>
      ) : (
        <Box
          sx={{
            p: 2,
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center'
          }}
        >
          <Typography
            variant="h5"
            sx={{
              fontWeight: 700,
              color: brandColors.darkOrange,
              letterSpacing: '0.5px'
            }}
          >
            B
          </Typography>
        </Box>
      )}

      <Divider sx={{ backgroundColor: 'rgba(255, 255, 255, 0.12)' }} />

      {/* Navigation Items */}
      <List sx={{ px: 1, pt: 2, flexGrow: 1 }}>
        {navItems.map((item) => {
          const isActive = pathname === item.path
          const navButton = (
            <ListItemButton
              component={Link}
              href={item.path}
              onClick={() => isMobile && setMobileOpen(false)}
              sx={{
                borderRadius: 2,
                py: 1.5,
                px: sidebarCollapsed ? 1.5 : 2,
                backgroundColor: isActive
                  ? brandColors.darkOrange
                  : 'transparent',
                '&:hover': {
                  backgroundColor: isActive
                    ? brandColors.darkOrange
                    : 'rgba(255, 255, 255, 0.08)'
                },
                transition: 'all 0.3s ease',
                justifyContent: sidebarCollapsed ? 'center' : 'flex-start'
              }}
            >
              <ListItemIcon
                sx={{
                  color: isActive ? 'white' : brandColors.lightBlueGray,
                  minWidth: sidebarCollapsed ? 'auto' : 40,
                  justifyContent: 'center'
                }}
              >
                {item.icon}
              </ListItemIcon>
              {!sidebarCollapsed && (
                <ListItemText
                  primary={item.text}
                  primaryTypographyProps={{
                    fontSize: '0.95rem',
                    fontWeight: isActive ? 600 : 400,
                    color: isActive ? 'white' : brandColors.lightBlueGray
                  }}
                />
              )}
            </ListItemButton>
          )

          return (
            <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
              {sidebarCollapsed ? (
                <Tooltip title={item.text} placement="right" arrow>
                  {navButton}
                </Tooltip>
              ) : (
                navButton
              )}
            </ListItem>
          )
        })}
      </List>

      {/* Toggle Button */}
      {!isMobile && (
        <Box
          sx={{
            px: 1,
            py: 2,
            borderTop: `1px solid rgba(255, 255, 255, 0.12)`
          }}
        >
          <IconButton
            onClick={handleSidebarToggle}
            sx={{
              width: '100%',
              color: brandColors.lightBlueGray,
              borderRadius: 2,
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.08)'
              }
            }}
          >
            {sidebarCollapsed ? <ChevronRightIcon /> : <ChevronLeftIcon />}
          </IconButton>
        </Box>
      )}

      {/* Footer Info */}
      {!sidebarCollapsed && (
        <Box
          sx={{
            p: 2,
            backgroundColor: 'rgba(0, 0, 0, 0.2)'
          }}
        >
          <Typography
            variant="caption"
            sx={{
              color: brandColors.gray,
              fontSize: '0.7rem',
              display: 'block'
            }}
          >
            H5N1 Surveillance
          </Typography>
          <Typography
            variant="caption"
            sx={{
              color: brandColors.lightBlueGray,
              fontSize: '0.65rem',
              display: 'block'
            }}
          >
            Version 1.0 - Prototype
          </Typography>
        </Box>
      )}
    </Box>
  )

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* Mobile AppBar */}
      {isMobile && (
        <AppBar
          position="fixed"
          sx={{
            width: '100%',
            backgroundColor: brandColors.darkBlue,
            zIndex: (theme) => theme.zIndex.drawer + 1
          }}
        >
          <Toolbar>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" noWrap component="div">
              BETS
            </Typography>
          </Toolbar>
        </AppBar>
      )}

      {/* Mobile Drawer (temporary - slides over content) */}
      {isMobile && (
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true // Better mobile performance
          }}
          sx={{
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              border: 'none'
            }
          }}
        >
          {drawer}
        </Drawer>
      )}

      {/* Desktop Sidebar (static - part of flex layout) */}
      {!isMobile && (
        <Box
          sx={{
            width: sidebarCollapsed ? drawerCollapsedWidth : drawerWidth,
            flexShrink: 0,
            position: 'relative',
            transition: 'width 0.3s ease'
          }}
        >
          {drawer}
        </Box>
      )}

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          minHeight: '100vh',
          backgroundColor: brandColors.lightBlueGray,
          mt: isMobile ? '64px' : 0
        }}
      >
        {children}
      </Box>
    </Box>
  )
}
