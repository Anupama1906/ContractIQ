import { motion } from 'motion/react';
import { CheckCircle2, Loader2, ArrowRight } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';

const mockAuditStream = [
  {
    "agent": "legal",
    "risk_type": "legal",
    "risk_score": 0.65,
    "comments": [
      "[LEGAL] The contract presents several significant legal risks:\n\n1. **Purchase Schedule Priority Creates Legal Uncertainty (Rule 1)**: Section 4 establishes that Purchase Schedules (1st priority) override the main agreement (4th priority), SOPs (2nd), and Exhibits (3rd). This creates potential conflicts where specific purchase commitments could contradict or undermine fundamental terms of the master agreement, creating legal uncertainty about which terms govern in case of disputes.\n\n2. **Broad Indemnification Obligations (Rule 2)**: Section 7 creates extensive indemnification obligations where Buyer must defend Seller against claims arising from Buyer's representations or services. Specifically, Section 7(c)(3) requires Buyer to indemnify Seller for infringement claims based on intellectual property that Buyer represented it owned and licensed to Seller. This creates significant liability exposure for Buyer.\n\n3. **Asymmetric Assignment Restrictions (Rule 3)**: While the contract doesn't explicitly address assignment rights, the indemnification and liability provisions create asymmetric obligations that could be problematic if assignment rights are addressed elsewhere or through implication.\n\nAdditional risks identified:\n- Section 2 allows Purchase Schedules to add/amend terms, creating potential for inconsistent obligations across different product lines\n- Force Majeure provisions in Section 9(c) are unusually broad, including \"any breach, negligence, criminal misconduct or other act or omission of any third-party\" as force majeure events\n- Insurance requirements in Section 8 are extensive and could be burdensome to maintain\n- Confidential Information definition in Section 10 is complex with multiple criteria that could lead to disputes over what constitutes protected information\n\nThe combination of these factors creates moderate to high legal risk due to potential conflicts between master agreement terms and purchase schedule-specific provisions, coupled with significant liability exposure through indemnification obligations."
    ]
  },
  {
    "agent": "financial",
    "risk_type": "financial",
    "risk_score": 0.3,
    "comments": [
      "[FINANCIAL] The contract presents moderate financial risk with several balanced protections. Key observations:\n\n1. **Limited Financial Exposure**: The agreement is structured as a master framework with specific commitments only in Purchase Schedules, limiting open-ended obligations. Both parties maintain flexibility to not purchase/sell unless specified in schedules.\n\n2. **Balanced Indemnification**: Section 7 provides reciprocal indemnification for third-party claims, but with reasonable limitations. Seller indemnifies for product defects and IP infringement (except for Buyer-provided IP), while Buyer indemnifies for its own misconduct and IP it licenses to Seller.\n\n3. **Reasonable Limitations**: Section 9 excludes indirect damages (except for specific carve-outs) and includes force majeure provisions that allow Buyer to source elsewhere during extended disruptions.\n\n4. **Insurance Requirements**: Section 8 mandates substantial insurance coverage ($10M minimums) with specific endorsements, providing financial protection layers.\n\n5. **Payment Certainty**: No evidence of payment uncertainty or unilateral price changes - pricing mechanisms are to be specified in Purchase Schedules.\n\nThe primary financial risks are:\n- Potential indemnification obligations for product liability or IP infringement\n- Inventory obligations under Purchase Schedules\n- Force majeure disruptions affecting supply continuity\n\nHowever, these are standard commercial risks with reasonable contractual mitigations. No evidence of penalties, harmful liability exposure, or significant payment uncertainty."
    ]
  },
  {
    "agent": "compliance",
    "risk_type": "compliance",
    "risk_score": 0.3,
    "comments": [
      "[COMPLIANCE] This is a commercial supply agreement between two companies for consumer and food service products. The contract contains standard commercial terms for product warranties, indemnification, insurance, and liability limitations. \n\nKey compliance considerations:\n1. The contract references compliance with Applicable Laws (Section 5a) and specifically mentions food safety regulations from the FDA (Section 6c), indicating regulatory obligations in the food industry.\n2. There are product warranty requirements for compliance with laws, including food safety regulations.\n3. The indemnification provisions cover fines/penalties from governmental authorities for violations of Applicable Law (Sections 7b(4) and 7c(4)).\n4. Insurance requirements include Workers Compensation and compliance with applicable laws.\n\nHowever, this appears to be a standard commercial supply agreement rather than a regulated reseller/affiliate arrangement. The rules provided about reseller obligations, agent discretion, and trademark restrictions don't align with this contract's content. The contract focuses on product supply, warranties, and commercial terms rather than reseller compliance obligations, licensing requirements, or trademark usage restrictions.\n\nThe moderate compliance risk score (0.3) reflects the food safety regulatory obligations but recognizes this is primarily a commercial agreement with standard regulatory compliance provisions rather than a heavily regulated licensing or reseller arrangement." 
    ]
  },
  {
    "agent": "operational",
    "risk_type": "operational",
    "risk_score": 0.6,
    "comments": [
      "[OPERATIONAL] The contract contains several operational risks:\n\n1. **Vague Standard Operating Procedures (SOPs)**: Section 3 states that the parties will update their business systems over the next 6 months and then \"agree on necessary modifications\" to the SOPs. This creates uncertainty about when updated procedures will be finalized and what they will contain, potentially disrupting operations.\n\n2. **Unclear Deliverables**: The agreement is structured around future Purchase Schedules that must be negotiated separately. Section 2 states that the agreement \"will not require Seller to sell any type or quantity of a product to Buyer, nor will this Agreement require Buyer to purchase any type or quantity of a product from Seller, except as expressly provided by the Parties in a Purchase Schedule.\" This creates dependency on future negotiations.\n\n3. **Dependency on Third-Party Systems**: The need to update business systems (mentioned in Section 3) creates operational risk if system updates are delayed or incompatible.\n\n4. **Ambiguous Force Majeure Allocation**: Section 9(c) states Seller will \"act in good faith in allocating its available manufacturing capacity\" during force majeure events, but doesn't specify clear allocation criteria, creating potential disputes during supply disruptions.\n\n5. **Confidential Information Process Dependencies**: Section 10 requires specific labeling and notification procedures for confidential information to be effective, creating operational risk if procedures aren't followed correctly."
    ]
  },
  {
    "agent": "data",
    "risk_type": "data",
    "risk_score": 0.1,
    "comments": [
      "[DATA] DATA RISK NOT APPLICABLE - This is a standard supply agreement for physical products (consumer and food service products) with no indication of personal data processing, customer data handling, or system/database access. The contract focuses on product specifications, warranties, indemnification, insurance, and confidentiality of business information. The confidentiality section covers trade secrets and proprietary business information, not personal data. Since no personal data, customer data, or system access is involved, data protection and privacy risks are not applicable."
    ]
  },
  {
    "agent": "termination",
    "risk_type": "termination",
    "risk_score": 0.4,
    "comments": [
      "[TERMINATION] The contract shows moderate termination risk. Key observations:\n\n1. **Termination Rights**: Section 1 provides termination rights after expiration of last Purchase Schedule with written notice, which is reasonable and not immediate.\n\n2. **Material Breach**: No specific termination for material breach clause found in the provided text, though Section 5 mentions 10-day cure period for adequate assurances of performance under UCC 2-609.\n\n3. **No Unfair Termination**: No immediate termination for assignment attempts, change of control, or other unfair triggers mentioned in the rules.\n\n4. **Business Continuity**: The agreement structure with Purchase Schedules provides some stability - termination doesn't automatically cancel existing purchase commitments.\n\n5. **Missing Elements**: The provided contract excerpt doesn't show Section 11(d) referenced in termination clause, which might contain additional termination provisions.\n\nRisk is moderate (0.4) because while termination provisions appear reasonable, the incomplete nature of the contract (missing Section 11) prevents full assessment, and there may be hidden risks in unreviewed sections."
    ]
  },
  {
    "agent": "evaluate",
    "risk_type": "evaluate",
    "risk_score": 0.45,
    "comments": [],
    "final_report": "# Contract Risk Assessment Report\n\n## Overall Risk Profile: MODERATE (0.45)\n\nThis supply agreement presents a balanced risk profile with several standard commercial protections but contains notable legal and operational uncertainties that require attention.\n\n## Key Risk Areas:\n\n**Legal Risks (0.65) - HIGHEST CONCERN**\n- Purchase Schedule priority creates potential conflicts between master agreement terms and specific purchase commitments\n- Broad indemnification obligations expose Buyer to significant liability for IP infringement claims\n- Force majeure provisions are unusually expansive, including third-party misconduct\n\n**Operational Risks (0.60) - SIGNIFICANT**\n- Vague Standard Operating Procedures with 6-month update timeline creates implementation uncertainty\n- Dependency on future Purchase Schedule negotiations for actual deliverables\n- Unclear capacity allocation during force majeure events\n\n**Financial Risks (0.30) - MODERATE**\n- Reasonable indemnification limitations and liability caps\n- Substantial insurance requirements ($10M minimums) provide protection\n- No evidence of payment uncertainty or unilateral price changes\n\n**Compliance Risks (0.30) - MODERATE**\n- Standard food safety regulatory obligations (FDA compliance)\n- Indemnification covers governmental fines/penalties\n- Primarily commercial rather than heavily regulated arrangement\n\n**Termination Risks (0.40) - MODERATE**\n- Reasonable termination provisions with written notice requirements\n- Missing Section 11 prevents complete assessment\n\n## Recommendations:\n1. Clarify hierarchy between Purchase Schedules and master agreement terms\n2. Define specific timelines and criteria for SOP updates\n3. Review and potentially narrow force majeure provisions\n4. Ensure complete contract review including missing sections"
  }
];

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

export default function AuditDashboard({ onViewReport, documentId }: { onViewReport: (report: string) => void, documentId: string | null }) {
  const [currentIndex, setCurrentIndex] = useState<number>(() => {
    const saved = localStorage.getItem('contractiq_audit_index');
    return saved ? parseInt(saved, 10) : -1;
  });
  const [logs, setLogs] = useState<LogEntry[]>(() => {
    const saved = localStorage.getItem('contractiq_audit_logs');
    return saved ? JSON.parse(saved) : [];
  });
  const [riskScores, setRiskScores] = useState<Record<string, number>>(() => {
    const saved = localStorage.getItem('contractiq_audit_scores');
    return saved ? JSON.parse(saved) : {
      legal: 0,
      financial: 0,
      compliance: 0,
      operational: 0,
      data: 0,
      termination: 0,
    };
  });

  useEffect(() => {
    localStorage.setItem('contractiq_audit_index', currentIndex.toString());
  }, [currentIndex]);

  useEffect(() => {
    localStorage.setItem('contractiq_audit_logs', JSON.stringify(logs));
  }, [logs]);

  useEffect(() => {
    localStorage.setItem('contractiq_audit_scores', JSON.stringify(riskScores));
  }, [riskScores]);

  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (currentIndex < mockAuditStream.length) {
      const timer = setTimeout(() => {
        const nextIndex = currentIndex + 1;
        
        if (nextIndex < mockAuditStream.length) {
          const nextAgent = mockAuditStream[nextIndex];
          
          // Append log
          if (nextAgent.comments.length > 0) {
            const rawComment = nextAgent.comments[0];
            const cleanComment = rawComment.replace(/^\[.*?\]\s*/, '');
            const timestamp = new Date().toLocaleTimeString('en-GB', { hour12: false });
            
            setLogs((prevLogs) => [
              ...prevLogs,
              {
                id: Math.random().toString(36).substr(2, 9),
                agent: nextAgent.agent,
                timestamp,
                message: cleanComment,
              }
            ]);
          }

          // Update risk scores (except evaluate)
          if (nextAgent.agent !== 'evaluate') {
            setRiskScores((prevScores) => ({
              ...prevScores,
              [nextAgent.agent]: nextAgent.risk_score,
            }));
          }
        }

        setCurrentIndex(nextIndex);
      }, 1500);

      return () => clearTimeout(timer);
    }
  }, [currentIndex]);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const getStageStatus = (stageId: string) => {
    if (stageId === 'retrieve') return 'completed';
    
    const stageIndex = AUDIT_STAGES_BASE.findIndex(s => s.id === stageId);
    const activeStageIndex = currentIndex + 1; // +1 because retrieve is index 0 in stages but not in stream

    if (stageIndex < activeStageIndex) return 'completed';
    if (stageIndex === activeStageIndex) return 'active';
    return 'pending';
  };

  const isComplete = currentIndex >= mockAuditStream.length - 1;
  const evaluateAgent = mockAuditStream.find(a => a.agent === 'evaluate');
  const finalRiskScore = isComplete ? (evaluateAgent?.risk_score || 0) : null;

  const getVerdict = (score: number) => {
    if (score >= 0.7) return { label: 'High risk — escalation required', color: 'text-error', bgColor: 'bg-error-container/10', borderColor: 'border-error' };
    if (score >= 0.4) return { label: 'Moderate risk — review recommended', color: 'text-amber-600', bgColor: 'bg-amber-50', borderColor: 'border-amber-500' };
    return { label: 'Low risk — approved', color: 'text-green-600', bgColor: 'bg-green-50', borderColor: 'border-green-500' };
  };

  const verdict = finalRiskScore !== null ? getVerdict(finalRiskScore) : null;

  return (
    <div className="flex flex-col gap-8">
      {/* Pipeline Tracker */}
      <section className="w-full py-2">
        <div className="flex items-center justify-between w-full relative">
          {/* Connecting Lines Layer */}
          <div className="absolute top-[12px] -translate-y-1/2 left-[6.25%] right-[6.25%] h-[1.5px] flex z-0">
            {AUDIT_STAGES_BASE.slice(0, -1).map((stage, index) => {
              const status = getStageStatus(stage.id);
              const nextStatus = getStageStatus(AUDIT_STAGES_BASE[index + 1].id);
              let lineColor = 'bg-gray-200';
              
              if (status === 'active') {
                lineColor = 'bg-primary';
              } else if (status === 'completed' && (nextStatus === 'completed' || nextStatus === 'active')) {
                lineColor = 'bg-green-500';
              }
              
              return (
                <div key={`line-${stage.id}`} className={`flex-1 h-full ${lineColor}`} />
              );
            })}
          </div>

          {/* Nodes Layer */}
          {AUDIT_STAGES_BASE.map((stage, index) => {
            const status = getStageStatus(stage.id);
            return (
              <div key={stage.id} className="flex flex-col items-center gap-2 flex-1">
                <div className="relative flex items-center justify-center">
                  {status === 'active' && (
                    <motion.div
                      animate={{ scale: [1, 1.6, 1], opacity: [0.6, 0, 0.6] }}
                      transition={{ duration: 2, repeat: Infinity }}
                      className="absolute w-7 h-7 rounded-full bg-primary/40"
                    />
                  )}
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center transition-all duration-300 z-10 ${
                    status === 'completed' 
                      ? 'bg-green-500 text-white' 
                      : status === 'active'
                      ? 'bg-primary text-white shadow-sm shadow-primary/20'
                      : 'bg-surface border-2 border-outline-variant text-on-surface-variant'
                  }`}>
                    {status === 'completed' ? (
                      <CheckCircle2 className="w-4 h-4" />
                    ) : status === 'active' ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <span className="text-[10px] font-bold leading-none">{index + 1}</span>
                    )}
                  </div>
                </div>
                <span className={`text-[10px] tracking-tight whitespace-nowrap ${
                  status === 'completed' ? 'text-green-600/70 font-medium' :
                  status === 'active' ? 'text-primary font-bold' :
                  'text-on-surface-variant/60 font-medium'
                }`}>
                  {stage.label}
                </span>
              </div>
            );
          })}
        </div>
      </section>

      {/* Main Bento Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Live Analysis Log */}
        <div className="lg:col-span-2 editorial-card flex flex-col h-[520px] overflow-hidden">
          <div className="p-4 border-b border-outline-variant/20 flex justify-between items-center bg-surface-container-low">
            <h3 className="font-headline font-semibold text-sm">Live Agent Analysis Log</h3>
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
              isComplete ? 'bg-green-100 text-green-700' : 'bg-primary/10 text-primary'
            }`}>
              {isComplete ? 'Complete' : 'Streaming Live'}
            </span>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {logs.map((log) => (
              <motion.div 
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                key={log.id} 
                className="flex flex-col gap-1"
              >
                <div className="flex items-center gap-2">
                  <span className={`text-[10px] font-bold uppercase tracking-widest font-headline ${AGENT_COLORS[log.agent]?.split(' ')[0]}`}>
                    {log.agent}
                  </span>
                  <span className="text-[10px] text-on-surface-variant">{log.timestamp}</span>
                </div>
                <div className={`text-[13px] leading-relaxed p-3 rounded-lg border-l-4 ${AGENT_COLORS[log.agent]?.split(' ').slice(1).join(' ')}`}>
                  {log.message}
                </div>
              </motion.div>
            ))}
            <div ref={logEndRef} />
          </div>
        </div>

        {/* Risk Summary Sidebar */}
        <div className="flex flex-col gap-6">
          {/* Risk Score Card */}
          <div className={`editorial-card p-6 border-l-4 flex items-start gap-4 transition-all duration-500 ${
            verdict ? `${verdict.borderColor} ${verdict.bgColor}` : 'border-outline-variant bg-surface-container-low'
          }`}>
            <div className="flex-shrink-0">
              {finalRiskScore !== null ? (
                <span className={`text-4xl font-extrabold font-headline tracking-tighter ${verdict?.color}`}>
                  {Math.round(finalRiskScore * 100)}
                </span>
              ) : (
                <Loader2 className="w-8 h-8 text-primary animate-spin" />
              )}
              <div className={`text-[10px] font-bold uppercase mt-1 ${verdict?.color || 'text-on-surface-variant'}`}>Risk Score</div>
            </div>
            <div className="flex-1">
              {verdict ? (
                <>
                  <p className={`font-bold text-[14px] leading-tight mb-1 ${verdict.color}`}>{verdict.label}</p>
                  <div className={`text-[11px] font-medium opacity-70 ${verdict.color}`}>
                    <span className="block">Analysis finalized</span>
                  </div>
                </>
              ) : (
                <p className="font-bold text-on-surface-variant text-[14px] leading-tight">Analyzing...</p>
              )}
            </div>
          </div>

          {/* Risk Vector Map */}
          <div className="editorial-card p-5 flex-1 flex flex-col gap-4 bg-surface-container-low/50">
            <h4 className="text-[11px] font-bold uppercase tracking-widest text-on-surface-variant">Risk Vector Map</h4>
            <div className="space-y-4">
              {['Legal', 'Financial', 'Compliance', 'Operational', 'Data', 'Termination'].map((label) => {
                const agentKey = label.toLowerCase();
                const score = riskScores[agentKey] || 0;
                const colorMap: Record<string, string> = {
                  legal: 'bg-purple-500',
                  financial: 'bg-blue-500',
                  compliance: 'bg-teal-500',
                  operational: 'bg-orange-500',
                  data: 'bg-red-500',
                  termination: 'bg-amber-500',
                };
                
                return (
                  <div key={label}>
                    <div className="flex justify-between text-[11px] mb-1.5">
                      <span className="font-medium text-on-surface-variant">{label}</span>
                      <span className="text-on-surface font-bold">{score.toFixed(2)}</span>
                    </div>
                    <div className="w-full h-1.5 bg-surface-container-lowest rounded-full overflow-hidden">
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${score * 100}%` }}
                        transition={{ duration: 1, ease: "easeOut" }}
                        className={`${colorMap[agentKey]} h-full`} 
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Primary Action */}
          <button 
            disabled={!isComplete}
            onClick={() => onViewReport(evaluateAgent?.final_report || '')}
            className={`w-full py-4 rounded-xl font-bold flex items-center justify-center gap-2 transition-all duration-300 shadow-lg active:scale-95 group ${
              isComplete 
                ? 'bg-primary text-white hover:bg-primary-container shadow-primary/10' 
                : 'bg-gray-200 text-gray-400 cursor-not-allowed shadow-none'
            }`}
          >
            View full report 
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </button>
        </div>
      </div>
    </div>
  );
}
