/**
 * Centralized logging for the BETS frontend application.
 * Provides consistent log formatting with optional context.
 */

let logContext: string | undefined

/**
 * Set a context string that will be included in all subsequent log messages.
 * Useful for tracking operations across multiple log calls.
 * 
 * @param context - Context identifier (e.g., "MapVisualization", "API:fetchCases")
 */
export function setLogContext(context: string): void {
  logContext = context
}

/**
 * Clear the current log context.
 */
export function clearLogContext(): void {
  logContext = undefined
}

/**
 * Get the formatted context string for log messages.
 */
const getContext = (): string => (logContext ? ` [${logContext}] |` : '')

/**
 * Format a log message with optional additional data.
 */
const formatMessage = (level: string, message: unknown, data?: unknown): string => {
  const contextStr = getContext()
  let msg = `[${level}]${contextStr} ${message}`
  
  if (data !== undefined) {
    msg += ` | Data: ${JSON.stringify(data)}`
  }
  
  return msg
}

/**
 * TRACE level logging - Most detailed, for fine-grained debugging.
 * Use for tracking detailed execution flow.
 */
export function trace(message: unknown, data?: unknown): void {
  console.debug(formatMessage('TRACE', message, data))
}

/**
 * DEBUG level logging - Detailed information for debugging.
 * Use for diagnostic information during development.
 */
export function debug(message: unknown, data?: unknown): void {
  console.debug(formatMessage('DEBUG', message, data))
}

/**
 * INFO level logging - General informational messages.
 * Use for normal operations and state changes.
 */
export function info(message: unknown, data?: unknown): void {
  console.info(formatMessage('INFO', message, data))
}

/**
 * WARN level logging - Warning messages for potentially harmful situations.
 * Use for recoverable issues that should be investigated.
 */
export function warn(message: unknown, data?: unknown): void {
  console.warn(formatMessage('WARN', message, data))
}

/**
 * ERROR level logging - Error messages for serious issues.
 * Use for errors that affect functionality but don't crash the app.
 */
export function error(message: unknown, data?: unknown): void {
  console.error(formatMessage('ERROR', message, data))
}

/**
 * FATAL level logging - Critical errors that may crash the application.
 * Use for unrecoverable errors.
 */
export function fatal(message: unknown, data?: unknown): void {
  console.error(formatMessage('FATAL', message, data))
}

/**
 * Log an API request with consistent formatting.
 */
export function logApiRequest(method: string, url: string, params?: unknown): void {
  debug(`API ${method} ${url}`, params)
}

/**
 * Log an API response with consistent formatting.
 */
export function logApiResponse(method: string, url: string, status: number, data?: unknown): void {
  if (status >= 200 && status < 300) {
    debug(`API ${method} ${url} [${status}]`, data)
  } else if (status >= 400 && status < 500) {
    warn(`API ${method} ${url} [${status}]`, data)
  } else {
    error(`API ${method} ${url} [${status}]`, data)
  }
}

/**
 * Create a scoped logger that automatically includes context.
 * Useful for component-specific logging.
 * 
 * @param scope - The scope name (e.g., component name)
 * @returns An object with logging methods that include the scope
 */
export function createScopedLogger(scope: string) {
  return {
    trace: (message: unknown, data?: unknown) => {
      console.debug(formatMessage('TRACE', `[${scope}] ${message}`, data))
    },
    debug: (message: unknown, data?: unknown) => {
      console.debug(formatMessage('DEBUG', `[${scope}] ${message}`, data))
    },
    info: (message: unknown, data?: unknown) => {
      console.info(formatMessage('INFO', `[${scope}] ${message}`, data))
    },
    warn: (message: unknown, data?: unknown) => {
      console.warn(formatMessage('WARN', `[${scope}] ${message}`, data))
    },
    error: (message: unknown, data?: unknown) => {
      console.error(formatMessage('ERROR', `[${scope}] ${message}`, data))
    },
    fatal: (message: unknown, data?: unknown) => {
      console.error(formatMessage('FATAL', `[${scope}] ${message}`, data))
    },
  };
}

// Export an alias for 'error' to match the backend naming
export const err = error
// TODO double check this logging logic