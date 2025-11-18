'use client'
import { ReactNode } from 'react'
import { Tooltip as MUITooltip, IconButton, Box } from '@mui/material'
import { Info as InfoIcon } from '@mui/icons-material'

interface TooltipProps {
  content: string | ReactNode
  children: ReactNode
}

export default function Tooltip({ content, children }: TooltipProps) {
  return (
    <Box sx={{ position: 'relative', width: '100%' }}>
      {children}
      <MUITooltip
        title={content}
        arrow
        placement="top"
        sx={{
          position: 'absolute',
          top: 8,
          right: 8
        }}
      >
        <IconButton
          size="small"
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
            width: 20,
            height: 20,
            backgroundColor: 'rgba(0, 0, 0, 0.1)',
            '&:hover': {
              backgroundColor: 'rgba(0, 0, 0, 0.2)'
            }
          }}
        >
          <InfoIcon sx={{ fontSize: 14, color: '#666' }} />
        </IconButton>
      </MUITooltip>
    </Box>
  )
}