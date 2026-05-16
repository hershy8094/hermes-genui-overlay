/**
 * QuizWidget — Interactive quiz component.
 * 
 * Renders a set of multiple-choice questions defined in meta.
 * Answers are stored in state.
 */

import type { GenUIWidgetProps } from "../registry";

export default function QuizWidget({
  state,
  actions,
  meta,
  onStateChange,
  onAction,
}: GenUIWidgetProps): React.JSX.Element {
  const title = (meta?.title as string) ?? "Quiz";
  const questions = (meta?.questions as any[]) ?? [];

  return (
    <div className="genui-quiz">
      <div className="genui-quiz-header">
        <span className="genui-quiz-title">{title}</span>
      </div>
      <div className="genui-quiz-questions">
        {questions.map((q) => (
          <div key={q.id} className="genui-quiz-question">
            <div className="genui-quiz-question-text">{q.text}</div>
            <div className="genui-quiz-options">
              {q.options.map((option: string, index: number) => (
                <label key={index} className="genui-quiz-option">
                  <input
                    type="radio"
                    name={`${title}-${q.id}`}
                    checked={state[q.id] === index}
                    onChange={() => onStateChange(q.id, index)}
                  />
                  <span>{option}</span>
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>
      {actions.length > 0 && (
        <div className="genui-widget-actions">
          {actions.map((action) => (
            <button
              key={action.id}
              className={`genui-action-btn genui-action-${action.style}`}
              data-tracking={action.tracking}
              onClick={() => onAction(action.id, state)}
            >
              {action.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
