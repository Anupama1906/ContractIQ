import { motion } from 'motion/react';
import { CheckCircle2, Loader2, ArrowRight } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';

const AUDIT_STAGES_BASE = [
  { id: 'retrieve', label: 'Retrieve' },
  { id: 'legal', label: 'Legal' },
  { id: 'financial', label: 'Financial' },
  { id: 'compliance', label: 'Compliance' },
  { id: 'operational', label: 'Operational' },
  { id: 'data', label: 'Data' },
  { id: 'termination', label: 'Termination' },
  { id: 'evaluate', label: 'Evaluate' },
];

const AGENT_COLORS: Record<string, string> = {
  legal: 'text-purple-700 bg-purple-50 border-purple-500',
  financial: 'text-blue-700 bg-blue-50 border-blue-500',
  compliance: 'text-teal-700 bg-teal-50 border-teal-500',
  operational: 'text-orange-700 bg-orange-50 border-orange-500',
  data: 'text-red-700 bg-red-50 border-red-500',
  termination: 'text-amber-700 bg-amber-50 border-amber-500',
  evaluate: 'text-green-700 bg-green-50 border-green-500',
  system: 'text-gray-500 bg-gray-50 border-gray-400',
};

interface LogEntry {
  id: string;
  agent: string;
  timestamp: string;
  message: string;
}

interface AuditData {
  currentIndex: number;
  logs: LogEntry[];
  isComplete: boolean;
  finalReport: string;
  riskScores: Record<string, number>;
  documentId: string;
  finalRiskScore: number | null;
}

export default function AuditDashboard({ onViewReport, documentId }: { onViewReport: (report: string) => void, documentId: string | null }) {
  const [currentIndex, setCurrentIndex] = useState<number>(-1);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isComplete, setIsComplete] = useState(false);
  const [finalReport, setFinalReport] = useState<string>("");
  const [finalRiskScore, setFinalRiskScore] = useState<number | null>(null);
  const [riskScores, setRiskScores] = useState<Record<string, number>>({
    legal: 0,
    financial: 0,
    compliance: 0,
    operational: 0,
    data: 0,
    termination: 0,
  });
  const [hasLoadedCache, setHasLoadedCache] = useState(false);

  const logEndRef = useRef<HTMLDivElement>(null);

  // Load cached audit data if it exists for this documentId
  useEffect(() => {
    if (!documentId || hasLoadedCache) return;

    const cached = localStorage.getItem('contractiq_audit_data');
    if (cached) {
      try {
        const auditData: AuditData = JSON.parse(cached);
        // Only restore cache if it's for the same documentId
        if (auditData.documentId === documentId) {
          setCurrentIndex(auditData.currentIndex);
          setLogs(auditData.logs);
          setIsComplete(auditData.isComplete);
          setFinalReport(auditData.finalReport);
          setFinalRiskScore(auditData.finalRiskScore);
          setRiskScores(auditData.riskScores);
          setHasLoadedCache(true);
          return;
        }
      } catch (err) {
        console.error("Error loading cached audit data:", err);
      }
    }

    setHasLoadedCache(true);
  }, [documentId, hasLoadedCache]);

  // Auto-scroll the analysis log as new agents report in
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  // Main Streaming Logic
  useEffect(() => {
    if (!documentId || !hasLoadedCache || currentIndex !== -1) return;

    const startLiveAudit = async () => {
      try {
        const response = await fetch('http://localhost:8000/contracts/evaluate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ document_id: documentId })
        });

        if (!response.body) return;

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        setCurrentIndex(0); // Start the visual pipeline

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n').filter(line => line.trim() !== '');

          lines.forEach(line => {
            const stepData = JSON.parse(line);
            
            // 1. Process Agent Comments
            if (stepData.comments && stepData.comments.length > 0) {
              const cleanMessage = stepData.comments[0].replace(/^\[.*?\]\s*/, '');
              setLogs(prev => [...prev, {
                id: Math.random().toString(36).substr(2, 9),
                agent: stepData.agent,
                timestamp: new Date().toLocaleTimeString('en-GB', { hour12: false }),
                message: cleanMessage,
              }]);
            }

            // 2. Update Risk Scores & UI Progression
            if (stepData.agent !== 'evaluate') {
              setRiskScores(prev => ({
                ...prev,
                [stepData.agent]: stepData.risk_score
              }));
              // Increment index to show progress in the top pipeline
              setCurrentIndex(prev => prev + 1);
            }

            // 3. Finalize Evaluation
            if (stepData.agent === 'evaluate') {
              setFinalReport(stepData.final_report || "");
              setFinalRiskScore(stepData.risk_score ?? null);
              setIsComplete(true);
              setCurrentIndex(8); // Jump to final stage in UI
            }
          });
        }
      } catch (err) {
        console.error("Audit Stream Error:", err);
      }
    };

    startLiveAudit();
  }, [documentId, hasLoadedCache]);

  // Persist audit data to localStorage whenever it changes
  useEffect(() => {
    if (!documentId || currentIndex === -1) return;

    const auditData: AuditData = {
      currentIndex,
      logs,
      isComplete,
      finalReport,
      finalRiskScore,
      riskScores,
      documentId,
    };

    localStorage.setItem('contractiq_audit_data', JSON.stringify(auditData));
  }, [currentIndex, logs, isComplete, finalReport, finalRiskScore, riskScores, documentId]);

  const getStageStatus = (stageId: string) => {
    if (stageId === 'retrieve') return 'completed';
    const stageIndex = AUDIT_STAGES_BASE.findIndex(s => s.id === stageId);
    if (stageIndex < currentIndex) return 'completed';
    if (stageIndex === currentIndex) return 'active';
    return 'pending';
  };

  const getVerdict = (score: number) => {
    if (score >= 0.7) return { label: 'High risk — escalation required', color: 'text-error', bgColor: 'bg-error-container/10', borderColor: 'border-error' };
    if (score >= 0.4) return { label: 'Moderate risk — review recommended', color: 'text-amber-600', bgColor: 'bg-amber-50', borderColor: 'border-amber-500' };
    return { label: 'Low risk — approved', color: 'text-green-600', bgColor: 'bg-green-50', borderColor: 'border-green-500' };
  };

  const verdict = isComplete && finalRiskScore !== null ? getVerdict(finalRiskScore) : null;

  return (
    <div className="flex flex-col gap-8">
      {/* Pipeline Tracker */}
      <section className="w-full py-2">
        <div className="flex items-center justify-between w-full relative">
          <div className="absolute top-[12px] -translate-y-1/2 left-[6.25%] right-[6.25%] h-[1.5px] flex z-0">
            {AUDIT_STAGES_BASE.slice(0, -1).map((stage, index) => {
              const status = getStageStatus(stage.id);
              const nextStatus = getStageStatus(AUDIT_STAGES_BASE[index + 1].id);
              let lineColor = 'bg-gray-200';
              if (status === 'active' || (status === 'completed' && nextStatus !== 'pending')) {
                lineColor = status === 'active' ? 'bg-primary' : 'bg-green-500';
              }
              return <div key={`line-${stage.id}`} className={`flex-1 h-full transition-colors duration-500 ${lineColor}`} />;
            })}
          </div>

          {AUDIT_STAGES_BASE.map((stage, index) => {
            const status = getStageStatus(stage.id);
            return (
              <div key={stage.id} className="flex flex-col items-center gap-2 flex-1">
                <div className="relative flex items-center justify-center">
                  {status === 'active' && (
                    <motion.div animate={{ scale: [1, 1.6, 1], opacity: [0.6, 0, 0.6] }} transition={{ duration: 2, repeat: Infinity }} className="absolute w-7 h-7 rounded-full bg-primary/40" />
                  )}
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center transition-all duration-300 z-10 ${status === 'completed' ? 'bg-green-500 text-white' : status === 'active' ? 'bg-primary text-white shadow-sm shadow-primary/20' : 'bg-surface border-2 border-outline-variant text-on-surface-variant'}`}>
                    {status === 'completed' ? <CheckCircle2 className="w-4 h-4" /> : status === 'active' ? <Loader2 className="w-4 h-4 animate-spin" /> : <span className="text-[10px] font-bold leading-none">{index + 1}</span>}
                  </div>
                </div>
                <span className={`text-[10px] tracking-tight whitespace-nowrap ${status === 'completed' ? 'text-green-600/70 font-medium' : status === 'active' ? 'text-primary font-bold' : 'text-on-surface-variant/60 font-medium'}`}>{stage.label}</span>
              </div>
            );
          })}
        </div>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Live Analysis Log */}
        <div className="lg:col-span-2 editorial-card flex flex-col h-[520px] overflow-hidden">
          <div className="p-4 border-b border-outline-variant/20 flex justify-between items-center bg-surface-container-low">
            <h3 className="font-headline font-semibold text-sm">Live Agent Analysis Log</h3>
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${isComplete ? 'bg-green-100 text-green-700' : 'bg-primary/10 text-primary'}`}>
              {isComplete ? 'Complete' : 'Streaming Live'}
            </span>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {logs.map((log) => (
              <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} key={log.id} className="flex flex-col gap-1">
                <div className="flex items-center gap-2">
                  <span className={`text-[10px] font-bold uppercase tracking-widest font-headline ${AGENT_COLORS[log.agent]?.split(' ')[0]}`}>{log.agent}</span>
                  <span className="text-[10px] text-on-surface-variant">{log.timestamp}</span>
                </div>
                <div className={`text-[13px] leading-relaxed p-3 rounded-lg border-l-4 ${AGENT_COLORS[log.agent]?.split(' ').slice(1).join(' ')}`}>{log.message}</div>
              </motion.div>
            ))}
            <div ref={logEndRef} />
          </div>
        </div>

        {/* Risk Summary Sidebar */}
        <div className="flex flex-col gap-6">
          <div className={`editorial-card p-6 border-l-4 flex items-start gap-4 transition-all duration-500 ${verdict ? `${verdict.borderColor} ${verdict.bgColor}` : 'border-outline-variant bg-surface-container-low'}`}>
            <div className="flex-shrink-0">
              {isComplete && finalRiskScore !== null ? <span className={`text-4xl font-extrabold font-headline tracking-tighter ${verdict?.color}`}>{Math.round(finalRiskScore * 100)}</span> : <Loader2 className="w-8 h-8 text-primary animate-spin" />}
              <div className={`text-[10px] font-bold uppercase mt-1 ${verdict?.color || 'text-on-surface-variant'}`}>Risk Score</div>
            </div>
            <div className="flex-1">
              {verdict ? (
                <>
                  <p className={`font-bold text-[14px] leading-tight mb-1 ${verdict.color}`}>{verdict.label}</p>
                  <div className={`text-[11px] font-medium opacity-70 ${verdict.color}`}><span className="block">Analysis finalized</span></div>
                </>
              ) : <p className="font-bold text-on-surface-variant text-[14px] leading-tight">Analyzing...</p>}
            </div>
          </div>

          <div className="editorial-card p-5 flex-1 flex flex-col gap-4 bg-surface-container-low/50">
            <h4 className="text-[11px] font-bold uppercase tracking-widest text-on-surface-variant">Risk Vector Map</h4>
            <div className="space-y-4">
              {['Legal', 'Financial', 'Compliance', 'Operational', 'Data', 'Termination'].map((label) => {
                const agentKey = label.toLowerCase();
                const score = riskScores[agentKey] || 0;
                const colorMap: Record<string, string> = { legal: 'bg-purple-500', financial: 'bg-blue-500', compliance: 'bg-teal-500', operational: 'bg-orange-500', data: 'bg-red-500', termination: 'bg-amber-500' };
                return (
                  <div key={label}>
                    <div className="flex justify-between text-[11px] mb-1.5">
                      <span className="font-medium text-on-surface-variant">{label}</span>
                      <span className="text-on-surface font-bold">{score.toFixed(2)}</span>
                    </div>
                    <div className="w-full h-1.5 bg-surface-container-lowest rounded-full overflow-hidden">
                      <motion.div initial={{ width: 0 }} animate={{ width: `${score * 100}%` }} transition={{ duration: 1, ease: "easeOut" }} className={`${colorMap[agentKey]} h-full`} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <button 
            disabled={!isComplete} 
            onClick={() => onViewReport(finalReport)} 
            className={`w-full py-4 rounded-xl font-bold flex items-center justify-center gap-2 transition-all duration-300 shadow-lg active:scale-95 group ${isComplete ? 'bg-primary text-white hover:bg-primary-container shadow-primary/10' : 'bg-gray-200 text-gray-400 cursor-not-allowed shadow-none'}`}
          >
            View full report <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </button>
        </div>
      </div>
    </div>
  );
}
