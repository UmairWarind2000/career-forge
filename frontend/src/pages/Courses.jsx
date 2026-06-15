import { useState, useEffect } from 'react';
import { coursesAPI } from '../services/api';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { toast } from 'react-toastify';

const platformColors = {
  Coursera: 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400',
  Udemy: 'bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400',
  freeCodeCamp: 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400',
  'LinkedIn Learning': 'bg-sky-50 dark:bg-sky-900/20 text-sky-600 dark:text-sky-400',
};

function CourseCard({ course }) {
  const pClass = platformColors[course.platform] || 'bg-gray-100 dark:bg-white/10 text-gray-500 dark:text-gray-400';
  return (
    <div className="glass-card p-5 flex flex-col gap-3 hover:shadow-md transition-shadow duration-200">
      <div className="flex items-center justify-between gap-2">
        <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${pClass}`}>
          {course.platform}
        </span>
        {course.free_audit && (
          <span className="badge-success text-xs">Free Audit</span>
        )}
      </div>
      <div>
        <h4 className="text-sm font-semibold text-gray-800 dark:text-gray-100 leading-snug mb-1">
          {course.title}
        </h4>
        <p className="text-xs text-gray-400">by {course.provider}</p>
      </div>
      <div className="flex items-center gap-3 text-xs text-gray-400">
        <span>⭐ {course.rating}</span>
        <span>⏱ {course.duration}</span>
        <span className="badge-info">{course.level}</span>
      </div>
      <a href={course.url} target="_blank" rel="noreferrer"
        className="btn-primary text-center text-sm py-2.5 mt-auto rounded-xl no-underline">
        View Course →
      </a>
    </div>
  );
}

export default function Courses() {
  const [recs, setRecs] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [searchRes, setSearchRes] = useState(null);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    coursesAPI.getForMyRoadmap()
      .then(r => setRecs(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleSearch = async () => {
    if (!search.trim()) return;
    setSearching(true);
    try {
      const res = await coursesAPI.search(search);
      setSearchRes(res.data);
    } catch { toast.error('Search failed'); }
    finally { setSearching(false); }
  };

  return (
    <div className="bg-app bg-grid min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 sm:px-6 py-10">

        <h1 className="page-title">Course Recommendations</h1>
        <p className="page-sub">Curated learning resources mapped to your skill gaps</p>

        {/* Search */}
        <div className="glass-card p-5 mb-6">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">Search by Skill</p>
          <div className="flex gap-3 flex-col sm:flex-row">
            <input value={search} onChange={e => setSearch(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSearch()}
              placeholder="e.g. python, react, docker..."
              className="input-field flex-1" />
            <button onClick={handleSearch} disabled={searching}
              className="btn-primary px-8 whitespace-nowrap"
              style={{ opacity: searching ? 0.7 : 1 }}>
              {searching ? 'Searching...' : 'Search'}
            </button>
          </div>
        </div>

        {searchRes && (
          <div className="mb-8">
            <h2 className="text-base font-display font-bold text-gray-800 dark:text-white mb-4">
              Results for <span className="text-blue-500 dark:text-cyan-400">"{searchRes.skill}"</span>
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {searchRes.courses.map((c, i) => <CourseCard key={i} course={c} />)}
            </div>
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center py-20 gap-3 text-gray-400">
            <span className="w-5 h-5 border-2 border-gray-200 border-t-blue-500 dark:border-t-cyan-400 rounded-full animate-spin" />
            Loading recommendations...
          </div>
        )}

        {!loading && recs && (
          <>
            <div className="grid grid-cols-3 gap-3 mb-8">
              {[
                { label: 'Total Courses', val: recs.total_courses_recommended, color: 'text-blue-500 dark:text-cyan-400' },
                { label: 'Free Available', val: recs.free_courses_available, color: 'text-emerald-500' },
                { label: 'Skills Covered', val: recs.total_skills_in_roadmap, color: 'text-purple-500' },
              ].map(s => (
                <div key={s.label} className="glass-card p-4 text-center">
                  <p className={`text-3xl font-display font-bold ${s.color}`}>{s.val}</p>
                  <p className="text-xs text-gray-400 uppercase tracking-wider mt-1">{s.label}</p>
                </div>
              ))}
            </div>

            {recs.recommendations.map(rec => (
              <div key={rec.skill} className="mb-8">
                <div className="flex flex-wrap items-center gap-2 mb-4">
                  <h3 className="text-lg font-display font-bold text-gray-800 dark:text-white capitalize">
                    {rec.skill}
                  </h3>
                  <span className="badge-info text-xs">Step {rec.step}</span>
                  <span className={rec.priority === 'high' ? 'badge-danger' : rec.priority === 'medium' ? 'badge-warning' : 'badge-success'}>
                    {rec.priority}
                  </span>
                  <span className="text-xs text-gray-400 font-mono">{rec.estimated_weeks}w</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {rec.courses.map((c, i) => <CourseCard key={i} course={c} />)}
                </div>
              </div>
            ))}
          </>
        )}

        {!loading && !recs && !searchRes && (
          <div className="glass-card p-16 text-center">
            <div className="text-5xl mb-4">📚</div>
            <h3 className="text-lg font-display font-bold text-gray-700 dark:text-gray-200 mb-2">No recommendations yet</h3>
            <p className="text-sm text-gray-400 max-w-xs mx-auto">
              Generate a roadmap first, or search for any skill above
            </p>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}