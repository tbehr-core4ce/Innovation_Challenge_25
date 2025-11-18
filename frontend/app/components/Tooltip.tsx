'use client'
import { ReactNode } from 'react'
import { Tooltip as MUITooltip, IconButton, Box } from '@mui/material'
import { Info as InfoIcon } from '@mui/icons-material'

type TooltipPosition = 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left'

interface TooltipProps {
  content: string | ReactNode
  children: ReactNode
  position?: TooltipPosition
}

export default function Tooltip({
  content,
  children,
  position = 'bottom-right'
}: TooltipProps) {
  const getPositionStyles = (pos: TooltipPosition) => {
    switch (pos) {
      case 'top-right':
        return { top: 8, right: 8, placement: 'bottom' as const }
      case 'top-left':
        return { top: 8, left: 8, placement: 'bottom' as const }
      case 'bottom-right':
        return { bottom: 8, right: 8, placement: 'top' as const }
      case 'bottom-left':
        return { bottom: 8, left: 8, placement: 'top' as const }
    }
  }

  const { placement, ...positionStyles } = getPositionStyles(position)

  return (
    <Box sx={{ position: 'relative', width: '100%' }}>
      {children}
      <MUITooltip
        title={content}
        arrow
        placement={placement}
        sx={{
          position: 'absolute',
          ...positionStyles
        }}
      >
        <IconButton
          size="small"
          sx={{
            position: 'absolute',
            ...positionStyles,
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
