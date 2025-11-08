import { debug, err } from './logging'

export class CustomError extends Error {
  message: string
  status: number

  public constructor(message: string, status = 400, error?: unknown) {
    super()
    this.message = message
    this.status = status

    if (!error) return

    const toLog = `${message}: ${error}`

    if (status >= 500) {
      err(toLog)
    } else {
      debug(toLog)
    }
  }

  public toString() {
    return `${this.status}: ${this.message}`
  }
}

export function failed(label: string, error?: unknown, status = 500): never {
  throw new CustomError(`Failed ${label.toLowerCase()}`, status, error)
}

export function noValue(label: string): never {
  throw new CustomError(`Must provide ${label.toLowerCase()}`)
}

export function notAuthorized(): never {
  throw new CustomError('Not authorized', 401)
}

export function invalidParameters(): never {
  throw new CustomError('Invalid parameters')
}

export function formatError(
  message: string,
  status = 400,
  error?: unknown
): never {
  throw new CustomError(message, status, error)
}
