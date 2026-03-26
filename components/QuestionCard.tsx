'use client';
import Image from 'next/image';
import { Question } from '@/types';
import { AnswerButton } from './AnswerButton';
import { AnswerState } from '@/hooks/useExamSession';

interface QuestionCardProps {
  question: Question;
  selectedAnswer: number | null;
  answerState: AnswerState;
  showImmediately: boolean;
  onSelectAnswer: (index: number) => void;
}

export function QuestionCard({
  question,
  selectedAnswer,
  answerState,
  showImmediately,
  onSelectAnswer,
}: QuestionCardProps) {
  const getButtonState = (
    optionIndex: number
  ): 'default' | 'selected' | 'correct' | 'wrong' | 'dimmed' => {
    if (selectedAnswer === null) return 'default';

    // Answers revealed
    if (showImmediately && answerState !== 'unanswered') {
      if (optionIndex === question.correctAnswer) return 'correct';
      if (optionIndex === selectedAnswer) return 'wrong';
      return 'dimmed';
    }

    // Answer selected, not yet revealed
    if (optionIndex === selectedAnswer) return 'selected';
    return 'dimmed';
  };

  return (
    <div className="flex flex-col gap-4">
      {/* Question text */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-4 shadow-sm">
        <p className="text-base font-medium text-gray-900 dark:text-white leading-relaxed">
          {question.question}
        </p>
        {question.image && (
          <div className="mt-3 rounded-xl overflow-hidden bg-white dark:bg-gray-900">
            <Image
              src={question.image}
              alt="Иллюстрация к вопросу"
              width={480}
              height={180}
              sizes="(max-width: 640px) 100vw, 480px"
              className="w-full h-auto"
              priority={false}
            />
          </div>
        )}
      </div>

      {/* Answer options */}
      <div className="flex flex-col gap-2">
        {question.options.map((option, idx) => (
          <AnswerButton
            key={idx}
            label={option}
            index={idx}
            state={getButtonState(idx)}
            onClick={() => onSelectAnswer(idx)}
          />
        ))}
      </div>

      {/* Explanation */}
      {showImmediately && selectedAnswer !== null && question.explanation && (
        <div
          className={`p-3.5 rounded-xl text-sm leading-relaxed ${
            answerState === 'correct'
              ? 'bg-green-50 dark:bg-green-950/50 text-green-800 dark:text-green-200 border border-green-200 dark:border-green-800'
              : 'bg-red-50 dark:bg-red-950/50 text-red-800 dark:text-red-200 border border-red-200 dark:border-red-800'
          }`}
        >
          <span className="font-semibold">
            {answerState === 'correct' ? '✓ Правильно. ' : '✗ Неправильно. '}
          </span>
          {question.explanation}
        </div>
      )}
    </div>
  );
}
