'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { BookOpen, MessageSquare, Settings, LogOut, User } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';

export const Navigation = () => {
  const pathname = usePathname();
  const router = useRouter();
  const { user, isAuthenticated, isAdmin, logout } = useAuth();

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  const navItems = [
    {
      name: 'Chat',
      href: '/chat',
      icon: MessageSquare,
      description: 'Ask questions about documents'
    }
  ];

  // Add Admin link only for admin users
  if (isAuthenticated && isAdmin) {
    navItems.push({
      name: 'Admin',
      href: '/admin',
      icon: Settings,
      description: 'Manage documents and system'
    });
  }

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <Link href="/" className="flex items-center px-4 text-lg font-semibold text-gray-900">
              <BookOpen className="h-6 w-6 mr-2 text-blue-600" />
              AI Academic Assistant
            </Link>
            
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;
                
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={cn(
                      'inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors',
                      isActive
                        ? 'border-blue-500 text-gray-900'
                        : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                    )}
                  >
                    <Icon className="h-4 w-4 mr-2" />
                    {item.name}
                  </Link>
                );
              })}
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {isAuthenticated && user && (
              <div className="flex items-center text-sm text-gray-600">
                <User className="h-4 w-4 mr-1" />
                <span>{user.username}</span>
                <span className="ml-1 px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-800">
                  {user.role}
                </span>
              </div>
            )}
            {isAuthenticated ? (
              <button 
                onClick={handleLogout}
                className="p-2 text-gray-400 hover:text-gray-500 transition-colors"
                title="Logout"
              >
                <LogOut className="h-5 w-5" />
              </button>
            ) : (
              <Link 
                href="/auth/login" 
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Login
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};
