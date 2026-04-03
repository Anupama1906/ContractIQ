import { 
  Shield, 
  FileText, 
  BarChart3, 
  Bell, 
  Settings, 
  Search, 
  CheckCircle2, 
  Clock, 
  AlertTriangle, 
  ArrowRight,
  Upload,
  Eye,
  Lock,
  Download,
  History,
  ChevronRight,
  Loader2
} from 'lucide-react';

export type View = 'audit' | 'anonymize' | 'report';

export interface AuditLogEntry {
  id: string;
  type: 'SYSTEM' | 'LEGAL' | 'FINANCIAL' | 'COMPLIANCE' | 'OPERATIONAL';
  timestamp: string;
  message: string;
  status: 'completed' | 'waiting';
}

export interface RiskVector {
  label: string;
  value: number;
  color: string;
}

export interface Notification {
  id: string;
  documentName: string;
  isRead: boolean;
  timestamp: string;
}

export const AUDIT_STAGES = [
  { id: 'retrieve', label: 'Retrieve', status: 'completed' },
  { id: 'legal', label: 'Legal', status: 'completed' },
  { id: 'financial', label: 'Financial', status: 'completed' },
  { id: 'compliance', label: 'Compliance', status: 'active' },
  { id: 'operational', label: 'Operational', status: 'pending' },
  { id: 'data', label: 'Data', status: 'pending' },
  { id: 'termination', label: 'Termination', status: 'pending' },
  { id: 'evaluate', label: 'Evaluate', status: 'pending' },
];

export const MOCK_LOGS: AuditLogEntry[] = [
  {
    id: '1',
    type: 'SYSTEM',
    timestamp: '14:20:01',
    message: 'Global risk framework loaded and applied to the current document set.',
    status: 'completed'
  },
  {
    id: '2',
    type: 'LEGAL',
    timestamp: '14:21:12',
    message: 'Clause 8.4 presents significant indemnity risks for third-party software integration.',
    status: 'completed'
  },
  {
    id: '3',
    type: 'FINANCIAL',
    timestamp: '14:22:05',
    message: 'Missing payment escalation schedule could lead to unforecasted liability in Q4.',
    status: 'completed'
  },
  {
    id: '4',
    type: 'COMPLIANCE',
    timestamp: '14:23:45',
    message: 'GDPR data processing addendum is outdated and requires immediate rectification.',
    status: 'completed'
  },
  {
    id: '5',
    type: 'OPERATIONAL',
    timestamp: 'Waiting...',
    message: 'Awaiting previous stage finalization...',
    status: 'waiting'
  }
];

export const RISK_VECTORS: RiskVector[] = [
  { label: 'Legal', value: 0.85, color: 'bg-purple-500' },
  { label: 'Financial', value: 0.62, color: 'bg-blue-500' },
  { label: 'Compliance', value: 0.91, color: 'bg-teal-500' },
  { label: 'Operational', value: 0.34, color: 'bg-orange-500' },
  { label: 'Data', value: 0.48, color: 'bg-red-500' },
  { label: 'Termination', value: 0.15, color: 'bg-amber-500' },
];
