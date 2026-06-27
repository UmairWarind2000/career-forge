import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { gapAPI, jobsAPI } from '../services/api';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { toast } from 'react-toastify';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function GapAnalysis() {
  const [roles, setRoles] = useState([]);
  const [role, setRole] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const navigate = useNavigate();

  useEffect(() => { jobsAPI.getRoles().then(r => setRoles(r.data.roles)); }, []);

 const handleAnalyze = async () => {
    if (!role) {
      toast.error('Please select a target role');
      return;
    }
    setLoading(true);
    try {
      const res = await gapAPI.analyze({ target_role: role });
      setResult(res.data);
      // Save the analyzed role so Roadmap page can use it automatically
      localStorage.setItem('lastAnalyzedRole', role);
      toast.success('Analysis complete!');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Analysis failed');
    } finally {
      setLoading(false);
    }
};

  const scoreVal = result?.analysis?.readiness_score || 0;
  const scoreColor = scoreVal >= 80 ? '#10b981' : scoreVal >= 60 ? '#22d3ee' : scoreVal >= 40 ? '#f59e0b' : '#ef4444';

  const chartData = result ? [
    { name: 'Exact Match', value: result.analysis.match_breakdown.exact_matches, fill: '#10b981' },
    { name: 'Similar', value: result.analysis.match_breakdown.semantic_matches, fill: '#22d3ee' },
    { name: 'Missing', value: result.analysis.match_breakdown.missing, fill: '#ef4444' },
  ] : [];

  return (
    <div className="bg-app bg-grid min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-4xl mx-auto w-full px-4 sm:px-6 py-10">

        <h1 className="page-title">Skill Gap Analysis</h1>
        <p className="page-sub">AI-powered comparison of your skills vs job requirements</p>

        {/* Selector */}
        <div className="glass-card p-6 mb-6">
          <div className="mb-4">
            <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-2">
              <span className="w-1 h-1 rounded-full bg-blue-500 dark:bg-cyan-400"></span>
              Select Target Role
            </p>
          </div>
          <div className="flex gap-3 flex-col sm:flex-row">
            <div className="relative flex-1">
              <select value={role} onChange={e => setRole(e.target.value)} className="input-field w-full appearance-none pr-10">
                <option value="">Choose a role...</option>
                {roles.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
              <div className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 flex items-center">
                <svg className="w-5 h-5 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                </svg>
              </div>
            </div>
            <button onClick={handleAnalyze} disabled={loading || !role}
              className="btn-primary px-8 py-2.5 whitespace-nowrap"
              style={{ opacity: loading || !role ? 0.6 : 1 }}>
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Analyzing...
                </span>
              ) : 'Analyze →'}
            </button>
          </div>
        </div>

        {result && (
          <div className="space-y-4">

            {/* Score Banner */}
            <div className="glass-card p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
              style={{ borderColor: `${scoreColor}30`, boxShadow: `0 0 20px ${scoreColor}15` }}>
              <div>
                <p className="text-xs font-mono text-gray-400 uppercase tracking-widest mb-1">Readiness Level</p>
                <h2 className="text-2xl font-display font-bold mb-1" style={{ color: scoreColor }}>
                  {result.analysis.readiness_level}
                </h2>
                <p className="text-sm text-gray-500 dark:text-gray-400 max-w-md">{result.analysis.message}</p>
              </div>
              <div className="text-5xl font-display font-bold flex-shrink-0" style={{ color: scoreColor }}>
                {scoreVal}%
              </div>
            </div>

            {/* Chart + Matched */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div className="glass-card p-6">
                <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-4">Match Breakdown</h3>
                <div style={{ height: 180 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.1)" />
                      <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                      <Tooltip contentStyle={{ background: '#0f1542', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }} />
                      <Bar dataKey="value" radius={[4,4,0,0]}>
                        {chartData.map((entry, i) => (
                          <rect key={i} fill={entry.fill} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex justify-around mt-3">
                  {[
                    { label: 'Exact', val: result.analysis.match_breakdown.exact_matches, color: '#10b981' },
                    { label: 'Similar', val: result.analysis.match_breakdown.semantic_matches, color: '#22d3ee' },
                    { label: 'Missing', val: result.analysis.match_breakdown.missing, color: '#ef4444' },
                  ].map(s => (
                    <div key={s.label} className="text-center">
                      <p className="text-2xl font-display font-bold" style={{ color: s.color }}>{s.val}</p>
                      <p className="text-xs text-gray-400 uppercase tracking-wider">{s.label}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="glass-card p-6">
                <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-4">Matched Skills</h3>
                <div className="flex flex-wrap gap-2">
                  {result.analysis.exactly_matched.map(s => (
                    <span key={s} className="badge-success">{s}</span>
                  ))}
                  {result.analysis.semantically_matched.map(m => (
                    <span key={m.required_skill} className="badge-info" title={`Similar to: ${m.matched_with}`}>
                      {m.required_skill} ~
                    </span>
                  ))}
                  {result.analysis.exactly_matched.length === 0 && result.analysis.semantically_matched.length === 0 && (
                    <p className="text-sm text-gray-400">No matching skills found</p>
                  )}
                </div>
              </div>
            </div>

            {/* Missing Skills */}
            {result.analysis.missing_skills.length > 0 && (
              <div className="glass-card p-6">
                <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-4">
                  Skills to Learn
                  <span className="ml-2 badge-danger">{result.analysis.missing_skills.length}</span>
                </h3>
                <div className="space-y-2">
                  {result.analysis.missing_skills.map(item => (
                    <div key={item.skill} className="flex items-center gap-3 p-3 rounded-xl bg-gray-50 dark:bg-white/[0.03] border border-gray-100 dark:border-white/[0.06]">
                      <span className={item.priority === 'high' ? 'badge-danger' : item.priority === 'medium' ? 'badge-warning' : 'badge-success'}>
                        {item.priority}
                      </span>
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-200 flex-1 capitalize">{item.skill}</span>
                      <div className="w-24 h-1.5 rounded-full bg-gray-200 dark:bg-white/10 overflow-hidden">
                        <div className="h-full rounded-full transition-all duration-500"
                          style={{ width: `${Math.min(item.weight / 2 * 100, 100)}%`, background: item.priority === 'high' ? '#ef4444' : item.priority === 'medium' ? '#f59e0b' : '#10b981' }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex gap-3 flex-col sm:flex-row">
              <button onClick={() => navigate('/roadmap', { state: { targetRole: role } })} className="btn-primary flex-1 py-3.5">
                Generate Learning Roadmap
              </button>
              <button onClick={() => navigate('/courses')} className="btn-ghost flex-1 py-3.5">
                Find Courses
              </button>
            </div>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}