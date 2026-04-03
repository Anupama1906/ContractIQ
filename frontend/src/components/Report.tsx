import { Download, History } from 'lucide-react';
import { useMemo } from 'react';

interface ParsedRisk {
  title: string;
  severity: string;
  score: string;
  points: string[];
  tagColor: string;
}

// Added documentId to props to support the download logic
export default function Report({ markdown, documentId }: { markdown?: string; documentId: string }) {
  const reportMarkdown = markdown || '';

  const handleDownload = () => {
    // Direct link to the backend endpoint
    const downloadUrl = `http://localhost:8000/contracts/download-report/${documentId}`;
    window.location.href = downloadUrl;
  };

  const parsedData = useMemo(() => {
    if (!reportMarkdown) {
      return { executiveSummary: '', riskAreas: [], recommendations: [], finalScore: 0 };
    }
    
    const sections = reportMarkdown.split(/(?:\r?\n|^)##\s*/).filter(Boolean);
    let executiveSummary = '';
    const riskAreas: ParsedRisk[] = [];
    const recommendations: string[] = [];
    let finalScore = 0;

    sections.forEach(section => {
      const lines = section.split(/\r?\n/);
      if (lines.length === 0) return;
      const header = lines[0].toLowerCase();
      const content = lines.slice(1).join('\n').trim();

      if (header.includes('overall risk profile') || header.includes('executive summary')) {
        executiveSummary = content;
        const scoreMatch = lines[0].match(/\(([\d.]+)\)/);
        if (scoreMatch) finalScore = parseFloat(scoreMatch[1]);
      } 
      else if (header.includes('risk areas')) {
        let currentRisk: ParsedRisk | null = null;
        lines.slice(1).forEach(line => {
          const trimmedLine = line.trim();
          if (!trimmedLine) return;
          const riskHeaderMatch = trimmedLine.match(/^[*]*\s*(.*?)\s*\(([\d.]+)\)\s*-\s*(.*?)\s*[*]*$/);
          if (riskHeaderMatch) {
            const severity = riskHeaderMatch[3].trim();
            let tagColor = 'bg-blue-100 text-blue-700';
            const sevLower = severity.toLowerCase();
            if (sevLower.includes('critical')) tagColor = 'bg-red-100 text-red-700';
            else if (sevLower.includes('high')) tagColor = 'bg-orange-100 text-orange-700';
            else if (sevLower.includes('low')) tagColor = 'bg-green-100 text-green-700';

            currentRisk = { title: riskHeaderMatch[1].trim(), severity, score: riskHeaderMatch[2].trim(), points: [], tagColor };
            riskAreas.push(currentRisk);
          } else if (trimmedLine.startsWith('-') && currentRisk) {
            currentRisk.points.push(trimmedLine.replace(/^-\s*/, '').trim());
          }
        });
      }
      else if (header.includes('recommendations')) {
        lines.slice(1).forEach(line => {
          const trimmedLine = line.trim();
          if (/^\d+\.\s/.test(trimmedLine)) {
            recommendations.push(trimmedLine.replace(/^\d+\.\s*/, '').trim());
          }
        });
      }
    });

    if (finalScore === 0) {
      const scoreMatch = reportMarkdown.match(/FINAL RISK SCORE:\s*([\d.]+)/i);
      if (scoreMatch) finalScore = parseFloat(scoreMatch[1]);
    }

    return { executiveSummary, riskAreas, recommendations, finalScore };
  }, [reportMarkdown]);

  const verdict = parsedData.finalScore >= 0.7 ? { label: 'HIGH RISK', color: 'bg-error shadow-error/10' } 
                : parsedData.finalScore >= 0.4 ? { label: 'MODERATE RISK', color: 'bg-amber-500 shadow-amber-500/10' } 
                : { label: 'LOW RISK', color: 'bg-green-500 shadow-green-500/10' };

  return (
    <div className="flex flex-col gap-12">
      <section className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
        <div className={`md:col-span-3 rounded-xl p-6 text-white shadow-lg ${verdict.color}`}>
          <p className="font-headline font-extrabold text-2xl tracking-tight mb-1">{verdict.label}</p>
          <p className="text-sm font-medium opacity-90">Score {parsedData.finalScore.toFixed(2)} / Threshold 0.60</p>
        </div>
        
        <div className="md:col-span-6">
          <h2 className="font-headline text-lg font-bold mb-3">Executive Summary</h2>
          <p className="text-on-surface-variant leading-relaxed text-sm">{parsedData.executiveSummary}</p>
        </div>

        <div className="md:col-span-3 flex justify-end">
          {/* Button now triggers handleDownload */}
          <button 
            onClick={handleDownload}
            className="flex items-center gap-2 px-4 py-2 editorial-card text-primary font-semibold hover:bg-surface-container-low transition-all active:scale-95 text-sm"
          >
            <Download className="w-4 h-4" />
            Download PDF
          </button>
        </div>
      </section>

      {/* ... Rest of your original UI code for Critical Risk Areas and Recommendations ... */}
      <section>
        <h3 className="font-headline text-xl font-bold mb-8 text-on-surface">Critical risk areas</h3>
        <div className="grid grid-cols-1 gap-4">
          {parsedData.riskAreas.map((area) => (
            <div key={area.title} className="editorial-card p-6">
              <div className="flex items-center gap-3 mb-4">
                <h4 className="font-bold text-base">{area.title}</h4>
                <span className={`${area.tagColor} px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider`}>{area.severity}</span>
                <span className="text-on-surface-variant text-sm font-medium">({area.score})</span>
              </div>
              <ul className="space-y-2 text-sm text-on-surface-variant">
                {area.points.map((point, idx) => <li key={idx}>- {point}</li>)}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* Recommendations UI remains identical */}
      <section>
        <h3 className="font-headline text-xl font-bold mb-6 text-on-surface">Recommendations</h3>
        <div className="editorial-card p-8 bg-surface-container-low/30">
          <ol className="space-y-4 list-decimal list-inside text-on-surface-variant text-sm">
            {parsedData.recommendations.map((rec, idx) => {
              const parts = rec.split('**');
              return parts.length >= 3 ? (
                <li key={idx} className="pl-2"><strong>{parts[1]}</strong>{parts.slice(2).join('')}</li>
              ) : <li key={idx} className="pl-2">{rec}</li>;
            })}
          </ol>
        </div>
      </section>

      <section className="text-center py-12 border-y border-outline-variant/20">
        <p className="text-xs font-bold uppercase tracking-[0.2em] text-on-surface-variant mb-2">Final risk score</p>
        <p className={`text-5xl font-extrabold font-headline tracking-tight ${parsedData.finalScore >= 0.7 ? 'text-error' : 'text-amber-500'}`}>
          {parsedData.finalScore.toFixed(2)} / 1.00
        </p>
      </section>

      <footer className="flex flex-col md:flex-row justify-between gap-4 text-on-surface-variant">
        <div className="flex items-center gap-2 text-[12px] font-medium">
          <History className="w-4 h-4" />
          <span>Audit Trail: Report generated on Oct 24, 2023 at 14:42 GMT</span>
        </div>
        <div className="flex items-center gap-6 text-[12px]">
          <span>Confidential • Internal Use</span>
          <span className="font-bold">ID: {documentId}</span>
        </div>
      </footer>
    </div>
  );
}