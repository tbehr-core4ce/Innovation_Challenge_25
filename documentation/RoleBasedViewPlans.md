In a project I am part of they use their pg database that IT can use to give perms to certain parts of the website to use. We can use this and convert to python?

```
export interface PermissionRecord {
  permission: string
  description: string
  readonly?: boolean
}

export interface PermissionSection {
  title: string
  description: string
  entries: (PermissionSection | PermissionRecord)[]
}

export const PERMISSION_SECTIONS = [
  {
    title: 'Manage Talent',
    description:
      'This is the features around searching talent, managing labor categories and creating staff lists',
    entries: [
      {
        permission: 'talent.search',
        description: 'Can search talent in the manage talent search tab.'
      },
      {
        permission: 'talent.employees.view',
        description:
          'Can browse all employees and their profile in the employees tab.'
      },
      {
        title: 'Labor Categories',
        description:
          'This is the feature that allows users to view and manage labor categories for staffing plan needs',
        entries: [
          {
            permission: 'talent.lcat.view',
            description: 'Can view all labor categories'
          },
          {
            permission: 'talent.lcat.upsert',
            description: 'Can create and update labor categories'
          },
          {
            permission: 'talent.lcat.delete',
            description: 'Can delete labor categories'
          },
          {
            permission: 'talent.lcat.tags.upsert',
            description:
              'Can create and update global tags for labor categories'
          },
          {
            permission: 'talent.lcat.tags.delete',
            description: 'Can delete global tags for labor categories'
          }
        ]
      }
    ]
  },
  {
    title: 'News',
    description: 'This is for the news feature',
    entries: [
      {
        permission: 'news.view',
        description: 'Can access the news section.'
      }
    ]
  },
  {
    title: 'Opportunities',
    description:
      'This is the feature set around searching and managing opportunities',
    entries: [
      {
        permission: 'opportunities.search',
        description:
          'Can search opportunities in the opportunities and hvt tabs.'
      },
      {
        permission: 'opportunities.view',
        description:
          'Can browse all employees and their profile in the employees tab.'
      },
      {
        permission: 'opportunities.lcats',
        description: 'Can assign and unassign labor categories to opportunity.'
      },
      {
        permission: 'opportunities.target',
        description: 'Can browse all opportunities in targets page.'
      }
    ]
  },
  {
    title: 'Administration',
    description:
      'This is administration features such as roles and permissions, and other administrative tasks',
    entries: [
      {
        title: 'Roles and Permissions',
        description:
          'This is the admin permissions for roles and permissions, this is readonly because onlyh the deault admin role can be granted these permissions',
        entries: [
          {
            permission: 'admin.roles.sync',
            readonly: true,
            description:
              'Can sync the MS Enterprise App with the Literacy Roles to update the apps known roles'
          },
          {
            permission: 'admin.roles.manage',
            readonly: true,
            description:
              'Can modify the permissions of existing roles, synced from the MS Enterprise role definitions'
          }
        ]
      }
    ]
  }
] as const satisfies readonly PermissionSection[]

// GPT magic to create the PermissionValue type from the tree of perm sections
type ExtractPermissions<T> =
  T extends ReadonlyArray<unknown>
    ? ExtractPermissions<T[number]>
    : T extends { permission: infer P extends string }
      ? P
      : T extends { entries: infer E }
        ? ExtractPermissions<E>
        : never

export type PermissionValue = ExtractPermissions<typeof PERMISSION_SECTIONS>

const createPermissionsList = (
  permissions: PermissionValue[],
  item: PermissionRecord | PermissionSection
): PermissionValue[] => {
  if ('permission' in item)
    return [...permissions, item.permission as PermissionValue]
  return item.entries.reduce(createPermissionsList, permissions)
}

export const PERMISSION_LIST: PermissionValue[] = PERMISSION_SECTIONS.reduce(
  createPermissionsList,
  []
)

```

Example Page / component
```
import { ensureAccess } from '@/utils/auth'
import SearchResults from './results'
import SearchFilters from './filters'
import { getLaborCategory } from '@literacy/postgres/services'
import { SearchProvider } from './provider'

interface Props {
  searchParams: Promise<{ lcat?: string }>
}

export default async function Page({ searchParams }: Props) {
  await ensureAccess({
    required: { all: ['talent.search'] },
    fallbacks: [
      {
        when: { all: ['talent.employees.view'] },
        href: '/talent/employees'
      },
      {
        when: { all: ['talent.lcat.view'] },
        href: '/talent/lcat'
      }
    ]
  })

  const { lcat: lcatId } = await searchParams

  const lcat = await getLaborCategory(lcatId)

  return (
    <SearchProvider loadedFilters={lcat}>
      <div className="flex flex-col gap-4">
        <SearchFilters title={lcat?.title} />
        <SearchResults />
      </div>
    </SearchProvider>
  )
}
```

```
import { auth } from '@/oauth/Auth'
import { PermissionTest } from '@/types/auth'
import { PermissionValue } from '@literacy/constants/postgres'
import { tryCatch } from '@literacy/utilities/error'
import { Session } from 'next-auth'
import { notFound, redirect } from 'next/navigation'

export function hasPerms(
  userPerms: PermissionValue[] = [],
  test: PermissionTest
) {
  return 'all' in test
    ? test.all.every((p) => userPerms.includes(p))
    : test.any.some((p) => userPerms.includes(p))
}

interface HasPermissionsSuccess {
  hasPermissions: (_permissions: PermissionTest) => boolean
  session: Session
  error?: undefined
}

interface HasPermissionsFailure {
  session: null
  error: true
  hasPermissions: null
}

export const getHasPermissions = async (): Promise<
  HasPermissionsSuccess | HasPermissionsFailure
> => {
  const { data: session, error } = await tryCatch(auth())

  if (error || !session || !session.permissions?.length)
    return { session: null, error: true, hasPermissions: null }

  const hasPermissions = (permissions: PermissionTest) =>
    hasPerms(session.permissions, permissions)

  return {
    hasPermissions,
    session
  }
}

type FallbackRule = {
  when: PermissionTest
  href: string
}

export async function ensureAccess(options: {
  required: PermissionTest
  fallbacks?: FallbackRule[]
}) {
  const { required, fallbacks } = options

  const session = await auth()

  if (!session || !session.permissions?.length) notFound()

  const perms = session.permissions

  if (hasPerms(perms, required)) return { session, permissions: perms }

  for (const rule of fallbacks ?? []) {
    if (hasPerms(perms, rule.when)) {
      redirect(rule.href)
    }
  }

  notFound()
}
```

```
import { OpportunityContext } from '@/Contexts/Opportunity/Context'
import { Guard } from '@/hooks/useHasPermissions'
import { Button } from '@literacy/components/components/ui/button'
import Link from 'next/link'
import { useContext } from 'react'

interface Props {
  id: number
}

export default function SearchLcat({ id }: Props) {
  const { opportunity } = useContext(OpportunityContext)

  return (
    <Guard required={{ all: ['talent.search'] }}>
      <Button variant="outline" size="sm">
        {opportunity.id < 0 ? (
          <a className="flex items-center" href={`/talent?lcat=${id}`}>
            Select
          </a>
        ) : (
          <Link
            className="flex items-center"
            href={`/opportunities/${opportunity.id}/staffplan?lcat=${id}`}
          >
            Select
          </Link>
        )}
      </Button>
    </Guard>
  )
}
```


```
'use client'

import { PermissionTest } from '@/types/auth'
import { useSession } from 'next-auth/react'
import { ComponentType, ReactElement } from 'react'
import type { JSX } from 'react'

//undefined permissions is treated as there are no permission requirements
export const useHasPermissions = (permissions: PermissionTest | undefined) => {
  const { data: session, status } = useSession()

  if (!permissions) return true

  if (status === 'loading') return false

  if (session === null) return false

  if ('all' in permissions)
    return permissions.all.every((p) => session?.permissions?.includes(p))

  return permissions.any.some((p) => session?.permissions?.includes(p))
}

export function withPermissionGuard<P extends JSX.IntrinsicAttributes>(
  WrappedComponent: ComponentType<P>,
  required: PermissionTest
): ComponentType<P> {
  return function GuardedComponent(props: P): ReactElement | null {
    const hasPermission = useHasPermissions(required)

    if (!hasPermission) return null

    return <WrappedComponent {...props} />
  }
}

export function Guard({
  required,
  children,
  fallback = <></>
}: {
  required?: PermissionTest
  children: React.ReactNode
  fallback?: React.ReactNode
}) {
  const ok = useHasPermissions(required)
  return ok ? <>{children}</> : <>{fallback}</>
}

```


```
import type * as React from 'react'
import { Sidebar } from '@literacy/components/components/ui/sidebar'
import { PermissionTest } from '@/types/auth'
import { AppSidebarClient, NavigationItem } from './client'
import { getHasPermissions } from '@/utils/auth'
import {
  Briefcase,
  Home,
  Newspaper,
  Search,
  Target,
  UserCheck
} from 'lucide-react'

const items: (NavigationItem & { permissions?: PermissionTest })[] = [
  {
    title: 'Home',
    Icon: <Home />,
    route: '/',
    type: 'dashboard'
  },
  {
    title: 'Find Targets',
    Icon: <Search />,
    route: '/targets',
    type: 'tool',
    permissions: {
      any: ['opportunities.target']
    }
  },
  {
    title: 'Manage Talent',
    Icon: <UserCheck />,
    route: '/talent',
    type: 'tool',
    permissions: {
      any: ['talent.employees.view', 'talent.lcat.view', 'talent.search']
    }
  },
  {
    title: 'News',
    Icon: <Newspaper />,
    route: '/news',
    type: 'tool',
    permissions: {
      any: ['news.view']
    }
  },


export async function AppSidebar({
  ...props
}: React.ComponentProps<typeof Sidebar>) {
  const { hasPermissions, error } = await getHasPermissions()

  if (error) return <AppSidebarClient items={[]} {...props} />

  const permittedItems = items
    .filter((item) => !item.permissions || hasPermissions(item.permissions))
    .map(({ permissions: _, ...rest }) => ({ ...rest }))

  return <AppSidebarClient items={permittedItems} {...props} />
}

```