import { useState } from 'react';

export default function SkillTags({ skills = [], maxVisible = 20 }) {
  const [showAll, setShowAll] = useState(false);

  const visible = showAll ? skills : skills.slice(0, maxVisible);
  const hidden = skills.length - maxVisible;

  return (
    <div>
      <div className="flex flex-wrap gap-2">
        {visible.map((skill) => (
          <span key={skill} className="skill-tag">{skill}</span>
        ))}
        {!showAll && hidden > 0 && (
          <button
            onClick={() => setShowAll(true)}
            className="px-3 py-1 rounded-full text-xs font-medium
              bg-navy-800/60 text-cyan-400 border border-navy-700/60
              hover:bg-navy-700 transition-all duration-200 cursor-pointer"
          >
            +{hidden} more
          </button>
        )}
        {showAll && hidden > 0 && (
          <button
            onClick={() => setShowAll(false)}
            className="px-3 py-1 rounded-full text-xs font-medium
              bg-navy-800/60 text-gray-400 border border-navy-700/60
              hover:bg-navy-700 transition-all duration-200 cursor-pointer"
          >
            Show less
          </button>
        )}
      </div>
    </div>
  );
}