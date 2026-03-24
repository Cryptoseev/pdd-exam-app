'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import questionBank from '@/data/questions.json';
import { useStatistics } from '@/hooks/useStatistics';
import { useExamSession } from '@/hooks/useExamSession';
import { Header } from '@/components/Header';
import { ProgressBar } from '@/components/ProgressBar';
import { QuestionCard } from '@/components/QuestionCard';
import { Question, ExamAttempt } from '@/types';

export default function MistakesPage() {
  const router = useRouter();
  const { mistakeIds, addAttempt, clearAll } = useStatistics();
  const [practicing, setPracticing] = useState(false);
  const [confirmClear, setConfirmClear] = useState(false);

  const allQuestions: Question[] = questionBank.tickets.flatMap(t => t.questions);
  const mistakeQuestions = allQuestions.filter(q => mistakeIds.includes(q.id));

  const session = useExamSession(mistakeQuestions);
  const correctCount = session.answers.filter(
    (a, i) => a === mistakeQuestions[i]?.correctAnswer
  ).length;

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

  if (practicing && mistakeQuestions.length > 0) {
    return (
      <div className="flex flex-col min-h-screen bg-[var(--bg)]">
        <Header
          title="Работа над ошибками"
          rightElement={
            <div className="flex items-center gap-1.5 bg-brand-blue/10 text-brand-blue rounded-full px-3 py-1 text-sm font-bold">
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
              className="w-full bg-brand-blue text-white rounded-2xl py-4 font-semibold text-sm cursor-pointer"
            >
              Завершить
            </button>
          ) : (
            <button
              onClick={session.goNext}
              disabled={!session.isAnswered}
              className="w-full bg-brand-blue text-white rounded-2xl py-4 font-semibold text-sm disabled:opacity-40 cursor-pointer"
            >
              Далее →
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-[var(--bg)]">
      <Header title="Мои ошибки" />

      {mistakeQuestions.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center px-5 gap-4 text-center">
          <div className="text-5xl">🎉</div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">Нина Леонидовна, ошибок нет!</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 max-w-xs">
            Отличный результат! Пройдите экзамен или тренировку — здесь появятся вопросы, в которых вы ошиблись
          </p>
          <button
            onClick={() => router.push('/')}
            className="mt-4 px-6 py-3.5 bg-brand-blue text-white rounded-2xl font-semibold text-sm cursor-pointer"
          >
            На главную
          </button>
        </div>
      ) : (
        <div className="px-4 py-4 flex flex-col gap-4">
          {/* Summary card */}
          <div className="bg-red-50 dark:bg-red-950/50 rounded-2xl p-4 border border-red-200 dark:border-red-800">
            <div className="text-3xl font-bold text-brand-red">{mistakeQuestions.length}</div>
            <div className="text-sm text-red-700 dark:text-red-300 font-medium mt-0.5">
              вопросов, в которых Нина Леонидовна ошиблась
            </div>
          </div>

          {/* Actions */}
          <button
            onClick={() => setPracticing(true)}
            className="w-full py-4 bg-brand-blue text-white rounded-2xl font-semibold text-sm hover:bg-blue-700 transition-colors cursor-pointer"
          >
            Нина Леонидовна, потренироваться по ошибкам
          </button>

          {confirmClear ? (
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-4 border-2 border-brand-red">
              <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">
                Нина Леонидовна, сбросить всю статистику и список ошибок?
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => { clearAll(); setConfirmClear(false); }}
                  className="flex-1 py-2.5 bg-brand-red text-white rounded-xl font-semibold text-sm cursor-pointer"
                >
                  Сбросить
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
              className="w-full py-3.5 border-2 border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-400 rounded-2xl font-medium text-sm hover:border-red-300 hover:text-brand-red transition-colors cursor-pointer"
            >
              Сбросить статистику
            </button>
          )}

          {/* Question list preview */}
          <div>
            <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
              Вопросы с ошибками
            </h3>
            <div className="flex flex-col gap-2">
              {mistakeQuestions.slice(0, 15).map(q => (
                <div
                  key={q.id}
                  className="bg-white dark:bg-gray-800 rounded-xl p-3 text-sm text-gray-700 dark:text-gray-300 border border-gray-100 dark:border-gray-700"
                >
                  <span className="text-xs text-gray-400 font-mono mr-1.5">#{q.id}</span>
                  {q.question.slice(0, 90)}
                  {q.question.length > 90 ? '…' : ''}
                </div>
              ))}
              {mistakeQuestions.length > 15 && (
                <p className="text-xs text-gray-400 text-center py-1">
                  и ещё {mistakeQuestions.length - 15} вопросов
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
