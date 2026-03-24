'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import questionBank from '@/data/questions.json';
import { useExamSession } from '@/hooks/useExamSession';
import { useStatistics } from '@/hooks/useStatistics';
import { shuffle } from '@/utils/shuffle';
import { Header } from '@/components/Header';
import { ProgressBar } from '@/components/ProgressBar';
import { QuestionCard } from '@/components/QuestionCard';
import { Question, ExamAttempt } from '@/types';

const COUNT_OPTIONS = [
  { count: 10, label: '10 вопросов', sub: 'Быстрая тренировка (~5 мин)' },
  { count: 20, label: '20 вопросов', sub: 'Как на экзамене (~10 мин)' },
  { count: 40, label: '40 вопросов', sub: 'Полная тренировка (~20 мин)' },
];

export default function RandomPage() {
  const router = useRouter();
  const { addAttempt } = useStatistics();
  const [questions, setQuestions] = useState<Question[]>([]);
  const session = useExamSession(questions);

  const correctCount = session.answers.filter(
    (a, i) => a === questions[i]?.correctAnswer
  ).length;

  const startSession = (n: number) => {
    const all: Question[] = questionBank.tickets.flatMap(t => t.questions);
    setQuestions(shuffle(all).slice(0, n));
  };

  if (questions.length === 0) {
    return (
      <div className="flex flex-col min-h-screen bg-[var(--bg)]">
        <Header title="Случайные вопросы" />
        <div className="flex-1 flex flex-col items-center justify-center px-5 gap-8">
          <div className="text-center">
            <div className="text-5xl mb-3">🎲</div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">Нина Леонидовна, сколько вопросов?</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Вопросы выбираются случайно из всех 40 билетов
            </p>
          </div>
          <div className="flex flex-col gap-3 w-full max-w-sm">
            {COUNT_OPTIONS.map(({ count, label, sub }) => (
              <button
                key={count}
                onClick={() => startSession(count)}
                className="w-full py-4 px-5 rounded-2xl bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 hover:border-brand-blue hover:bg-blue-50 dark:hover:bg-blue-950 transition-all text-left active:scale-[0.98] cursor-pointer"
              >
                <div className="font-bold text-gray-900 dark:text-white">{label}</div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{sub}</div>
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const handleFinish = () => {
    const results = session.getResults();
    const attempt: ExamAttempt = {
      id: Date.now().toString(),
      date: new Date().toISOString(),
      mode: 'random',
      totalQuestions: results.totalQuestions,
      correctCount: results.correctCount,
      wrongQuestionIds: results.wrongQuestionIds,
      durationSeconds: results.durationSeconds,
    };
    addAttempt(attempt);
    sessionStorage.setItem('lastAttempt', JSON.stringify(attempt));
    router.push('/results');
  };

  return (
    <div className="flex flex-col min-h-screen bg-[var(--bg)]">
      <Header
        title="Случайные вопросы"
        rightElement={
          <div className="flex items-center gap-1.5 bg-brand-blue/10 dark:bg-brand-blue/20 text-brand-blue rounded-full px-3 py-1 text-sm font-bold">
            {correctCount}/{session.totalQuestions}
          </div>
        }
      />
      <ProgressBar
        current={session.currentIndex + 1}
        total={session.totalQuestions}
        correctCount={correctCount}
      />

      <div className="flex-1 px-4 py-4 overflow-y-auto">
        <QuestionCard
          question={session.currentQuestion}
          selectedAnswer={session.answers[session.currentIndex]}
          answerState={session.answerStates[session.currentIndex]}
          showImmediately={true}
          onSelectAnswer={idx => session.selectAnswer(idx, true)}
        />
      </div>

      <div className="px-4 pb-6 pt-3 border-t border-gray-100 dark:border-gray-800 bg-[var(--bg)]">
        {session.isLast ? (
          <button
            onClick={handleFinish}
            className="w-full bg-brand-blue text-white rounded-2xl py-4 font-semibold text-base hover:bg-blue-700 transition-colors cursor-pointer"
          >
            Завершить тренировку
          </button>
        ) : (
          <button
            onClick={session.goNext}
            disabled={!session.isAnswered}
            className="w-full bg-brand-blue text-white rounded-2xl py-4 font-semibold text-base disabled:opacity-40 disabled:cursor-not-allowed hover:bg-blue-700 transition-colors cursor-pointer"
          >
            Следующий →
          </button>
        )}
      </div>
    </div>
  );
}
