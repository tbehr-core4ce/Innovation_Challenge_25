import { CustomError, notAuthorized } from '@/core/errors'
import { err } from '@/core/logging'

export function compareAuthentication(request: Request, expected?: string) {
  if (request.headers.get('Authorization') !== `Bearer ${expected}`)
    notAuthorized()
}

export async function handleAPIError(error: unknown) {
  if (error instanceof CustomError)
    return new Response(error.message, { status: error.status })

  if (typeof error === 'string') return new Response(error, { status: 400 })

  err(error?.toString())

  return new Response('Something went wrong on our end. Try again later.', {
    status: 500
  })
}
