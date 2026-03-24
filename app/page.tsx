'use client';
import { useRouter } from 'next/navigation';
import { useStatistics } from '@/hooks/useStatistics';
import { useSettings } from '@/hooks/useSettings';
import { ModeCard } from '@/components/ModeCard';

const MODES = [
  {
    icon: '🎓',
    title: 'Начать экзамен',
    description: '20 случайных вопросов — как на настоящем экзамене ГИБДД',
    colorClass: 'bg-blue-100 dark:bg-blue-900/50',
    href: '/exam',
  },
  {
    icon: '📋',
    title: 'Тренировка по билетам',
    description: 'Выберите билет №1–40 и пройдите его целиком',
    colorClass: 'bg-purple-100 dark:bg-purple-900/50',
    href: '/tickets',
  },
  {
    icon: '🎲',
    title: 'Случайные вопросы',
    description: 'Быстрая тренировка: 10, 20 или 40 вопросов из всей базы',
    colorClass: 'bg-orange-100 dark:bg-orange-900/50',
    href: '/random',
  },
  {
    icon: '❌',
    title: 'Мои ошибки',
    description: 'Вопросы, в которых вы ошибались — потренируйтесь снова',
    colorClass: 'bg-red-100 dark:bg-red-900/50',
    href: '/mistakes',
  },
  {
    icon: '📊',
    title: 'Статистика',
    description: 'История попыток, средний балл и лучший результат',
    colorClass: 'bg-green-100 dark:bg-green-900/50',
    href: '/statistics',
  },
  {
    icon: '⚙️',
    title: 'Настройки',
    description: 'Тёмная тема, показ ответов, звук и другие параметры',
    colorClass: 'bg-gray-100 dark:bg-gray-700/50',
    href: '/settings',
  },
];

export default function HomePage() {
  const router = useRouter();
  const { stats } = useStatistics();
  // Apply dark mode on mount
  useSettings();

  return (
    <main className="flex flex-col pb-8">
      {/* Hero banner */}
      <div className="bg-brand-blue text-white px-5 pt-12 pb-8">
        <div className="flex items-center gap-3 mb-1">
          <span className="text-3xl">🚗</span>
          <h1 className="text-2xl font-bold">Экзамен ПДД</h1>
        </div>
        <p className="text-blue-100 text-sm font-medium">Добро пожаловать, Нина Леонидовна! 👋</p>
        <p className="text-blue-200 text-xs mt-0.5">Подготовка к экзамену ГИБДД России</p>

        {stats.totalAttempts > 0 && (
          <div className="mt-4 bg-white/15 rounded-2xl px-4 py-3 grid grid-cols-3 gap-2">
            <div className="text-center">
              <div className="text-lg font-bold">{stats.totalAttempts}</div>
              <div className="text-blue-200 text-xs">попыток</div>
            </div>
            <div className="text-center border-x border-white/20">
              <div className="text-lg font-bold">{stats.averageScore}%</div>
              <div className="text-blue-200 text-xs">средний балл</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold">{stats.mistakeCount}</div>
              <div className="text-blue-200 text-xs">ошибок</div>
            </div>
          </div>
        )}
        {stats.totalAttempts === 0 && (
          <div className="mt-3 bg-white/10 rounded-2xl px-4 py-2.5">
            <p className="text-blue-100 text-xs leading-relaxed">
              Нина Леонидовна, выберите режим ниже и начните подготовку! 🚦
            </p>
          </div>
        )}
      </div>

      {/* Mode cards */}
      <div className="px-4 pt-5 flex flex-col gap-3">
        {MODES.map(mode => (
          <ModeCard
            key={mode.href}
            icon={mode.icon}
            title={mode.title}
            description={mode.description}
            colorClass={mode.colorClass}
            badge={mode.href === '/mistakes' && stats.mistakeCount > 0 ? String(stats.mistakeCount) : undefined}
            onClick={() => router.push(mode.href)}
          />
        ))}
      </div>
    </main>
  );
}
