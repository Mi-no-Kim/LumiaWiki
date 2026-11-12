import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { appRoutes } from './app/App';
import { createAppQueryClient } from './app/queryClient';
import './style.css';

const devRoutes = import.meta.env.DEV ? (await import('./dev/routes')).foundationRoutes : [];
const router = createBrowserRouter(appRoutes(devRoutes));
const queryClient = createAppQueryClient();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}><RouterProvider router={router} /></QueryClientProvider>
  </StrictMode>,
);
