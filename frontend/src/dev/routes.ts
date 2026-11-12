import type { RouteObject } from 'react-router-dom';

export const foundationRoutes: RouteObject[] = [
  {
    path: '/__dev/foundation',
    lazy: async () => ({
      Component: (await import('./FoundationPage')).default,
    }),
  },
  {
    path: '/__dev/foundation/navigation',
    lazy: async () => ({
      Component: (await import('./NavigationPage')).default,
    }),
  },
];
