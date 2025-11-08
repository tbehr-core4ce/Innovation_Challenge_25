import { DefaultSession, DefaultUser } from 'next-auth'

declare module 'next-auth' {
  export interface User extends DefaultUser {
    providerAccountId?: string
  }

  export interface Session extends DefaultSession {
    roles: string[]
    idToken: string
    accessToken: string
    user: User
  }
}
