import React from 'react';
import { User, Lock } from 'lucide-react';
import { View } from '../types';

type AppStep = 'upload' | 'audit' | 'report';

interface LayoutProps {
  children: React.ReactNode;
  currentView: View;
  onViewChange: (view: View) => void;
  appStep: AppStep;
}

export default function Layout({ children, currentView, onViewChange, appStep }: LayoutProps) {

  return (
    <div className="min-h-screen flex flex-col bg-surface">
      <header className="sticky top-0 z-50 bg-surface-container-lowest border-b border-outline-variant/20 px-8 py-4 flex justify-between items-center">
        <div className="flex items-center gap-8">
          <span className="text-xl font-bold tracking-tight text-on-surface font-headline">ContractIQ</span>
          <nav className="hidden md:flex gap-6 items-center">
            <button
              onClick={() => onViewChange('anonymize')}
              className={`text-sm font-medium transition-colors duration-200 pb-1 border-b-2 flex items-center gap-2 ${
                currentView === 'anonymize'
                  ? 'text-primary border-primary'
                  : 'text-on-surface-variant hover:text-on-surface border-transparent'
              }`}
            >
              Upload & anonymize
            </button>
            <button
              onClick={() => onViewChange('audit')}
              disabled={appStep === 'upload'}
              className={`text-sm font-medium transition-colors duration-200 pb-1 border-b-2 flex items-center gap-2 ${
                appStep === 'upload'
                  ? 'text-on-surface-variant/50 border-transparent cursor-not-allowed'
                  : currentView === 'audit'
                    ? 'text-primary border-primary'
                    : 'text-on-surface-variant hover:text-on-surface border-transparent'
              }`}
            >
              Audit
              {appStep === 'upload' && <Lock className="w-3 h-3" />}
            </button>
            <button
              onClick={() => onViewChange('report')}
              disabled={appStep !== 'report'}
              className={`text-sm font-medium transition-colors duration-200 pb-1 border-b-2 flex items-center gap-2 ${
                appStep !== 'report'
                  ? 'text-on-surface-variant/50 border-transparent cursor-not-allowed'
                  : currentView === 'report'
                    ? 'text-primary border-primary'
                    : 'text-on-surface-variant hover:text-on-surface border-transparent'
              }`}
            >
              Report
              {appStep !== 'report' && <Lock className="w-3 h-3" />}
            </button>
          </nav>
        </div>

        <div className="h-8 w-8 rounded-full overflow-hidden ghost-border bg-primary/10 flex items-center justify-center text-primary">
          <User className="w-5 h-5" />
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
