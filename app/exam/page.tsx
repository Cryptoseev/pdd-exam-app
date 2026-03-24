'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import questionBank from '@/data/questions.json';
import { useExamSession } from '@/hooks/useExamSession';
import { useSettings } from '@/hooks/useSettings';
import { useStatistics } from '@/hooks/useStatistics';
import { shuffle } from '@/utils/shuffle';
import { Header } from '@/components/Header';
import { ProgressBar } from '@/components/ProgressBar';
import { QuestionCard } from '@/components/QuestionCard';
import { Question, ExamAttempt } from '@/types';

const EXAM_QUESTION_COUNT = 20;

export default function ExamPage() {
  const router = useRouter();
  const { settings } = useSettings();
  const { addAttempt } = useStatistics();
  const [questions] = useState<Question[]>(() => {
    const all: Question[] = questionBank.tickets.flatMap(t => t.questions);
    return shuffle(all).slice(0, EXAM_QUESTION_COUNT);
  });

  const session = useExamSession(questions);
  const correctCount = session.answers.filter(
    (a, i) => a === questions[i]?.correctAnswer
  ).length;

  const handleFinish = () => {
    if (!settings.showAnswerImmediately) {
      session.revealAllAnswers();
    }
    const results = session.getResults();
    const attempt: ExamAttempt = {
      id: Date.now().toString(),
      date: new Date().toISOString(),
      mode: 'exam',
      totalQuestions: results.totalQuestions,
      correctCount: results.correctCount,
      wrongQuestionIds: results.wrongQuestionIds,
      durationSeconds: results.durationSeconds,
    };
    addAttempt(attempt);
    sessionStorage.setItem('lastAttempt', JSON.stringify(attempt));
    router.push('/results');
  };

  if (!session.currentQuestion) {
    return (
      <div className="flex items-center justify-center h-screen text-gray-400">
        Нина Леонидовна, загружаем вопросы…
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-[var(--bg)]">
      <Header
        title="Экзамен"
        rightElement={
          <div className="flex items-center gap-1.5 bg-brand-blue/10 dark:bg-brand-blue/20 text-brand-blue rounded-full px-3 py-1 text-sm font-bold">
            {correctCount}/{session.totalQuestions}
          </div>
        }
      />
      <ProgressBar
        current={session.currentIndex + 1}
        total={session.totalQuestions}
        correctCount={settings.showAnswerImmediately ? correctCount : undefined}
      />

      <div className="flex-1 px-4 py-4 overflow-y-auto">
        <QuestionCard
          question={session.currentQuestion}
          selectedAnswer={session.answers[session.currentIndex]}
          answerState={session.answerStates[session.currentIndex]}
          showImmediately={settings.showAnswerImmediately}
          onSelectAnswer={idx => session.selectAnswer(idx, settings.showAnswerImmediately)}
        />
      </div>

      <div className="px-4 pb-6 pt-3 border-t border-gray-100 dark:border-gray-800 bg-[var(--bg)]">
        {session.isLast ? (
          <button
            onClick={handleFinish}
            className="w-full bg-brand-blue text-white rounded-2xl py-4 font-semibold text-base hover:bg-blue-700 transition-colors active:scale-[0.98] cursor-pointer"
          >
            Завершить экзамен
          </button>
        ) : (
          <button
            onClick={session.goNext}
            disabled={!session.isAnswered && settings.showAnswerImmediately}
            className="w-full bg-brand-blue text-white rounded-2xl py-4 font-semibold text-base hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors active:scale-[0.98] cursor-pointer"
          >
            Следующий вопрос →
          </button>
        )}
        {!settings.showAnswerImmediately && !session.isAnswered && (
          <p className="text-center text-xs text-gray-400 dark:text-gray-500 mt-2">
            Нина Леонидовна, выберите ответ для перехода к следующему вопросу
          </p>
        )}
      </div>
    </div>
  );
}
