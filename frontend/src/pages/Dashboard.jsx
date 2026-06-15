import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { gapAPI, resumeAPI } from '../services/api';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import SkillTags from '../components/SkillTags';
import { RadialBarChart, RadialBar, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [score, setScore] = useState(null);
  const [resume, setResume] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.allSettled([gapAPI.getScore(), resumeAPI.getMyResume(), gapAPI.getHistory()])
      .then(([s, r, h]) => {
        if (s.status === 'fulfilled') setScore(s.value.data);
        if (r.status === 'fulfilled') setResume(r.value.data);
        if (h.status === 'fulfilled') setHistory(h.value.data.history);
      }).finally(() => setLoading(false));
  }, []);

  const scoreVal = score?.readiness_score || 0;
  const scoreColor = scoreVal >= 80 ? '#10b981' : scoreVal >= 60 ? '#22d3ee' : scoreVal >= 40 ? '#f59e0b' : '#ef4444';

  const chartData = history.slice(0, 6).map((h, i) => ({
    name: `#${i + 1}`, score: h.analysis?.readiness_score || 0,
  }));

  if (loading) return (
    <div className="min-h-screen bg-app bg-grid flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="w-10 h-10 rounded-full border-2 border-transparent border-t-blue-500 dark:border-t-cyan-400 animate-spin" />
        <p className="text-sm text-gray-400 font-mono">Loading dashboard...</p>
      </div>
    </div>
  );

  return (
    <div className="bg-app bg-grid min-h-screen flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">

        {/* Hero Banner */}
        <div className="relative overflow-hidden rounded-2xl p-6 sm:p-8 mb-6"
          style={{ background: 'linear-gradient(135deg, #0d1b6e 0%, #0f1542 60%, #060b2e 100%)' }}>
          <div className="absolute inset-0 bg-grid opacity-20" />
          <div
            className="absolute top-0 right-0 w-64 h-64 rounded-full opacity-20 blur-3xl pointer-events-none"
            style={{
              background: 'radial-gradient(circle, #22d3ee, transparent)',
              transform: 'translateZ(0)',  // GPU layer
              willChange: 'auto',
            }}
          />
          <div className="relative z-10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <div className="glow-dot" />
                <span className="text-xs text-cyan-400 font-mono font-medium uppercase tracking-widest">
                  AI Career Platform
                </span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-display font-bold text-white mb-1">
                Welcome back, {user?.full_name?.split(' ')[0]}
              </h1>
              <p className="text-sm text-gray-400">
                Target: <span className="text-cyan-400 font-medium">{user?.target_role || 'Not set'}</span>
              </p>
            </div>
            <button onClick={() => navigate('/gap')}
              className="btn-primary dark px-6 py-3 text-sm whitespace-nowrap flex-shrink-0">
              Run Analysis →
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6">
          {[
            { label: 'Readiness Score', value: `${scoreVal}%`, color: scoreColor, sub: score?.readiness_level || 'Not analyzed' },
            { label: 'Skills Detected', value: resume?.parsed_data?.total_skills_found || 0, color: '#22d3ee', sub: 'From your resume' },
            { label: 'Analyses Run', value: history.length, color: '#818cf8', sub: 'Total sessions' },
            { label: 'Target Role', value: user?.target_role?.split(' ').slice(0, 2).join(' ') || '—', color: '#34d399', sub: 'Current goal', small: true },
          ].map((s) => (
            <div key={s.label} className="glass-card p-4 sm:p-5">
              <p className="stat-label mb-2">{s.label}</p>
              <p className={`font-display font-bold mb-0.5 ${s.small ? 'text-lg' : 'text-2xl sm:text-3xl'}`}
                style={{ color: s.color }}>
                {s.value}
              </p>
              <p className="text-xs text-gray-400 dark:text-gray-500">{s.sub}</p>
            </div>
          ))}
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">

          {/* Gauge */}
          <div className="glass-card p-6 relative">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-4">
              Readiness Gauge
            </h3>
            <div style={{ height: 200 }}>
              <ResponsiveContainer width="100%" height="100%">
                <RadialBarChart cx="50%" cy="65%" innerRadius="55%" outerRadius="85%"
                  startAngle={180} endAngle={0}
                  data={[{ value: scoreVal, fill: scoreColor }]}>
                  <RadialBar dataKey="value" cornerRadius={6} />
                </RadialBarChart>
              </ResponsiveContainer>
            </div>
            <div className="absolute bottom-10 left-1/2 -translate-x-1/2 text-center">
              <p className="text-3xl font-display font-bold" style={{ color: scoreColor }}>
                {scoreVal}%
              </p>
              <p className="text-xs text-gray-400 mt-0.5">
                {score?.readiness_level || 'Run analysis'}
              </p>
            </div>
          </div>

          {/* History chart */}
          <div className="glass-card p-6">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-4">
              Score History
            </h3>
            {chartData.length > 0 ? (
              <div style={{ height: 200 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.1)" />
                    <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                    <Tooltip
                      contentStyle={{ background: '#0f1542', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }}
                      labelStyle={{ color: '#94a3b8' }}
                      itemStyle={{ color: '#22d3ee' }}
                    />
                    <Bar dataKey="score" fill="url(#barGrad)" radius={[4, 4, 0, 0]} />
                    <defs>
                      <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#22d3ee" stopOpacity={0.9} />
                        <stop offset="100%" stopColor="#1a44ff" stopOpacity={0.7} />
                      </linearGradient>
                    </defs>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-[200px] flex flex-col items-center justify-center text-center gap-2">
                <p className="text-sm text-gray-400">No history yet</p>
                <p className="text-xs text-gray-500">Run your first analysis to track progress</p>
              </div>
            )}
          </div>
        </div>

        {/* Bottom row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">

          {/* Skills */}
          <SkillTags skills={resume.parsed_data.skills} maxVisible={20} />

          {/* Quick Actions */}
          <div className="glass-card p-6">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-4">
              Quick Actions
            </h3>
            <div className="space-y-2">
              {[
                { label: 'Upload Resume', desc: 'Auto-extract your skills', path: '/upload', accent: '#22d3ee' },
                { label: 'Analyze Skill Gap', desc: 'Compare with job requirements', path: '/gap', accent: '#818cf8' },
                { label: 'View Roadmap', desc: 'Your AI learning plan', path: '/roadmap', accent: '#34d399' },
                { label: 'Find Courses', desc: 'Curated course recommendations', path: '/courses', accent: '#f59e0b' },
              ].map(a => (
                <button key={a.path} onClick={() => navigate(a.path)}
                  className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-left transition-all duration-200 border-0 cursor-pointer bg-gray-50 dark:bg-white/[0.03] hover:bg-gray-100 dark:hover:bg-white/[0.06] border border-transparent hover:border-gray-200 dark:hover:border-white/10 group">
                  <div className="w-2 h-2 rounded-full flex-shrink-0 transition-transform group-hover:scale-125"
                    style={{ background: a.accent, boxShadow: `0 0 8px ${a.accent}80` }} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-gray-700 dark:text-gray-200">{a.label}</p>
                    <p className="text-xs text-gray-400">{a.desc}</p>
                  </div>
                  <span className="text-gray-300 dark:text-gray-600 group-hover:translate-x-1 transition-transform text-sm">→</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}