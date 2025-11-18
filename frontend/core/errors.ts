/**
 * Custom error handling for the BETS frontend application.
 * Provides consistent error types with automatic logging.
 */

import { debug, err } from './logging'

/**
 * Base custom error class for BETS application.
 * Automatically logs errors based on their severity (status code).
 */
export class CustomError extends Error {
  message: string
  status: number

  public constructor(message: string, status = 400, error?: unknown) {
    super(message)
    this.name = 'CustomError'
    this.message = message
    this.status = status

    // Log based on status code severity
    if (error) {
      const toLog = `${message}: ${error}`
      if (status >= 500) {
        err(toLog)
      } else {
        debug(toLog)
      }
    }
  }

  public toString(): string {
    return `${this.status}: ${this.message}`
  }
}

/**
 * API error with response details.
 */
export class ApiError extends CustomError {
  public readonly endpoint: string
  public readonly method: string
  public readonly responseData?: unknown

  public constructor(
    message: string,
    status: number,
    endpoint: string,
    method: string = 'GET',
    responseData?: unknown
  ) {
    super(message, status)
    this.name = 'ApiError'
    this.endpoint = endpoint
    this.method = method
    this.responseData = responseData

    err(
      `API Error: ${method} ${endpoint} [${status}] - ${message}`,
      responseData
    )
  }
}

/**
 * Validation error for form inputs or data validation.
 */
export class ValidationError extends CustomError {
  public readonly field?: string

  public constructor(message: string, field?: string) {
    super(message, 400)
    this.name = 'ValidationError'
    this.field = field
  }
}

/**
 * Error for missing required values.
 */
export class MissingValueError extends ValidationError {
  public constructor(fieldName: string) {
    super(`Must provide ${fieldName.toLowerCase()}`, fieldName)
    this.name = 'MissingValueError'
  }
}

/**
 * Authentication/authorization errors.
 */
export class AuthError extends CustomError {
  public constructor(message: string = 'Not authorized', status: number = 401) {
    super(message, status)
    this.name = 'AuthError'
  }
}

/**
 * Not found errors (404).
 */
export class NotFoundError extends CustomError {
  public readonly resource?: string

  public constructor(
    message: string = 'Resource not found',
    resource?: string
  ) {
    super(message, 404)
    this.name = 'NotFoundError'
    this.resource = resource
  }
}

// ============================================================================
// Convenience functions for common error patterns
// ============================================================================

/**
 * Throw an error for a failed operation.
 *
 * @param label - Description of what failed (e.g., "fetch cases", "load map")
 * @param error - Original error object
 * @param status - HTTP status code (default: 500)
 * @throws {CustomError} Always throws
 */
export function failed(label: string, error?: unknown, status = 500): never {
  throw new CustomError(`Failed to ${label.toLowerCase()}`, status, error)
}

/**
 * Ensure a required value is present, throw if not.
 *
 * @param value - The value to check
 * @param label - Name of the value for the error message
 * @throws {MissingValueError} If value is null, undefined, or empty string
 */
export function requireValue<T>(
  value: T | null | undefined,
  label: string
): asserts value is T {
  if (value === null || value === undefined || value === '') {
    throw new MissingValueError(label)
  }
}

/**
 * Convenience function for missing value errors.
 *
 * @param label - Name of the missing value
 * @throws {MissingValueError} Always throws
 */
export function noValue(label: string): never {
  throw new MissingValueError(label)
}

/**
 * Throw an authorization error.
 *
 * @param message - Optional custom message
 * @throws {AuthError} Always throws
 */
export function notAuthorized(message?: string): never {
  throw new AuthError(message)
}

/**
 * Throw an error for invalid parameters.
 *
 * @param message - Optional custom message
 * @throws {ValidationError} Always throws
 */
export function invalidParameters(
  message: string = 'Invalid parameters'
): never {
  throw new ValidationError(message)
}

/**
 * Throw a custom formatted error.
 *
 * @param message - Error message
 * @param status - HTTP status code
 * @param error - Original error object
 * @throws {CustomError} Always throws
 */
export function formatError(
  message: string,
  status = 400,
  error?: unknown
): never {
  throw new CustomError(message, status, error)
}

/**
 * Throw a not found error.
 *
 * @param resource - Name of the resource that wasn't found
 * @param identifier - Optional identifier for the resource
 * @throws {NotFoundError} Always throws
 */
export function notFound(
  resource: string,
  identifier?: string | number
): never {
  const message = identifier
    ? `${resource} not found: ${identifier}`
    : `${resource} not found`
  throw new NotFoundError(message, resource)
}

/**
 * Handle API errors consistently.
 * Converts fetch errors and HTTP errors into ApiError instances.
 *
 * @param error - The caught error
 * @param endpoint - API endpoint that was called
 * @param method - HTTP method used
 * @throws {ApiError} Always throws an ApiError
 */
export function handleApiError(
  error: unknown,
  endpoint: string,
  method: string = 'GET'
): never {
  if (error instanceof ApiError) {
    throw error
  }

  if (error instanceof Response) {
    throw new ApiError(
      error.statusText || 'API request failed',
      error.status,
      endpoint,
      method
    )
  }

  if (error instanceof Error) {
    throw new ApiError(error.message, 500, endpoint, method)
  }

  throw new ApiError('Unknown API error', 500, endpoint, method, error)
}

/**
 * Safe error message extraction.
 * Ensures we always get a string message from any error type.
 *
 * @param error - Any error object
 * @returns A string error message
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message
  }
  if (typeof error === 'string') {
    return error
  }
  return 'An unknown error occurred'
}

/**
 * Check if an error is a specific type.
 *
 * @param error - The error to check
 * @param errorType - The error class to check against
 * @returns True if the error is an instance of the specified type
 */
export function isErrorType<T extends Error>(
  error: unknown,
  errorType: new (...args: any[]) => T
): error is T {
  return error instanceof errorType
}
