let logContext: string | undefined

export function setLogContext(context: string) {
  logContext = context
}

const getContext = () => (logContext ? ` ${logContext} |` : '')

//Least harmful/most detailed
export function trace(message: unknown) {
  console.info(`[TRACE]${getContext()} ${message}`)
}

export function debug(message: unknown) {
  console.info(`[DEBUG]${getContext()} ${message}`)
}

export function info(message: unknown) {
  console.info(`[INFO]${getContext()} ${message}`)
}

export function warn(message: unknown) {
  console.warn(`[WARN]${getContext()} ${message}`)
}

export function err(message: unknown) {
  console.error(`[ERROR]${getContext()} ${message}`)
}
//Most harmful
export function fatal(message: unknown) {
  console.info(`[FATAL]${getContext()} ${message}`)
}
