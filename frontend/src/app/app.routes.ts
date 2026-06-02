import { Routes } from '@angular/router';

import { Dashboard } from './pages/dashboard/dashboard';
import { SettingsPage } from './pages/settings-page/settings-page';

export const routes: Routes = [
  {
    path: '',
    component: Dashboard,
  },
  {
    path: 'settings',
    component: SettingsPage,
  },
];
