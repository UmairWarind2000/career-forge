export default function PageLoader({ text = 'Loading...' }) {
  return (
    <div className="min-h-screen bg-navy-950 bg-grid flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="relative w-12 h-12">
          <div className="absolute inset-0 rounded-full border-2 border-navy-700" />
          <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-cyan-400 animate-spin" />
        </div>
        <p className="text-xs text-gray-500 font-mono tracking-widest uppercase animate-pulse">
          {text}
        </p>
      </div>
    </div>
  );
}