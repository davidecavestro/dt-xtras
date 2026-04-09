import pino from 'pino'

// Create logger configuration based on environment
const isDevelopment = process.env.NODE_ENV === 'development'

// Configure pino logger
const logger = pino({
  level: isDevelopment ? 'debug' : 'info',
  transport: isDevelopment ? {
    target: 'pino-pretty',
    options: {
      colorize: true,
      translateTime: 'HH:MM:ss Z',
      ignore: 'pid,hostname'
    }
  } : undefined,
  browser: {
    transmit: {
      send: (level, logEvent) => {
        // In production, you might want to send logs to a service
        // For now, we'll just use console
        const msg = logEvent.messages.map(m => m.msg || m).join(' ')
        const levelUpper = level.toUpperCase()
        
        switch (level) {
          case 'error':
            console.error(`[${levelUpper}] ${msg}`, logEvent)
            break
          case 'warn':
            console.warn(`[${levelUpper}] ${msg}`, logEvent)
            break
          case 'info':
            console.info(`[${levelUpper}] ${msg}`, logEvent)
            break
          case 'debug':
            console.debug(`[${levelUpper}] ${msg}`, logEvent)
            break
          default:
            console.log(`[${levelUpper}] ${msg}`, logEvent)
        }
      }
    }
  }
})

// Create child loggers for different modules
export const createLogger = (module) => {
  return logger.child({ module })
}

// Export default logger
export default logger
