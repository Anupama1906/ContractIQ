import { useState, useEffect } from 'react';
import { View, Notification } from './types';
import Layout from './components/Layout';
import AuditDashboard from './components/AuditDashboard';
import Anonymizer from './components/Anonymizer';
import Report from './components/Report';
import { motion, AnimatePresence } from 'motion/react';

export default function App() {
  const [currentView, setCurrentView] = useState<View>(() => {
    const saved = localStorage.getItem('contractiq_view');
    return (saved as View) || 'audit';
  });
  const [finalReport, setFinalReport] = useState<string>(() => {
    return localStorage.getItem('contractiq_report') || '';
  });
  const [documentId, setDocumentId] = useState<string | null>(() => {
    return localStorage.getItem('contractiq_document_id');
  });

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
    setCurrentView('report');
  };

  const handleViewReport = (report: string) => {
    setFinalReport(report);
    setCurrentView('report');
  };

  const handleAnonymizeComplete = () => {
    const id = localStorage.getItem('contractiq_document_id');
    setDocumentId(id);
    setCurrentView('audit');
  };

  const renderView = () => {
    switch (currentView) {
      case 'audit':
        return <AuditDashboard onViewReport={handleViewReport} documentId={documentId} />;
      case 'anonymize':
        return <Anonymizer onAudit={handleAnonymizeComplete} />;
      case 'report':
        return <Report markdown={finalReport} />;
      default:
        return <AuditDashboard onViewReport={handleViewReport} documentId={documentId} />;
    }
  };

  return (
    <Layout 
      currentView={currentView} 
      onViewChange={setCurrentView}
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
