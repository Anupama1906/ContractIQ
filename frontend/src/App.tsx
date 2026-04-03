import { useState, useEffect } from 'react';
import { View, Notification } from './types';
import Layout from './components/Layout';
import AuditDashboard from './components/AuditDashboard';
import Anonymizer from './components/Anonymizer';
import Report from './components/Report';
import { motion, AnimatePresence } from 'motion/react';

type AppStep = 'upload' | 'audit' | 'report';

export default function App() {
  const [appStep, setAppStep] = useState<AppStep>(() => {
    const saved = localStorage.getItem('contractiq_app_step');
    return (saved as AppStep) || 'upload';
  });

  const [currentView, setCurrentView] = useState<View>(() => {
    const saved = localStorage.getItem('contractiq_view');
    return (saved as View) || 'anonymize';
  });
  const [finalReport, setFinalReport] = useState<string>(() => {
    return localStorage.getItem('contractiq_report') || '';
  });
  const [documentId, setDocumentId] = useState<string | null>(() => {
    return localStorage.getItem('contractiq_document_id');
  });

  useEffect(() => {
    localStorage.setItem('contractiq_app_step', appStep);
  }, [appStep]);

  useEffect(() => {
    localStorage.setItem('contractiq_view', currentView);
  }, [currentView]);

  useEffect(() => {
    localStorage.setItem('contractiq_report', finalReport);
  }, [finalReport]);

  const [notifications, setNotifications] = useState<Notification[]>(() => {
    const saved = localStorage.getItem('contractiq_notifications');
    if (saved) return JSON.parse(saved);
    return [
      {
        id: '1',
        documentName: '1.pdf',
        isRead: false,
        timestamp: new Date().toISOString()
      }
    ];
  });

  useEffect(() => {
    localStorage.setItem('contractiq_notifications', JSON.stringify(notifications));
  }, [notifications]);

  const markNotificationAsRead = (id: string) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, isRead: true } : n));
    setAppStep('report');
    setCurrentView('report');
  };

  const handleViewReport = (report: string) => {
    setFinalReport(report);
    setAppStep('report');
    setCurrentView('report');
  };

  const handleAnonymizeComplete = () => {
    const id = localStorage.getItem('contractiq_document_id');
    setDocumentId(id);
    setAppStep('audit');
    setCurrentView('audit');
  };

  const handleAdvanceStep = (step: AppStep) => {
    setAppStep(step);
  };

  const handleResetUpload = () => {
    setAppStep('upload');
    localStorage.removeItem('contractiq_entity_map');
    localStorage.removeItem('contractiq_document_id');
    localStorage.removeItem('contractiq_audit_data');
    setDocumentId(null);
    setFinalReport('');
  };

  const handleViewChange = (view: View) => {
    // Only allow navigation to views that are unlocked based on appStep
    if (view === 'anonymize') {
      setCurrentView('anonymize');
    } else if (view === 'audit' && appStep !== 'upload') {
      setCurrentView('audit');
    } else if (view === 'report' && appStep === 'report') {
      setCurrentView('report');
    }
    // Clicking locked tabs does nothing (no state changes)
  };

  const renderView = () => {
    switch (currentView) {
      case 'audit':
        return <AuditDashboard onViewReport={handleViewReport} documentId={documentId} />;
      case 'anonymize':
        return <Anonymizer onAudit={handleAnonymizeComplete} onResetUpload={handleResetUpload} />;
      case 'report':
        return <Report markdown={finalReport} documentId={documentId ?? ''} />;
      default:
        return <Anonymizer onAudit={handleAnonymizeComplete} onResetUpload={handleResetUpload} />;
    }
  };

  return (
    <Layout
      currentView={currentView}
      onViewChange={handleViewChange}
      appStep={appStep}
      notifications={notifications}
      onMarkAsRead={markNotificationAsRead}
    >
      <AnimatePresence mode="wait">
        <motion.div
          key={currentView}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.3, ease: "easeInOut" }}
        >
          {renderView()}
        </motion.div>
      </AnimatePresence>
    </Layout>
  );
}