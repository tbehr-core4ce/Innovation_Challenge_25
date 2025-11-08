import { auth } from '@/app/oauth/Auth'
import { info } from '@/core/logging'
import { NextResponse } from 'next/server'
import { notAuthorized } from '@/core/errors'
import { NextAuthRequest } from 'next-auth'

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|sitemap.xml|icon.png|api/auth).*)'
  ]
}

const _WELCOME_PATHS = []

export default auth((request) => {
  if (!request.auth)
    return Response.redirect(new URL('/api/auth/redirect', request.url))

  // // Default Logging Section
  // const forwarded = request.headers.get('forwarded')

  // if (!forwarded) {
  //   info(
  //     `User is trying to ${request.method} ${request.nextUrl.pathname} and shown error`
  //   )

  //   return NextResponse.rewrite(new URL('/not-found', request.url))
  // }

  // const client = forwarded.split(';')

  // const ipString = client.find((info) => info.startsWith('for='))

  // if (!ipString) {
  //   info(
  //     `User is trying to ${request.method} ${request.nextUrl.pathname} and shown error`
  //   )

  //   return NextResponse.rewrite(new URL('/not-found', request.url))
  // }

  // const ip = ipString.slice(4)

  const email = request.auth.user?.email || 'Not Authorized'

  if (request.nextUrl.pathname.includes('/admin')) {
    try {
      isAdmin(request)

      info(
        ` - User ${email} is accessing ${request.method} ${request.nextUrl.pathname}`
      )
    } catch (error) {
      info(
        ` - User ${email} is trying to ${request.method} ${request.nextUrl.pathname} and shown error`
      )

      return NextResponse.rewrite(new URL('/not-found', request.url))
    }
  } else {
    info(
      ` - User ${email} is accessing ${request.method} ${request.nextUrl.pathname}`
    )
  }
})

function isAdmin(request: NextAuthRequest) {
  if (!request.auth?.roles) notAuthorized()

  const { roles } = request.auth

  if (
    !Array.isArray(roles) ||
    !roles.some((role) => role.toLowerCase() === 'admin.write')
  )
    notAuthorized()
}
