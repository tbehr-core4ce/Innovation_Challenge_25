//Generic zod types
import { z } from 'zod'

export const sharepointId = z.string().min(8).max(250)

export const weaviateBackupId = z.string().length(25)
