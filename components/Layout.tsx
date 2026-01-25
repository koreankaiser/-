
import React from 'react';
import Navigation from './Navigation';

interface LayoutProps {
  children: React.ReactNode;
  showNav?: boolean;
}

const Layout: React.FC<LayoutProps> = ({ children, showNav = true }) => {
  return (
    <div className="min-h-screen toss-bg-gray pb-24 max-w-2xl mx-auto shadow-sm">
      <main className="w-full">
        {children}
      </main>
      {showNav && <Navigation />}
    </div>
  );
};

export default Layout;
