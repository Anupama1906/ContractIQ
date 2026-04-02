import React, { useState, useRef, useEffect } from 'react';
import { Bell, FileText, User } from 'lucide-react';
import { View, Notification } from '../types';

interface LayoutProps {
  children: React.ReactNode;
  currentView: View;
  onViewChange: (view: View) => void;
  notifications: Notification[];
  onMarkAsRead: (id: string) => void;
}

export default function Layout({ children, currentView, onViewChange, notifications, onMarkAsRead }: LayoutProps) {
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const unreadCount = notifications.filter(n => !n.isRead).length;

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsNotificationsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-surface">
      <header className="sticky top-0 z-50 bg-surface-container-lowest border-b border-outline-variant/20 px-8 py-4 flex justify-between items-center">
        <div className="flex items-center gap-8">
          <span className="text-xl font-bold tracking-tight text-on-surface font-headline">ContractIQ</span>
          <nav className="hidden md:flex gap-6 items-center">
            <button 
              onClick={() => onViewChange('anonymize')}
              className={`text-sm font-medium transition-colors duration-200 pb-1 border-b-2 ${
                currentView === 'anonymize' 
                  ? 'text-primary border-primary' 
                  : 'text-on-surface-variant hover:text-on-surface border-transparent'
              }`}
            >
              Upload & anonymize
            </button>
            <button 
              onClick={() => onViewChange('audit')}
              className={`text-sm font-medium transition-colors duration-200 pb-1 border-b-2 ${
                currentView === 'audit' 
                  ? 'text-primary border-primary' 
                  : 'text-on-surface-variant hover:text-on-surface border-transparent'
              }`}
            >
              Audit
            </button>
            <button 
              onClick={() => onViewChange('report')}
              className={`text-sm font-medium transition-colors duration-200 pb-1 border-b-2 ${
                currentView === 'report' 
                  ? 'text-primary border-primary' 
                  : 'text-on-surface-variant hover:text-on-surface border-transparent'
              }`}
            >
              Report
            </button>
          </nav>
        </div>

        <div className="flex items-center gap-4">
          <div className="relative" ref={dropdownRef}>
            <button 
              onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
              className="p-2 text-on-surface-variant hover:bg-surface-container-low rounded-full transition-colors relative"
            >
              <Bell className="w-5 h-5" />
              {unreadCount > 0 && (
                <span className="absolute top-0 right-0 bg-error text-white text-[9px] font-bold h-4 min-w-[16px] flex items-center justify-center rounded-full border-2 border-white">
                  {unreadCount}
                </span>
              )}
            </button>

            {isNotificationsOpen && (
              <div className="absolute right-0 mt-2 w-80 bg-surface-container-lowest editorial-card shadow-xl z-[60] overflow-hidden">
                <div className="p-4 border-b border-outline-variant/20 bg-surface-container-low">
                  <h3 className="font-headline font-bold text-sm">Notifications</h3>
                </div>
                <div className="max-h-96 overflow-y-auto">
                  {notifications.length === 0 ? (
                    <div className="p-8 text-center text-on-surface-variant text-sm italic">
                      No notifications yet
                    </div>
                  ) : (
                    notifications.map((n) => (
                      <button
                        key={n.id}
                        onClick={() => {
                          onMarkAsRead(n.id);
                          setIsNotificationsOpen(false);
                        }}
                        className={`w-full text-left p-4 hover:bg-surface-container-low transition-colors flex gap-3 items-start border-b border-outline-variant/10 last:border-0 ${
                          !n.isRead ? 'bg-primary/5' : ''
                        }`}
                      >
                        <div className={`p-2 rounded-lg ${!n.isRead ? 'bg-primary/10 text-primary' : 'bg-surface-container text-on-surface-variant'}`}>
                          <FileText className="w-4 h-4" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className={`text-xs leading-relaxed ${!n.isRead ? 'font-semibold text-on-surface' : 'text-on-surface-variant'}`}>
                            Risk report for the document <span className="text-primary">{n.documentName}</span> is finalized. Go to Report View.
                          </p>
                          <span className="text-[10px] text-on-surface-variant mt-1 block">
                            {new Date(n.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                        {!n.isRead && (
                          <div className="w-2 h-2 rounded-full bg-primary mt-1.5 flex-shrink-0" />
                        )}
                      </button>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
          <div className="h-8 w-8 rounded-full overflow-hidden ghost-border ml-2 bg-primary/10 flex items-center justify-center text-primary">
            <User className="w-5 h-5" />
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto w-full px-8 py-8">
        {children}
      </main>

      <footer className="px-8 py-6 flex justify-between items-center text-on-surface-variant text-[11px] font-medium border-t border-outline-variant/10">
        <div className="flex gap-4">
          <a className="hover:text-on-surface transition-colors" href="#">Privacy Policy</a>
          <a className="hover:text-on-surface transition-colors" href="#">Audit Methodology</a>
        </div>
        <div>
          © 2024 ContractIQ Intelligent Ledger. All agents verified.
        </div>
      </footer>
    </div>
  );
}
