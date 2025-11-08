import { ONE_DAY } from '@/core/constants'
import NextAuth, { NextAuthConfig, NextAuthResult } from 'next-auth'
import EntraID from 'next-auth/providers/microsoft-entra-id'

export const authOptions: NextAuthConfig = {
  providers: [
    EntraID({
      clientId: `${process.env.AZURE_CLIENT_ID}`,
      clientSecret: `${process.env.AZURE_CLIENT_SECRET}`,
      issuer: `https://login.microsoftonline.us/${process.env.AZURE_TENANT_ID}/v2.0`
    })
  ],
  trustHost: true,
  basePath: '/api/auth',
  session: {
    strategy: 'jwt',
    maxAge: ONE_DAY
  },
  pages: {
    signIn: '/api/auth/redirect'
  },
  callbacks: {
    jwt: async ({ token, account }) => {
      if (account?.id_token) {
        const { roles } = JSON.parse(atob(account.id_token.split('.')[1]))

        token.roles = roles
        token.accessToken = account.access_token
        token.idToken = account.id_token
        token.providerAccountId = account.providerAccountId
      }

      return token
    },
    redirect: ({ baseUrl }) => baseUrl,
    session: ({ session, token }) => ({
      ...session,
      sub: token.sub,
      roles: token.roles as string[],
      accessToken: token.accessToken as string,
      idToken: token.idToken as string,
      user: {
        ...session.user,
        providerAccountId: token.providerAccountId as string | undefined
      }
    }),
    authorized: ({ auth }) => Boolean(auth)
  }
}

const result = NextAuth(authOptions)

export const handlers: NextAuthResult['handlers'] = result.handlers
export const auth: NextAuthResult['auth'] = result.auth
export const signIn: NextAuthResult['signIn'] = result.signIn
export const signOut: NextAuthResult['signOut'] = result.signOut
