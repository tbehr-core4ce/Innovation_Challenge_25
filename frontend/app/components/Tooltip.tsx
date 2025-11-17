'use client'
import { ReactNode } from 'react'

interface TooltipProps {
  content: string | ReactNode
  children: ReactNode
}

export default function Tooltip({ content, children }: TooltipProps) {
  return (
    <div className="relative inline-block w-full">
      {children}
      <div className="group absolute bottom-2 right-2">
        <div className="w-5 h-5 rounded-full bg-gray-300 hover:bg-gray-400 flex items-center justify-center cursor-help text-xs text-gray-600 font-semibold">
          ?
        </div>
        <div className="absolute bottom-full right-0 mb-2 hidden group-hover:block w-56 p-2 text-sm text-white bg-gray-800 rounded shadow-lg z-10">
          {content}
        </div>
      </div>
    </div>
  )
}