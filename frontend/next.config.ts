import type { NextConfig } from 'next'
import { webpack } from 'next/dist/compiled/webpack/webpack'
import classnamesMinifier from '@nimpl/classnames-minifier'
import {
  PHASE_DEVELOPMENT_SERVER,
  PHASE_PRODUCTION_SERVER
} from 'next/dist/shared/lib/constants'
import { join, resolve } from 'path'

const nextConfig: NextConfig = {
  experimental: {
    staleTimes: {
      dynamic: 10,
      static: 180
    }
  },
  reactStrictMode: false,
  webpack: (config: webpack.Configuration) => {
    config.resolve.fallback = {
      ...config.resolve.fallback,
      canvas: false,
      fs: false
    }

    // Need to disable these modules [see more](https://github.com/vercel/next.js/discussions/50177)
    config.plugins.push(
      new webpack.IgnorePlugin({
        resourceRegExp: /^pg-native$|^cloudflare:sockets$/
      })
    )

    config.resolve.alias = {
      '#icon': resolve('app', 'icon.png'),
      ...config.resolve.alias
    }

    return config
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '*.core4ce.com',
        port: '',
        search: ''
      }
    ]
  },
  output: 'standalone',
  outputFileTracingRoot: join(__dirname, './')
}

const minifyCss = (phase: string) =>
  classnamesMinifier({
    reservedNames: ['row', 'ad', 'body'],
    distDeletionPolicy: 'auto',
    disabled:
      phase === PHASE_DEVELOPMENT_SERVER || phase === PHASE_PRODUCTION_SERVER
  })

export default (phase: string) => minifyCss(phase)(nextConfig)
