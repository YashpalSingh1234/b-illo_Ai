import React, { useState } from 'react';
import UserProfileMenu from '../UserProfileMenu/UserProfileMenu';
import type { User } from '../../types';
import './Header.css';

interface HeaderProps {
  user: User | null;
  sidebarCollapsed: boolean;
}

const Header: React.FC<HeaderProps> = ({ user, sidebarCollapsed }) => {
  const [showProfileMenu, setShowProfileMenu] = useState(false);


  return (
    <header className={`header ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      <div className="header-content">
        <div className="header-left">
          <h1 className="company-name">billo</h1>
        </div>
        
        <div className="header-right">
          <div className="user-profile-container">
            <button 
              className="user-profile-btn"
              onClick={() => setShowProfileMenu(!showProfileMenu)}
            >
              {user?.avatar ? (
                <img src={user.avatar} alt={user.firstName} className="user-avatar" />
              ) : (
                <div className="user-avatar-placeholder">
                  {user?.firstName?.charAt(0) || 'B'}
                </div>
              )}
            </button>
            
            {showProfileMenu && (
              <UserProfileMenu 
                user={user}
                onClose={() => setShowProfileMenu(false)}
              />
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
