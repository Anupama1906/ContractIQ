import { motion } from 'motion/react';
import { Upload, Eye, Lock, CheckCircle2, ArrowRight, Loader2, ChevronLeft, ChevronRight } from 'lucide-react';
import React, { useState, useRef, useEffect, useMemo } from 'react';

interface AnonymizeResponse {
  document_id: string;
  raw_text: string;
  anonymized_text: string;
  mapping_dict: Record<string, string>;
}

export default function Anonymizer({ onAudit }: { onAudit: () => void }) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<AnonymizeResponse | null>(null);
  const [isStored, setIsStored] = useState(false);
  const [chipPage, setChipPage] = useState(0);

  const originalRef = useRef<HTMLDivElement>(null);
  const anonymizedRef = useRef<HTMLDivElement>(null);
  const isSyncingRef = useRef(false);

  const handleFileUpload = async (file: File) => {
    if (!file.name.endsWith('.pdf') && !file.name.endsWith('.docx')) {
      setError('Only PDF or DOCX files are supported.');
      return;
    }

    setError(null);
    setIsProcessing(true);
    setIsStored(false);
    setData(null);

    // Simulate API call
    try {
      // In a real app: await fetch('http://localhost:8000/upload', { method: 'POST', body: formData });
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockResponse: AnonymizeResponse = {
        "document_id": "550e8400-e29b-41d4-a716-446655440000",
        "raw_text": "THIS MASTER SERVICES AGREEMENT (the Agreement) is made this 12th day of October, 2023 (the Effective Date). BETWEEN: Acme Dynamics Inc., a Delaware corporation (Client) and Sarah J. Miller d/b/a Miller Consulting Group (Contractor). WHEREAS, the parties desire to enter into an arrangement for the provision of certain software engineering services starting on November 1, 2023. Notice shall be sent to Acme Headquarters at the address listed below. Signed: John R. Sterling, CEO, Acme Dynamics.",
        "anonymized_text": "THIS MASTER SERVICES AGREEMENT (the Agreement) is made this DATE_1 (the Effective Date). BETWEEN: ORG_1, a Delaware corporation (Client) and PERSON_1 d/b/a ORG_2 (Contractor). WHEREAS, the parties desire to enter into an arrangement for the provision of certain software engineering services starting on DATE_2. Notice shall be sent to LOCATION_1 at the address listed below. Signed: PERSON_2, CEO, ORG_3.",
        "mapping_dict": {
          "DATE_1": "12th day of October, 2023",
          "ORG_1": "Acme Dynamics Inc.",
          "PERSON_1": "Sarah J. Miller",
          "ORG_2": "Miller Consulting Group",
          "DATE_2": "November 1, 2023",
          "LOCATION_1": "Acme Headquarters",
          "PERSON_2": "John R. Sterling",
          "ORG_3": "Acme Dynamics"
        }
      };

      setData(mockResponse);
      localStorage.setItem('contractiq_entity_map', JSON.stringify(mockResponse));
      localStorage.setItem('contractiq_document_id', mockResponse.document_id);
      setIsStored(true);
    } catch (err) {
      setError('Failed to process document.');
    } finally {
      setIsProcessing(false);
    }
  };

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  // Synchronized scrolling
  useEffect(() => {
    const original = originalRef.current;
    const anonymized = anonymizedRef.current;

    if (!original || !anonymized) return;

    const handleScroll = (source: HTMLDivElement, target: HTMLDivElement) => {
      if (isSyncingRef.current) return;
      isSyncingRef.current = true;
      target.scrollTop = source.scrollTop;
      setTimeout(() => {
        isSyncingRef.current = false;
      }, 10);
    };

    const onOriginalScroll = () => handleScroll(original, anonymized);
    const onAnonymizedScroll = () => handleScroll(anonymized, original);

    original.addEventListener('scroll', onOriginalScroll);
    anonymized.addEventListener('scroll', onAnonymizedScroll);

    return () => {
      original.removeEventListener('scroll', onOriginalScroll);
      anonymized.removeEventListener('scroll', onAnonymizedScroll);
    };
  }, [data]);

  const highlightedOriginal = useMemo(() => {
    if (!data) return null;
    let text = data.raw_text;
    const mappings = (Object.entries(data.mapping_dict) as [string, string][]).sort((a, b) => b[1].length - a[1].length);
    
    // We need to be careful with overlapping matches. 
    // A simple way is to use a regex that matches any of the values.
    const escapedValues = mappings.map(([_, val]: [string, string]) => val.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
    const regex = new RegExp(`(${escapedValues.join('|')})`, 'g');
    
    const parts = text.split(regex);
    return parts.map((part, i) => {
      const isMatch = mappings.some(([_, val]: [string, string]) => val === part);
      if (isMatch) {
        return <span key={i} className="bg-orange-100 text-orange-900 px-1 rounded">{part}</span>;
      }
      return part;
    });
  }, [data]);

  const highlightedAnonymized = useMemo(() => {
    if (!data) return null;
    let text = data.anonymized_text;
    const keys = Object.keys(data.mapping_dict).sort((a, b) => b.length - a.length);
    const regex = new RegExp(`(${keys.join('|')})`, 'g');
    
    const parts = text.split(regex);
    return parts.map((part, i) => {
      if (data.mapping_dict[part]) {
        return (
          <span key={i} className="bg-primary/10 text-primary px-1.5 py-0.5 rounded-full text-[11px] font-semibold">
            [{part}]
          </span>
        );
      }
      return part;
    });
  }, [data]);

  const entityCounts = useMemo(() => {
    if (!data) return [];
    const counts: Record<string, number> = {};
    Object.keys(data.mapping_dict).forEach(key => {
      const type = key.split('_')[0];
      counts[type] = (counts[type] || 0) + 1;
    });
    return Object.entries(counts).map(([type, count]) => ({ type, count }));
  }, [data]);

  const paginatedChips = useMemo(() => {
    return entityCounts.slice(chipPage * 5, (chipPage * 5) + 5);
  }, [entityCounts, chipPage]);

  const canAudit = data !== null && isStored && !isProcessing;

  return (
    <div className="flex flex-col gap-8">
      <div className="max-w-2xl">
        <h1 className="text-2xl font-extrabold text-on-surface mb-2 font-headline">Contract Anonymization</h1>
        <p className="text-on-surface-variant text-sm">Strip sensitive PII before running deep structural audits.</p>
      </div>

      {/* Upload Zone */}
      <section>
        <div 
          onDragOver={(e) => e.preventDefault()}
          onDrop={onDrop}
          className="w-full h-48 border-2 border-dashed border-outline-variant bg-surface-container-low rounded-xl flex flex-col items-center justify-center gap-3 transition-all hover:bg-surface-container-high group cursor-pointer relative"
        >
          <input 
            type="file" 
            className="absolute inset-0 opacity-0 cursor-pointer" 
            onChange={onFileChange}
            accept=".pdf,.docx"
          />
          <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary shadow-sm group-hover:scale-110 transition-transform">
            {isProcessing ? <Loader2 className="w-6 h-6 animate-spin" /> : <Upload className="w-6 h-6" />}
          </div>
          <div className="text-center">
            <p className="font-semibold text-on-surface">
              {isProcessing ? 'Processing document...' : 'Drop contract here'}
            </p>
            <p className="text-xs text-on-surface-variant mt-1">PDF or DOCX</p>
          </div>
          {!isProcessing && (
            <button className="mt-2 px-6 py-2 bg-surface-container-lowest text-primary border border-outline-variant rounded-lg text-sm font-semibold hover:bg-primary hover:text-white transition-all active:scale-95 pointer-events-none">
              Browse files
            </button>
          )}
        </div>
        {error && <p className="text-error text-xs mt-2 font-medium">{error}</p>}
      </section>

      {/* Comparison Panel */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Original */}
        <div className="editorial-card overflow-hidden">
          <div className="px-5 py-3 bg-surface-container-low flex items-center justify-between border-b border-outline-variant/20">
            <span className="text-xs font-bold uppercase tracking-widest text-on-surface-variant font-headline">Original</span>
            <Eye className="w-4 h-4 text-on-surface-variant" />
          </div>
          <div 
            ref={originalRef}
            className="p-6 font-body text-sm leading-relaxed text-on-surface space-y-4 h-[400px] overflow-y-auto"
          >
            {data ? (
              <div className="whitespace-pre-wrap">{highlightedOriginal}</div>
            ) : (
              <p className="text-on-surface-variant italic">Upload a contract to preview content here.</p>
            )}
          </div>
        </div>

        {/* Anonymized */}
        <div className="editorial-card overflow-hidden">
          <div className="px-5 py-3 bg-primary/5 flex items-center justify-between border-b border-outline-variant/20">
            <span className="text-xs font-bold uppercase tracking-widest text-primary font-headline">Anonymized</span>
            <Lock className="w-4 h-4 text-primary" />
          </div>
          <div 
            ref={anonymizedRef}
            className="p-6 font-body text-sm leading-relaxed text-on-surface-variant space-y-4 h-[400px] overflow-y-auto"
          >
            {data ? (
              <div className="whitespace-pre-wrap">{highlightedAnonymized}</div>
            ) : (
              <p className="text-on-surface-variant italic">Upload a contract to preview content here.</p>
            )}
          </div>
        </div>
      </section>

      {/* Footer Actions */}
      <div className="flex flex-col gap-6">
        <div className="flex flex-wrap items-center justify-between gap-4 min-h-[32px]">
          <div className="flex items-center gap-2">
            {entityCounts.length > 5 && (
              <button 
                onClick={() => setChipPage(p => Math.max(0, p - 1))}
                disabled={chipPage === 0}
                className="p-1 rounded-full hover:bg-surface-container disabled:opacity-30"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
            )}
            
            <div className="flex items-center gap-2">
              {paginatedChips.map(({ type, count }) => (
                <span key={type} className="px-3 py-1 bg-surface-container text-primary rounded-full text-[10px] font-bold tracking-tight uppercase">
                  {type} ×{count}
                </span>
              ))}
            </div>

            {entityCounts.length > 5 && (
              <button 
                onClick={() => setChipPage(p => Math.min(Math.ceil(entityCounts.length / 5) - 1, p + 1))}
                disabled={chipPage >= Math.ceil(entityCounts.length / 5) - 1}
                className="p-1 rounded-full hover:bg-surface-container disabled:opacity-30"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            )}
          </div>
          
          {isStored && (
            <div className="flex items-center gap-2 text-green-600">
              <CheckCircle2 className="w-4 h-4" />
              <span className="text-xs font-medium">Entity map stored locally. No PII transmitted externally.</span>
            </div>
          )}
        </div>
        <button 
          onClick={onAudit}
          disabled={!canAudit}
          className={`w-full py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-2 transition-all shadow-lg font-headline group ${
            canAudit 
              ? 'bg-primary text-white hover:bg-primary-container shadow-primary/10 active:scale-95' 
              : 'bg-gray-300 text-gray-500 cursor-not-allowed shadow-none'
          }`}
        >
          Run adversarial audit
          <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
        </button>
      </div>
    </div>
  );
}
