import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { resumeAPI } from '../services/api';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { toast } from 'react-toastify';

export default function Upload() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [dragging, setDragging] = useState(false);
  const navigate = useNavigate();

  const handleFile = (f) => {
    if (!f) return;
    const ok = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!ok.includes(f.type)) { toast.error('Only PDF and DOCX files allowed'); return; }
    setFile(f); setResult(null);
  };

 const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await resumeAPI.upload(formData);
      setResult(res.data.data);
      toast.success('Resume verified and parsed successfully!');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Upload failed';
      if (msg.includes('ML classifier')) {
        toast.error(
          'Our AI determined this is not a resume. Please upload your CV or resume document.',
          { autoClose: 5000 }
        );
      } else if (msg.includes('5MB')) {
        toast.error('File too large. Maximum size is 5MB.');
      } else {
        toast.error(msg);
      }
    } finally {
      setLoading(false);
    }
};

  return (
    <div className="bg-app bg-grid min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-3xl mx-auto w-full px-4 sm:px-6 py-10">

        <h1 className="page-title">Upload Resume</h1>
        <p className="page-sub">AI will extract your skills, education and experience automatically</p>

        {/* Drop Zone */}
        <div
          onDrop={(e) => { e.preventDefault(); setDragging(false); handleFile(e.dataTransfer.files[0]); }}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          className={`glass-card transition-all duration-300 mb-4 ${dragging ? 'border-blue-400 dark:border-cyan-400 shadow-glow-cyan' : ''} ${file ? 'p-5' : 'p-12 sm:p-16 text-center cursor-pointer hover:border-gray-300 dark:hover:border-white/20'}`}
        >
          {file ? (
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center justify-center text-red-400 font-mono text-xs font-bold flex-shrink-0">
                PDF
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-700 dark:text-gray-200 truncate">{file.name}</p>
                <p className="text-xs text-gray-400 mt-0.5">{(file.size / 1024).toFixed(1)} KB</p>
              </div>
              <button onClick={() => setFile(null)}
                className="text-xs px-3 py-1.5 rounded-lg bg-red-50 dark:bg-red-500/10 text-red-500 border border-red-100 dark:border-red-500/20 cursor-pointer">
                Remove
              </button>
            </div>
          ) : (
            <div>
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-2xl mx-auto mb-4"
                style={{ background: 'linear-gradient(135deg, rgba(13,27,110,0.1), rgba(34,211,238,0.1))', border: '1px solid rgba(34,211,238,0.2)' }}>
                ↑
              </div>
              <p className="text-base font-semibold text-gray-700 dark:text-gray-200 mb-1">
                Drop your resume here
              </p>
              <p className="text-sm text-gray-400 mb-5">PDF or DOCX, max 5MB</p>
              <label className="btn-primary cursor-pointer inline-block px-6 py-2.5">
                Browse Files
                <input type="file" accept=".pdf,.docx" className="hidden"
                  onChange={e => handleFile(e.target.files[0])} />
              </label>
            </div>
          )}
        </div>

        {file && !result && (
          <button onClick={handleUpload} disabled={loading}
            className="btn-primary w-full py-3.5 text-base"
            style={{ opacity: loading ? 0.7 : 1 }}>
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Parsing resume with AI...
              </span>
            ) : 'Upload & Parse Resume →'}
          </button>
        )}

        {/* Results */}
        {result && (
          <div className="glass-card p-6 mt-4">
            <div className="flex items-center gap-2 mb-5">
              <div className="w-2 h-2 rounded-full bg-emerald-400" style={{ boxShadow: '0 0 8px #34d39980' }} />
              <h3 className="text-base font-display font-bold text-gray-800 dark:text-white">
                Resume Parsed Successfully
              </h3>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
              {[
                { label: 'Name', value: result.name },
                { label: 'Email', value: result.email || '—' },
                { label: 'Phone', value: result.phone || '—' },
                { label: 'Skills Found', value: result.total_skills, highlight: true },
              ].map(item => (
                <div key={item.label} className="bg-gray-50 dark:bg-white/[0.04] rounded-xl p-3">
                  <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">{item.label}</p>
                  <p className={`text-sm font-semibold truncate ${item.highlight ? 'text-blue-500 dark:text-cyan-400 text-lg' : 'text-gray-700 dark:text-gray-200'}`}>
                    {item.value}
                  </p>
                </div>
              ))}
            </div>

            <div className="mb-5">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">
                Detected Skills
              </p>
              <div className="flex flex-wrap gap-2">
                {result.skills_found.map(s => (
                  <span key={s} className="skill-tag">{s}</span>
                ))}
              </div>
            </div>

            {result.education?.length > 0 && (
              <div className="mb-5">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">Education</p>
                {result.education.map((e, i) => (
                  <p key={i} className="text-sm text-gray-600 dark:text-gray-300 py-1.5 border-b border-gray-100 dark:border-white/[0.05] last:border-0">{e}</p>
                ))}
              </div>
            )}

            <div className="flex gap-3 mt-4">
              <button onClick={() => navigate('/gap')} className="btn-primary flex-1 py-3">
                Analyze Skill Gap →
              </button>
              <button onClick={() => { setFile(null); setResult(null); }} className="btn-ghost flex-1 py-3">
                Upload Another
              </button>
            </div>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}