'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ExamAttempt, DEFAULT_SCORING } from '@/types';
import { getExamStatus, STATUS_MESSAGES } from '@/utils/scoring';

export default function ResultsPage() {
  const router = useRouter();
  const [attempt, setAttempt] = useState<ExamAttempt | null>(null);

  useEffect(() => {
    const raw = sessionStorage.getItem('lastAttempt');
    if (raw) setAttempt(JSON.parse(raw));
  }, []);

  if (!attempt) {
    return (
      <div className="flex items-center justify-center h-screen text-gray-400">
        Нина Леонидовна, данные о результате не найдены
      </div>
    );
  }

  const percent = Math.round((attempt.correctCount / attempt.totalQuestions) * 100);
  const status = getExamStatus(attempt.correctCount, attempt.totalQuestions, DEFAULT_SCORING);
  const msg = STATUS_MESSAGES[status];
  const wrongCount = attempt.totalQuestions - attempt.correctCount;
  const minutes = Math.floor(attempt.durationSeconds / 60);
  const seconds = attempt.durationSeconds % 60;

  const circumference = 2 * Math.PI * 48;
  const dashOffset = circumference - (percent / 100) * circumference;
  const circleColor =
    status === 'excellent' ? '#0E9F6E' : status === 'passed' ? '#F59E0B' : '#E02424';

  const modeLabel =
    attempt.mode === 'exam'
      ? 'Экзамен'
      : attempt.mode === 'ticket'
      ? `Билет №${attempt.ticketNumber}`
      : 'Тренировка';

  return (
    <div className="flex flex-col min-h-screen bg-[var(--bg)]">
      <div className="flex-1 flex flex-col items-center justify-center px-5 py-8 gap-6">
        {/* Mode badge */}
        <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 px-3 py-1 rounded-full">
          {modeLabel}
        </span>

        {/* Score circle */}
        <div className="relative w-36 h-36">
          <svg className="w-full h-full -rotate-90" viewBox="0 0 110 110">
            <circle
              cx="55" cy="55" r="48"
              fill="none"
              stroke="#E5E7EB"
              className="dark:stroke-gray-700"
              strokeWidth="7"
            />
            <circle
              cx="55" cy="55" r="48"
              fill="none"
              stroke={circleColor}
              strokeWidth="7"
              strokeDasharray={circumference}
              strokeDashoffset={dashOffset}
              strokeLinecap="round"
              style={{ transition: 'stroke-dashoffset 0.8s ease-out' }}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-3xl font-bold text-gray-900 dark:text-white">{percent}%</span>
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {attempt.correctCount}/{attempt.totalQuestions}
            </span>
          </div>
        </div>

        {/* Status message */}
        <div className="text-center">
          <h2 className={`text-xl font-bold ${msg.colorClass}`}>{msg.title}</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-2 max-w-xs leading-relaxed">
            {msg.subtitle}
          </p>
        </div>

        {/* Stats row */}
        <div className="flex gap-3 w-full max-w-sm">
          <div className="flex-1 bg-white dark:bg-gray-800 rounded-2xl p-3.5 text-center shadow-sm border border-gray-100 dark:border-gray-700">
            <div className="text-xl font-bold text-brand-green">{attempt.correctCount}</div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Верных</div>
          </div>
          <div className="flex-1 bg-white dark:bg-gray-800 rounded-2xl p-3.5 text-center shadow-sm border border-gray-100 dark:border-gray-700">
            <div className="text-xl font-bold text-brand-red">{wrongCount}</div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Ошибок</div>
          </div>
          <div className="flex-1 bg-white dark:bg-gray-800 rounded-2xl p-3.5 text-center shadow-sm border border-gray-100 dark:border-gray-700">
            <div className="text-xl font-bold text-gray-700 dark:text-gray-200">
              {minutes}:{String(seconds).padStart(2, '0')}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Время</div>
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex flex-col gap-3 w-full max-w-sm">
          {wrongCount > 0 && (
            <button
              onClick={() => router.push('/mistakes')}
              className="w-full py-4 rounded-2xl border-2 border-brand-red text-brand-red font-semibold text-sm hover:bg-red-50 dark:hover:bg-red-950 transition-colors cursor-pointer"
            >
              Нина Леонидовна, посмотреть ошибки ({wrongCount})
            </button>
          )}
          <button
            onClick={() => router.back()}
            className="w-full py-4 rounded-2xl bg-brand-blue text-white font-semibold text-sm hover:bg-blue-700 transition-colors cursor-pointer"
          >
            Пройти заново
          </button>
          <button
            onClick={() => router.push('/')}
            className="w-full py-4 rounded-2xl border-2 border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 font-semibold text-sm hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors cursor-pointer"
          >
            На главную, Нина Леонидовна
          </button>
        </div>
      </div>
    </div>
  );
}
