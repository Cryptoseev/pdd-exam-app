import { ExamStatus, ScoringConfig } from '@/types';

export function getExamStatus(
  correct: number,
  total: number,
  config: ScoringConfig
): ExamStatus {
  const ratio = correct / total;
  if (ratio >= config.excellentThreshold) return 'excellent';
  if (ratio >= config.passThreshold) return 'passed';
  return 'failed';
}

export const STATUS_MESSAGES: Record<
  ExamStatus,
  { title: string; subtitle: string; colorClass: string; bgClass: string }
> = {
  excellent: {
    title: 'Нина Леонидовна, вы сдали на отлично! 🎉',
    subtitle: 'Великолепный результат! Вы ответили на все вопросы правильно. Так держать, Нина Леонидовна — настоящий экзамен вам по плечу!',
    colorClass: 'text-brand-green',
    bgClass: 'bg-green-50',
  },
  passed: {
    title: 'Нина Леонидовна, почти сдано! 👍',
    subtitle: 'Очень хороший результат! Есть небольшие ошибки — загляните в раздел «Мои ошибки» и повторите их.',
    colorClass: 'text-amber-500',
    bgClass: 'bg-amber-50',
  },
  failed: {
    title: 'Нина Леонидовна, в этот раз не получилось 💪',
    subtitle: 'Не расстраивайтесь! Пройдите тренировку ещё раз — у вас обязательно получится.',
    colorClass: 'text-brand-red',
    bgClass: 'bg-red-50',
  },
};
