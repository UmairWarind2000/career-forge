import { useState, memo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

function Navbar() {
  const { user, logout } = useAuth();
  const { dark, toggle } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [open, setOpen] = useState(false);

  const links = [
    { label: 'Dashboard', path: '/dashboard' },
    { label: 'Upload', path: '/upload' },
    { label: 'Skill Gap', path: '/gap' },
    { label: 'Roadmap', path: '/roadmap' },
    { label: 'Courses', path: '/courses' },
    { label: 'Jobs', path: '/jobs' },
  ];

  return (
    <nav className="sticky top-0 z-50 bg-white/80 dark:bg-navy-950/80 backdrop-blur-xl border-b border-gray-100/80 dark:border-white/[0.06]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">

        {/* Logo */}
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2.5 border-0 bg-transparent cursor-pointer group"
        >
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center text-white text-xs font-display font-bold shadow-glow-navy transition-transform group-hover:scale-105"
            style={{ background: 'linear-gradient(135deg, #0d1b6e, #1a44ff)' }}
          >
            SG
          </div>
          <span className="font-display font-bold text-navy-900 dark:text-white text-base tracking-tight hidden sm:block">
            SkillGap<span className="text-blue-500 dark:text-cyan-400">AI</span>
          </span>
        </button>

        {/* Desktop links */}
        <div className="hidden md:flex items-center gap-0.5">
          {links.map(l => (
            <button
              key={l.path}
              onClick={() => navigate(l.path)}
              className={`nav-link ${location.pathname === l.path ? 'nav-link-active' : ''}`}
            >
              {l.label}
            </button>
          ))}
        </div>

        {/* Right controls */}
        <div className="flex items-center gap-2">

          {/* Theme toggle */}
          <button
            onClick={toggle}
            className="w-9 h-9 rounded-xl flex items-center justify-center text-base transition-all duration-200 cursor-pointer border-0 bg-gray-100 dark:bg-white/[0.06] hover:bg-gray-200 dark:hover:bg-white/10 text-gray-500 dark:text-gray-300"
          >
            {dark ? '☀️' : '🌙'}
          </button>

          {/* Avatar — clicking goes to profile */}
          <button
            onClick={() => navigate('/profile')}
            className="hidden sm:flex items-center gap-2 border-0 bg-transparent cursor-pointer group"
          >
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold transition-transform group-hover:scale-105"
              style={{ background: 'linear-gradient(135deg, #0d1b6e, #1a44ff)' }}
            >
              {user?.full_name?.charAt(0).toUpperCase()}
            </div>
            <span className="text-sm font-medium text-gray-600 dark:text-gray-300 hidden lg:block max-w-[100px] truncate group-hover:text-navy-800 dark:group-hover:text-white transition-colors">
              {user?.full_name?.split(' ')[0]}
            </span>
          </button>

          {/* Logout */}
          <button
            onClick={() => { logout(); navigate('/login'); }}
            className="hidden sm:block text-xs font-semibold px-3 py-1.5 rounded-lg cursor-pointer border-0 transition-all duration-200 bg-red-50 dark:bg-red-500/10 text-red-500 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-500/20"
          >
            Logout
          </button>

          {/* Mobile hamburger */}
          <button
            onClick={() => setOpen(!open)}
            className="md:hidden w-9 h-9 rounded-xl flex items-center justify-center border-0 cursor-pointer bg-gray-100 dark:bg-white/[0.06] text-gray-500 dark:text-gray-300 text-lg"
          >
            {open ? '✕' : '☰'}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="md:hidden px-4 pb-4 pt-2 border-t border-gray-100 dark:border-white/[0.06] space-y-1 bg-white/90 dark:bg-navy-950/90 backdrop-blur-xl">
          {links.map(l => (
            <button
              key={l.path}
              onClick={() => { navigate(l.path); setOpen(false); }}
              className={`w-full text-left nav-link py-2.5 block ${location.pathname === l.path ? 'nav-link-active' : ''}`}
            >
              {l.label}
            </button>
          ))}
          <button
            onClick={() => { logout(); navigate('/login'); }}
            className="w-full text-left text-sm font-medium px-3 py-2.5 text-red-500 rounded-lg border-0 bg-transparent cursor-pointer hover:bg-red-50 dark:hover:bg-red-500/10"
          >
            Logout
          </button>
        </div>
      )}
    </nav>
  );
}

export default memo(Navbar);