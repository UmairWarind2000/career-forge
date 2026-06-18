import { useState, useEffect, useCallback } from 'react';
import { liveJobsAPI, gapAPI } from '../services/api';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { toast } from 'react-toastify';

export default function Jobs() {

    const [jobs, setJobs] = useState([]);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(false);
    const [selectedJob, setSelectedJob] = useState(null);

    const [filters, setFilters] = useState({
        query: 'software developer',
        location: 'Pakistan',
        remote_only: false,
        employment_type: '',
    });

    const [userScore, setUserScore] = useState(null);
    const [page, setPage] = useState(1);


    const fetchJobs = useCallback(async (customFilters = null, pageNum = 1) => {

        setLoading(true);

        try {
            const f = customFilters || filters;

            const res = await liveJobsAPI.search({
                ...f,
                page: pageNum
            });

            setJobs(res.data.jobs || []);
            setPage(pageNum);

        } catch (err) {

            toast.error('Failed to fetch jobs');

        } finally {

            setLoading(false);

        }

    }, [filters]);


    useEffect(() => {

        liveJobsAPI
            .getCategories()
            .then(r => setCategories(r.data.categories));


        gapAPI
            .getScore()
            .then(r => setUserScore(r.data))
            .catch(() => { });


        fetchJobs();

    }, [fetchJobs]);



    const handleCategoryClick = (query) => {

        const newFilters = {
            ...filters,
            query
        };

        setFilters(newFilters);

        fetchJobs(newFilters);

    };


    const handleSearch = (e) => {

        e.preventDefault();

        fetchJobs();

    };


    const getMatchScore = (jobSkills) => {

        if (!userScore || !jobSkills?.length) return null;

        return userScore.readiness_score;

    };


    const getMatchColor = (score) => {

        if (!score) return null;

        if (score >= 80) return 'text-emerald-500';
        if (score >= 60) return 'text-cyan-400';
        if (score >= 40) return 'text-amber-400';

        return 'text-red-400';
    };


    const formatDate = (dateStr) => {

        if (!dateStr) return 'Recently';

        const date = new Date(dateStr);

        const days = Math.floor(
            (Date.now() - date) /
            (1000 * 60 * 60 * 24)
        );

        if (days === 0) return 'Today';
        if (days === 1) return 'Yesterday';
        if (days < 7) return `${days} days ago`;
        if (days < 30) return `${Math.floor(days / 7)} weeks ago`;

        return `${Math.floor(days / 30)} months ago`;
    };



return (
    <div className="bg-app bg-grid min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">

            {/* Header */}
            <div className="mb-6">
                <h1 className="page-title">Tech Job Board</h1>
                <p className="page-sub">
                    Live tech job postings — click any job to view details and apply
                </p>
            </div>

            {/* Search Bar */}
            <form onSubmit={handleSearch} className="glass-card p-4 mb-6">
                <div className="flex flex-col sm:flex-row gap-3">
                    <input
                        value={filters.query}
                        onChange={e => setFilters({ ...filters, query: e.target.value })}
                        placeholder="Job title, skill, or keyword..."
                        className="input-field flex-1"
                    />
                    <input
                        value={filters.location}
                        onChange={e => setFilters({ ...filters, location: e.target.value })}
                        placeholder="Location..."
                        className="input-field sm:w-40"
                    />
                    <select
                        value={filters.employment_type}
                        onChange={e => setFilters({ ...filters, employment_type: e.target.value })}
                        className="input-field sm:w-36"
                    >
                        <option value="">All Types</option>
                        <option value="FULLTIME">Full Time</option>
                        <option value="PARTTIME">Part Time</option>
                        <option value="CONTRACTOR">Contract</option>
                        <option value="INTERN">Internship</option>
                    </select>
                    <label className="flex items-center gap-2 cursor-pointer whitespace-nowrap">
                        <input
                            type="checkbox"
                            checked={filters.remote_only}
                            onChange={e => setFilters({ ...filters, remote_only: e.target.checked })}
                            className="w-4 h-4 accent-blue-500"
                        />
                        <span className="text-sm text-gray-600 dark:text-gray-300">Remote only</span>
                    </label>
                    <button type="submit" className="btn-primary px-6 whitespace-nowrap">
                        Search
                    </button>
                </div>
            </form>

            {/* Categories */}
            <div className="flex flex-wrap gap-2 mb-6">
                {categories.map(cat => (
                    <button
                        key={cat.query}
                        onClick={() => handleCategoryClick(cat.query)}
                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-sm font-medium transition-all duration-200 cursor-pointer border
                ${filters.query === cat.query
                                ? 'bg-navy-800 dark:bg-cyan-400/20 text-white dark:text-cyan-400 border-navy-700 dark:border-cyan-400/30'
                                : 'bg-white dark:bg-white/[0.04] text-gray-600 dark:text-gray-300 border-gray-200 dark:border-white/10 hover:border-navy-300 dark:hover:border-white/20'
                            }`}
                    >
                        <span>{cat.icon}</span>
                        <span>{cat.label}</span>
                    </button>
                ))}
            </div>

            {/* Main Content */}
            <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">

                {/* Job List */}
                <div className="lg:col-span-2 space-y-3">
                    {loading ? (
                        <div className="flex flex-col gap-3">
                            {[1, 2, 3, 4, 5].map(i => (
                                <div key={i} className="glass-card p-5 animate-pulse">
                                    <div className="h-4 bg-gray-200 dark:bg-white/10 rounded mb-3 w-3/4" />
                                    <div className="h-3 bg-gray-200 dark:bg-white/10 rounded mb-2 w-1/2" />
                                    <div className="h-3 bg-gray-200 dark:bg-white/10 rounded w-2/3" />
                                </div>
                            ))}
                        </div>
                    ) : jobs.length === 0 ? (
                        <div className="glass-card p-12 text-center">
                            <div className="text-4xl mb-3">🔍</div>
                            <p className="text-gray-500 dark:text-gray-400 text-sm">
                                No jobs found. Try different keywords.
                            </p>
                        </div>
                    ) : (
                        <>
                            <p className="text-xs text-gray-400 font-mono mb-2">
                                {jobs.length} tech jobs found
                            </p>
                            {jobs.map(job => {
                                const match = getMatchScore(job.required_skills);
                                const isSelected = selectedJob?.id === job.id;
                                return (
                                    <button
                                        key={job.id}
                                        onClick={() => setSelectedJob(job)}
                                        className={`w-full text-left glass-card p-4 transition-all duration-200 cursor-pointer border-0
                        ${isSelected
                                                ? 'ring-2 ring-blue-500 dark:ring-cyan-400 shadow-glow-cyan'
                                                : 'hover:shadow-md'
                                            }`}
                                    >
                                        <div className="flex items-start justify-between gap-2 mb-2">
                                            <div className="flex-1 min-w-0">
                                                <h3 className="text-sm font-semibold text-gray-800 dark:text-white truncate">
                                                    {job.title}
                                                </h3>
                                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                                                    {job.company}
                                                </p>
                                            </div>
                                            {match && (
                                                <span className={`text-xs font-bold flex-shrink-0 ${getMatchColor(match)}`}>
                                                    {match}%
                                                </span>
                                            )}
                                        </div>

                                        <div className="flex flex-wrap items-center gap-1.5 mb-2">
                                            <span className="text-xs text-gray-400 flex items-center gap-1">
                                                📍 {job.location}
                                            </span>
                                            {job.is_remote && (
                                                <span className="badge-success text-xs">Remote</span>
                                            )}
                                            <span className="badge-info text-xs">{job.employment_type}</span>
                                        </div>

                                        <div className="flex flex-wrap gap-1">
                                            {job.required_skills?.slice(0, 3).map(skill => (
                                                <span key={skill} className="skill-tag text-xs">{skill}</span>
                                            ))}
                                            {job.required_skills?.length > 3 && (
                                                <span className="text-xs text-gray-400">
                                                    +{job.required_skills.length - 3}
                                                </span>
                                            )}
                                        </div>

                                        <p className="text-xs text-gray-400 mt-2 flex items-center justify-between">
                                            <span>{formatDate(job.posted_at)}</span>
                                            <span className="text-gray-300 dark:text-gray-600">{job.source}</span>
                                        </p>
                                    </button>
                                );
                            })}

                            {/* Pagination */}
                            <div className="flex items-center justify-between pt-2">
                                <button
                                    onClick={() => fetchJobs(null, Math.max(1, page - 1))}
                                    disabled={page === 1 || loading}
                                    className="btn-ghost text-sm px-4 py-2"
                                    style={{ opacity: page === 1 ? 0.4 : 1 }}
                                >
                                    ← Previous
                                </button>
                                <span className="text-xs text-gray-400 font-mono">Page {page}</span>
                                <button
                                    onClick={() => fetchJobs(null, page + 1)}
                                    disabled={loading}
                                    className="btn-ghost text-sm px-4 py-2"
                                >
                                    Next →
                                </button>
                            </div>
                        </>
                    )}
                </div>

                {/* Job Detail Panel */}
                <div className="lg:col-span-3">
                    {selectedJob ? (
                        <div className="glass-card p-6 sticky top-24">

                            {/* Job Header */}
                            <div className="flex items-start gap-4 mb-5 pb-5 border-b border-gray-100 dark:border-white/[0.06]">
                                <div className="w-14 h-14 rounded-xl bg-navy-50 dark:bg-navy-800 flex items-center justify-center text-2xl flex-shrink-0 border border-gray-100 dark:border-white/10">
                                    {selectedJob.company_logo ? (
                                        <img src={selectedJob.company_logo} alt={selectedJob.company}
                                            className="w-full h-full object-contain rounded-xl" />
                                    ) : (
                                        selectedJob.company?.charAt(0).toUpperCase()
                                    )}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <h2 className="text-xl font-display font-bold text-gray-900 dark:text-white mb-1">
                                        {selectedJob.title}
                                    </h2>
                                    <p className="text-sm font-medium text-gray-600 dark:text-gray-300">
                                        {selectedJob.company}
                                    </p>
                                    <div className="flex flex-wrap gap-2 mt-2">
                                        <span className="text-xs text-gray-400 flex items-center gap-1">
                                            📍 {selectedJob.location}
                                        </span>
                                        {selectedJob.is_remote && <span className="badge-success">Remote</span>}
                                        <span className="badge-info">{selectedJob.employment_type}</span>
                                        <span className="text-xs text-gray-400">
                                            🕒 {formatDate(selectedJob.posted_at)}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            {/* Salary */}
                            {selectedJob.salary_min && (
                                <div className="glass-card p-4 mb-4 bg-emerald-50/50 dark:bg-emerald-900/10 border-emerald-100 dark:border-emerald-800/30">
                                    <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Salary Range</p>
                                    <p className="text-lg font-display font-bold text-emerald-600 dark:text-emerald-400">
                                        {selectedJob.salary_currency} {selectedJob.salary_min?.toLocaleString()} —{' '}
                                        {selectedJob.salary_max?.toLocaleString()}
                                    </p>
                                </div>
                            )}

                            {/* Match Score */}
                            {userScore?.readiness_score > 0 && (
                                <div className="glass-card p-4 mb-4">
                                    <div className="flex items-center justify-between mb-2">
                                        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                                            Your Match Score
                                        </p>
                                        <span className={`text-lg font-display font-bold ${getMatchColor(userScore.readiness_score)}`}>
                                            {userScore.readiness_score}%
                                        </span>
                                    </div>
                                    <div className="w-full h-2 bg-gray-100 dark:bg-white/10 rounded-full overflow-hidden">
                                        <div
                                            className="h-full rounded-full transition-all duration-500"
                                            style={{
                                                width: `${userScore.readiness_score}%`,
                                                background: userScore.readiness_score >= 80 ? '#10b981' :
                                                    userScore.readiness_score >= 60 ? '#22d3ee' :
                                                        userScore.readiness_score >= 40 ? '#f59e0b' : '#ef4444'
                                            }}
                                        />
                                    </div>
                                    <p className="text-xs text-gray-400 mt-1.5">{userScore.readiness_level}</p>
                                </div>
                            )}

                            {/* Required Skills */}
                            {selectedJob.required_skills?.length > 0 && (
                                <div className="mb-4">
                                    <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                                        Required Skills
                                    </p>
                                    <div className="flex flex-wrap gap-2">
                                        {selectedJob.required_skills.map(skill => (
                                            <span key={skill} className="skill-tag">{skill}</span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Highlights */}
                            {selectedJob.highlights?.responsibilities?.length > 0 && (
                                <div className="mb-4">
                                    <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                                        Responsibilities
                                    </p>
                                    <ul className="space-y-1.5">
                                        {selectedJob.highlights.responsibilities.map((r, i) => (
                                            <li key={i} className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-300">
                                                <span className="text-cyan-400 mt-0.5 flex-shrink-0">▸</span>
                                                {r}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {selectedJob.highlights?.qualifications?.length > 0 && (
                                <div className="mb-4">
                                    <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                                        Qualifications
                                    </p>
                                    <ul className="space-y-1.5">
                                        {selectedJob.highlights.qualifications.map((q, i) => (
                                            <li key={i} className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-300">
                                                <span className="text-blue-400 mt-0.5 flex-shrink-0">▸</span>
                                                {q}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {/* Description */}
                            <div className="mb-5">
                                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                                    About the Role
                                </p>
                                <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed line-clamp-4">
                                    {selectedJob.description}
                                </p>
                            </div>

                            {/* Apply Button */}
                            <a
                                href={selectedJob.apply_link}
                                target="_blank"
                                rel="noreferrer"
                                className="btn-primary w-full py-3.5 text-center text-base block mt-4 no-underline"
                            >
                                Apply Now →
                            </a>
                            <p className="text-center text-xs text-gray-400 mt-2">
                                You will be redirected to {selectedJob.source}
                            </p>
                        </div>

                    ) : (
                        <div className="glass-card p-16 text-center sticky top-24">
                            <div className="text-5xl mb-4">💼</div>
                            <h3 className="text-lg font-display font-bold text-gray-700 dark:text-gray-200 mb-2">
                                Select a job to view details
                            </h3>
                            <p className="text-sm text-gray-400 max-w-xs mx-auto">
                                Click any job from the list to see full details and apply
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </main >
        <Footer />
    </div >
);
}