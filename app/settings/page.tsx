'use client';
import { useSettings } from '@/hooks/useSettings';
import { Header } from '@/components/Header';

interface ToggleProps {
  label: string;
  description: string;
  checked: boolean;
  onChange: (v: boolean) => void;
}

function Toggle({ label, description, checked, onChange }: ToggleProps) {
  return (
    <div className="flex items-center gap-3 bg-white dark:bg-gray-800 rounded-2xl px-4 py-3.5 shadow-sm border border-gray-100 dark:border-gray-700">
      <div className="flex-1 min-w-0">
        <div className="text-sm font-semibold text-gray-900 dark:text-white">{label}</div>
        <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5 leading-relaxed">
          {description}
        </div>
      </div>
      <button
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={`relative flex-shrink-0 w-11 h-6 rounded-full transition-colors duration-200 cursor-pointer ${
          checked ? 'bg-brand-blue' : 'bg-gray-300 dark:bg-gray-600'
        }`}
      >
        <span
          className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow-sm transition-transform duration-200 ${
            checked ? 'translate-x-5' : 'translate-x-0'
          }`}
        />
      </button>
    </div>
  );
}

export default function SettingsPage() {
  const { settings, updateSettings } = useSettings();

  return (
    <div className="flex flex-col min-h-screen bg-[var(--bg)]">
      <Header title="Настройки" />
      <div className="px-4 py-4 flex flex-col gap-3">
        <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide px-1">
          Экзамен
        </div>
        <Toggle
          label="Показывать ответ сразу"
          description="Подсвечивает правильный/неправильный ответ сразу после выбора"
          checked={settings.showAnswerImmediately}
          onChange={v => updateSettings({ showAnswerImmediately: v })}
        />
        <Toggle
          label="Перемешивать вопросы"
          description="Случайный порядок вопросов в режиме экзамена"
          checked={settings.shuffleQuestions}
          onChange={v => updateSettings({ shuffleQuestions: v })}
        />

        <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide px-1 mt-2">
          Интерфейс
        </div>
        <Toggle
          label="Тёмная тема"
          description="Переключиться на тёмный интерфейс для комфортной работы ночью"
          checked={settings.darkMode}
          onChange={v => updateSettings({ darkMode: v })}
        />
        <Toggle
          label="Звуки при ответе"
          description="Звуковой сигнал при правильном и неправильном ответе"
          checked={settings.soundEnabled}
          onChange={v => updateSettings({ soundEnabled: v })}
        />

        <div className="mt-3 bg-blue-50 dark:bg-blue-950/50 rounded-2xl px-4 py-3.5 border border-blue-100 dark:border-blue-900">
          <div className="text-xs font-semibold text-blue-700 dark:text-blue-300 mb-1">
            О приложении
          </div>
          <p className="text-xs text-blue-600 dark:text-blue-400 leading-relaxed">
            Нина Леонидовна, это приложение создано специально для вас! 🚗
            Вопросы соответствуют официальным билетам ГИБДД.
            Все данные хранятся только на вашем устройстве — никакой регистрации не нужно.
          </p>
        </div>

        <div className="bg-gray-50 dark:bg-gray-800/50 rounded-2xl px-4 py-3 border border-gray-100 dark:border-gray-700">
          <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">
            Критерии оценки
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400 space-y-0.5">
            <div>✅ Отлично — 0 ошибок (100%)</div>
            <div>⚠️ Почти сдан — 1–2 ошибки (≥90%)</div>
            <div>❌ Не сдан — 3 и более ошибок (&lt;90%)</div>
          </div>
        </div>
      </div>
    </div>
  );
}
