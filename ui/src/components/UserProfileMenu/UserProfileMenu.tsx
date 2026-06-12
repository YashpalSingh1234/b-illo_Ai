import React, { useEffect, useRef } from 'react';
import type { User } from '../../types';
import './UserProfileMenu.css';

interface UserProfileMenuProps {
  user: User | null;
  onClose: () => void;
}

const UserProfileMenu: React.FC<UserProfileMenuProps> = ({ user, onClose }) => {
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [onClose]);

  const handleLogin = () => {
    console.log('Login clicked');
    onClose();
  };

  const handleLogout = () => {
    console.log('Logout clicked');
    onClose();
  };

  return (
    <div className="user-profile-menu" ref={menuRef}>
      {user ? (
        <>
          <div className="menu-header">
            <div className="user-info">
              <div className="user-name">{user.firstName}</div>
              <div className="user-email">{user.email}</div>
            </div>
          </div>
          <div className="menu-divider"></div>
          <button className="menu-item" onClick={handleLogout}>
            <span>🚪</span> Logout
          </button>
        </>
      ) : (
        <button className="menu-item" onClick={handleLogin}>
          <span>🔑</span> Login
        </button>
      )}
    </div>
  );
};

export default UserProfileMenu;
