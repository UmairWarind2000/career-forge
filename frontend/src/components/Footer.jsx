import { useNavigate } from 'react-router-dom';
import { memo } from 'react';

function Footer() {
  const navigate = useNavigate();
  return (
    <footer className="bg-white/60 dark:bg-navy-950/60 backdrop-blur-sm border-t border-gray-100 dark:border-white/[0.06] mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">

          <div className="lg:col-span-2">
            <div className="flex items-center gap-2.5 mb-3">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center text-white text-xs font-display font-bold"
                style={{ background: 'linear-gradient(135deg,#0d1b6e,#1a44ff)' }}>
                SG
              </div>
              <span className="font-display font-bold text-navy-900 dark:text-white">
                SkillGap<span className="text-blue-500 dark:text-cyan-400">AI</span>
              </span>
            </div>
            <p className="text-sm text-gray-400 dark:text-gray-500 leading-relaxed max-w-xs">
              AI-powered career platform using NLP and Reinforcement Learning to map your path from current skills to your dream role.
            </p>
            <div className="flex items-center gap-1.5 mt-4">
              <div className="glow-dot" />
              <span className="text-xs text-gray-400 dark:text-gray-500 font-mono">All systems operational</span>
            </div>
          </div>

          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500 mb-3">Platform</p>
            <ul className="space-y-2">
              {[
                ['Dashboard', '/dashboard'],
                ['Upload Resume', '/upload'],
                ['Skill Gap Analysis', '/gap'],
                ['Learning Roadmap', '/roadmap'],
                ['Courses', '/courses'],
              ].map(([label, path]) => (
                <li key={path}>
                  <button onClick={() => navigate(path)}
                    className="text-sm text-gray-500 dark:text-gray-400 hover:text-navy-800 dark:hover:text-cyan-400 transition-colors duration-200 bg-transparent border-0 cursor-pointer p-0">
                    {label}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500 mb-3">Technology</p>
            <ul className="space-y-2 text-sm text-gray-500 dark:text-gray-400">
              {['FastAPI Backend', 'React Frontend', 'spaCy NLP Engine', 'Sentence-BERT', 'Q-Learning (RL)', 'PostgreSQL + MongoDB'].map(t => (
                <li key={t} className="flex items-center gap-2">
                  <span className="w-1 h-1 rounded-full bg-blue-400 dark:bg-cyan-400" />
                  {t}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-100 dark:border-white/[0.06] pt-6 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p className="text-xs text-gray-400 dark:text-gray-500 font-mono">
            © {new Date().getFullYear()} SkillGapAI. All rights reserved.
          </p>
          <p className="text-xs text-gray-400 dark:text-gray-500">
            Built with <span className="text-red-400">♥</span> using React · FastAPI · NLP · Reinforcement Learning
          </p>
        </div>
      </div>
    </footer>
  );
}
export default memo(Footer);
