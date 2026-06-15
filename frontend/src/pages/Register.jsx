import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-toastify';

const ROLES = [
  'Frontend Developer','Backend Developer','Full Stack Developer',
  'Data Scientist','DevOps Engineer','Machine Learning Engineer',
  'React Developer','Python Developer','Node.js Developer',
];

export default function Register() {
  const [form, setForm] = useState({ fullName:'', email:'', password:'', targetRole:'' });
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await register(form.fullName, form.email, form.password, form.targetRole);
      toast.success('Account created!');
      navigate('/dashboard');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-navy-950 bg-grid bg-glow flex items-center justify-center px-4 py-12 relative overflow-hidden">

      <div className="absolute top-1/3 right-1/4 w-72 h-72 rounded-full opacity-15 blur-3xl pointer-events-none"
        style={{ background: 'radial-gradient(circle, #1a44ff, transparent)' }} />
      <div className="absolute bottom-1/3 left-1/4 w-48 h-48 rounded-full opacity-10 blur-3xl pointer-events-none"
        style={{ background: 'radial-gradient(circle, #22d3ee, transparent)' }} />

      <div className="w-full max-w-md relative z-10">
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl flex items-center justify-center text-white font-display font-bold text-lg mx-auto mb-4 shadow-glow-cyan"
            style={{ background: 'linear-gradient(135deg, #0d1b6e, #22d3ee)' }}>
            SG
          </div>
          <h1 className="text-3xl font-display font-bold text-white mb-1">Start your journey</h1>
          <p className="text-sm text-gray-400">Create your SkillGapAI account</p>
        </div>

        <div className="glass-card p-8 dark">
          <form onSubmit={handleSubmit} className="space-y-4">
            {[
              { label:'Full Name', key:'fullName', type:'text', placeholder:'Ahmed Ali' },
              { label:'Email', key:'email', type:'email', placeholder:'you@example.com' },
              { label:'Password', key:'password', type:'password', placeholder:'••••••••' },
            ].map(f => (
              <div key={f.key}>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-2">
                  {f.label}
                </label>
                <input type={f.type} value={form[f.key]} placeholder={f.placeholder} required
                  onChange={e => setForm({ ...form, [f.key]: e.target.value })}
                  className="input-field dark" />
              </div>
            ))}

            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-2">
                Target Role
              </label>
              <select value={form.targetRole} required
                onChange={e => setForm({ ...form, targetRole: e.target.value })}
                className="input-field dark">
                <option value="">Select your goal role...</option>
                {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>

            <button type="submit" disabled={loading}
              className="btn-primary w-full py-3 text-base dark mt-2"
              style={{ opacity: loading ? 0.7 : 1 }}>
              {loading ? 'Creating account...' : 'Create account →'}
            </button>
          </form>

          <p className="text-center text-sm text-gray-500 mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-cyan-400 hover:text-cyan-300 font-semibold transition-colors">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}