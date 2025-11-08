import { Session } from 'next-auth'

export const hasAdmin = (session: Session) => {
  return session.roles.some((role) => role.toLowerCase() === 'admin.write')
}
