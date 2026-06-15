import { useState, useEffect } from 'react';
import { profileAPI } from '../services/api';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { toast } from 'react-toastify';

const ROLES = [
  'Frontend Developer', 'Backend Developer', 'Full Stack Developer',
  'Data Scientist', 'DevOps Engineer', 'Machine Learning Engineer',
  'React Developer', 'Python Developer', 'Node.js Developer',
  'Mobile Developer', 'Cloud Engineer', 'Cybersecurity Engineer',
];

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('profile');
  const [form, setForm] = useState({
    full_name: '',
    target_role: '',
    bio: '',
    location: '',
    linkedin_url: '',
    github_url: '',
    portfolio_url: '',
  });
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });

  useEffect(() => {
    profileAPI.getProfile()
      .then(res => {
        setProfile(res.data);
        setForm({
          full_name: res.data.full_name || '',
          target_role: res.data.target_role || '',
          bio: res.data.bio || '',
          location: res.data.location || '',
          linkedin_url: res.data.linkedin_url || '',
          github_url: res.data.github_url || '',
          portfolio_url: res.data.portfolio_url || '',
        });
      })
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await profileAPI.updateProfile(form);
      toast.success('Profile updated successfully!');
      setProfile({ ...profile, ...form });
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Update failed');
    } finally {
      setSaving(false);
    }
  };

  const handlePasswordChange = async () => {
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      toast.error('New passwords do not match');
      return;
    }
    if (passwordForm.new_password.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }
    setSaving(true);
    try {
      await profileAPI.changePassword({
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password,
      });
      toast.success('Password changed successfully!');
      setPasswordForm({ current_password: '', new_password: '', confirm_password: '' });
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Password change failed');
    } finally {
      setSaving(false);
    }
  };

  const scoreColor = profile?.readiness_score >= 80 ? '#10b981' :
    profile?.readiness_score >= 60 ? '#22d3ee' :
    profile?.readiness_score >= 40 ? '#f59e0b' : '#ef4444';

  if (loading) return (
    <div className="bg-app bg-grid min-h-screen flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-transparent border-t-blue-500 dark:border-t-cyan-400 rounded-full animate-spin" />
    </div>
  );

  return (
    <div className="bg-app bg-grid min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-4xl mx-auto w-full px-4 sm:px-6 py-10">

        {/* Profile Header Card */}
        <div className="glass-card p-6 mb-6 relative overflow-hidden">
          <div className="absolute inset-0 opacity-30"
            style={{ background: 'linear-gradient(135deg, #0d1b6e22, transparent)' }} />
          <div className="relative flex flex-col sm:flex-row items-start sm:items-center gap-5">

            {/* Avatar */}
            <div className="w-20 h-20 rounded-2xl flex items-center justify-center text-white text-3xl font-display font-bold flex-shrink-0 shadow-glow-navy"
              style={{ background: 'linear-gradient(135deg, #0d1b6e, #1a44ff)' }}>
              {profile?.avatar_letter}
            </div>

            {/* Info */}
            <div className="flex-1">
              <h1 className="text-2xl font-display font-bold text-gray-900 dark:text-white mb-1">
                {profile?.full_name}
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                {profile?.email}
              </p>
              <div className="flex flex-wrap gap-2">
                {profile?.target_role && (
                  <span className="badge-info">{profile.target_role}</span>
                )}
                {profile?.location && (
                  <span className="text-xs text-gray-400">📍 {profile.location}</span>
                )}
                {profile?.member_since && (
                  <span className="text-xs text-gray-400">
                    🗓 Member since {profile.member_since}
                  </span>
                )}
              </div>
            </div>

            {/* Score */}
            <div className="text-center flex-shrink-0">
              <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Readiness</p>
              <p className="text-4xl font-display font-bold" style={{ color: scoreColor }}>
                {profile?.readiness_score || 0}%
              </p>
            </div>
          </div>

          {/* Social Links */}
          {(profile?.linkedin_url || profile?.github_url || profile?.portfolio_url) && (
            <div className="flex flex-wrap gap-3 mt-4 pt-4 border-t border-gray-100 dark:border-white/[0.06]">
              {profile.linkedin_url && (
                <a href={profile.linkedin_url} target="_blank" rel="noreferrer"
                  className="flex items-center gap-1.5 text-xs text-blue-500 hover:text-blue-400 transition-colors">
                  🔗 LinkedIn
                </a>
              )}
              {profile.github_url && (
                <a href={profile.github_url} target="_blank" rel="noreferrer"
                  className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors">
                  🐙 GitHub
                </a>
              )}
              {profile.portfolio_url && (
                <a href={profile.portfolio_url} target="_blank" rel="noreferrer"
                  className="flex items-center gap-1.5 text-xs text-cyan-500 hover:text-cyan-400 transition-colors">
                  🌐 Portfolio
                </a>
              )}
            </div>
          )}
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mb-6 glass-card p-1.5 w-fit">
          {[
            { key: 'profile', label: 'Edit Profile' },
            { key: 'password', label: 'Change Password' },
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-5 py-2 rounded-lg text-sm font-medium transition-all duration-200 border-0 cursor-pointer
                ${activeTab === tab.key
                  ? 'bg-navy-800 dark:bg-cyan-400/20 text-white dark:text-cyan-400'
                  : 'text-gray-500 dark:text-gray-400 bg-transparent hover:text-gray-700 dark:hover:text-gray-200'
                }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Edit Profile Tab */}
        {activeTab === 'profile' && (
          <div className="glass-card p-6">
            <h2 className="text-base font-display font-bold text-gray-800 dark:text-white mb-5">
              Personal Information
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-2">
                  Full Name
                </label>
                <input
                  value={form.full_name}
                  onChange={e => setForm({ ...form, full_name: e.target.value })}
                  className="input-field"
                  placeholder="Your full name"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-2">
                  Target Role
                </label>
                <select
                  value={form.target_role}
                  onChange={e => setForm({ ...form, target_role: e.target.value })}
                  className="input-field"
                >
                  <option value="">Select target role</option>
                  {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-2">
                  Location
                </label>
                <input
                  value={form.location}
                  onChange={e => setForm({ ...form, location: e.target.value })}
                  className="input-field"
                  placeholder="e.g. Lahore, Pakistan"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-2">
                  LinkedIn URL
                </label>
                <input
                  value={form.linkedin_url}
                  onChange={e => setForm({ ...form, linkedin_url: e.target.value })}
                  className="input-field"
                  placeholder="https://linkedin.com/in/yourname"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-2">
                  GitHub URL
                </label>
                <input
                  value={form.github_url}
                  onChange={e => setForm({ ...form, github_url: e.target.value })}
                  className="input-field"
                  placeholder="https://github.com/yourname"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-2">
                  Portfolio URL
                </label>
                <input
                  value={form.portfolio_url}
                  onChange={e => setForm({ ...form, portfolio_url: e.target.value })}
                  className="input-field"
                  placeholder="https://yourportfolio.com"
                />
              </div>
            </div>

            <div className="mb-6">
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-2">
                Bio
              </label>
              <textarea
                value={form.bio}
                onChange={e => setForm({ ...form, bio: e.target.value })}
                className="input-field resize-none"
                rows={3}
                placeholder="Tell us about yourself..."
                maxLength={300}
              />
              <p className="text-xs text-gray-400 mt-1 text-right">
                {form.bio?.length || 0}/300
              </p>
            </div>

            <button
              onClick={handleSave}
              disabled={saving}
              className="btn-primary px-8 py-3"
              style={{ opacity: saving ? 0.7 : 1 }}
            >
              {saving ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Saving...
                </span>
              ) : 'Save Changes'}
            </button>
          </div>
        )}

        {/* Password Tab */}
        {activeTab === 'password' && (
          <div className="glass-card p-6">
            <h2 className="text-base font-display font-bold text-gray-800 dark:text-white mb-5">
              Change Password
            </h2>

            <div className="space-y-4 max-w-md">
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-2">
                  Current Password
                </label>
                <input
                  type="password"
                  value={passwordForm.current_password}
                  onChange={e => setPasswordForm({ ...passwordForm, current_password: e.target.value })}
                  className="input-field"
                  placeholder="••••••••"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-2">
                  New Password
                </label>
                <input
                  type="password"
                  value={passwordForm.new_password}
                  onChange={e => setPasswordForm({ ...passwordForm, new_password: e.target.value })}
                  className="input-field"
                  placeholder="••••••••"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-2">
                  Confirm New Password
                </label>
                <input
                  type="password"
                  value={passwordForm.confirm_password}
                  onChange={e => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })}
                  className="input-field"
                  placeholder="••••••••"
                />
                {passwordForm.new_password &&
                  passwordForm.confirm_password &&
                  passwordForm.new_password !== passwordForm.confirm_password && (
                  <p className="text-xs text-red-400 mt-1">Passwords do not match</p>
                )}
              </div>

              <button
                onClick={handlePasswordChange}
                disabled={saving || !passwordForm.current_password || !passwordForm.new_password}
                className="btn-primary px-8 py-3 mt-2"
                style={{ opacity: saving ? 0.7 : 1 }}
              >
                {saving ? 'Changing...' : 'Change Password'}
              </button>
            </div>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}