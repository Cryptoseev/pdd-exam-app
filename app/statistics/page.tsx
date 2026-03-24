'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useStatistics } from '@/hooks/useStatistics';
import { Header } from '@/components/Header';
import { StatCard } from '@/components/StatCard';

export default function StatisticsPage() {
  const router = useRouter();
  const { stats, attempts, clearAll } = useStatistics();
  const [confirmClear, setConfirmClear] = useState(false);

  return (
    <div className="flex flex-col min-h-screen bg-[var(--bg)]">
      <Header title="Статистика" />
      <div className="px-4 py-4 flex flex-col gap-4">
        {/* Stats grid */}
        <div className="grid grid-cols-2 gap-3">
          <StatCard label="Попыток" value={stats.totalAttempts} colorClass="text-brand-blue" />
          <StatCard
            label="Средний балл"
            value={stats.totalAttempts ? `${stats.averageScore}%` : '—'}
            colorClass="text-brand-green"
          />
          <StatCard
            label="Лучший результат"
            value={stats.totalAttempts ? `${stats.bestScore}%` : '—'}
            colorClass="text-purple-500"
          />
          <StatCard
            label="Ошибок в базе"
            value={stats.mistakeCount}
            colorClass="text-brand-red"
          />
        </div>

        {stats.totalQuestions > 0 && (
          <StatCard
            label="Всего вопросов отвечено"
            value={stats.totalQuestions}
            sub={`${stats.totalCorrect} правильных · ${stats.totalQuestions - stats.totalCorrect} ошибок`}
            colorClass="text-gray-700 dark:text-gray-200"
          />
        )}

        {/* Recent attempts */}
        {attempts.length > 0 && (
          <div>
            <h2 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
              Последние попытки
            </h2>
            <div className="flex flex-col gap-2">
              {stats.recentAttempts.map(a => {
                const pct = Math.round((a.correctCount / a.totalQuestions) * 100);
                const date = new Date(a.date).toLocaleDateString('ru-RU', {
                  day: 'numeric',
                  month: 'short',
                  hour: '2-digit',
                  minute: '2-digit',
                });
                const modeLabel =
                  a.mode === 'exam'
                    ? 'Экзамен'
                    : a.mode === 'ticket'
                    ? `Билет №${a.ticketNumber}`
                    : 'Тренировка';
                const colorClass =
                  pct >= 90
                    ? 'text-brand-green'
                    : pct >= 70
                    ? 'text-amber-500'
                    : 'text-brand-red';
                return (
                  <div
                    key={a.id}
                    className="bg-white dark:bg-gray-800 rounded-xl px-4 py-3 flex items-center gap-3 shadow-sm border border-gray-100 dark:border-gray-700"
                  >
                    <div className={`text-lg font-bold w-12 flex-shrink-0 ${colorClass}`}>
                      {pct}%
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-800 dark:text-gray-200">
                        {modeLabel}
                      </div>
                      <div className="text-xs text-gray-400 mt-0.5">{date}</div>
                    </div>
                    <div className="text-xs text-gray-400 flex-shrink-0">
                      {a.correctCount}/{a.totalQuestions}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {attempts.length === 0 && (
          <div className="text-center py-12">
            <div className="text-4xl mb-3">📊</div>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Нина Леонидовна, статистика появится после первого экзамена
            </p>
            <button
              onClick={() => router.push('/exam')}
              className="mt-4 px-6 py-3 bg-brand-blue text-white rounded-2xl font-semibold text-sm cursor-pointer"
            >
              Начать первый экзамен
            </button>
          </div>
        )}

        {/* Clear stats */}
        {attempts.length > 0 && (
          confirmClear ? (
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-4 border-2 border-brand-red">
              <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">
                Нина Леонидовна, удалить всю статистику и историю попыток?
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => { clearAll(); setConfirmClear(false); }}
                  className="flex-1 py-2.5 bg-brand-red text-white rounded-xl font-semibold text-sm cursor-pointer"
                >
                  Удалить
                </button>
                <button
                  onClick={() => setConfirmClear(false)}
                  className="flex-1 py-2.5 border-2 border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 rounded-xl font-semibold text-sm cursor-pointer"
                >
                  Отмена
                </button>
              </div>
            </div>
          ) : (
            <button
              onClick={() => setConfirmClear(true)}
              className="w-full py-3.5 border-2 border-gray-200 dark:border-gray-700 rounded-2xl text-sm font-semibold text-gray-500 dark:text-gray-400 hover:border-red-300 hover:text-brand-red transition-colors cursor-pointer"
            >
              Сбросить всю статистику
            </button>
          )
        )}
      </div>
    </div>
  );
}
