import React, { useEffect } from 'react';
import { ProfilePage } from '../auth';
import { useAuth } from '../auth';
import { saveReturnUrl } from '../utils/redirectUtils';

const AccountPage: React.FC = () => {
  const { state } = useAuth();

  useEffect(() => {
    if (state.isLoading) {
      return;
    }

    if (!state.isAuthenticated || !state.user) {
      if (typeof window !== 'undefined') {
        saveReturnUrl(window.location.pathname + window.location.search);
        window.location.replace('/login');
      }
    }
  }, [state.isAuthenticated, state.isLoading, state.user]);

  if (!state.isAuthenticated || !state.user) {
    return null;
  }

  return <ProfilePage />;
};

export default AccountPage;
