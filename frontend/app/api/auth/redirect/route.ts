import { signIn } from '@/app/oauth/Auth'

export async function GET() {
  await signIn('microsoft-entra-id')
}
