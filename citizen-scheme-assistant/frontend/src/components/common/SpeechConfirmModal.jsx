import React, { useEffect, useRef } from 'react';
import { useLanguage } from '../../i18n/LanguageContext';

/**
 * Simple accessible modal that asks the user to confirm the spoken text.
 * Props:
 *   - text: the transcript string
 *   - onConfirm: called when user clicks “Yes, correct”
 *   - onCancel: called when user clicks “Try again”
 */
export const SpeechConfirmModal = ({ text, onConfirm, onCancel }) => {
  const { t } = useLanguage();
  const dialogRef = useRef(null);

  // Focus the dialog when it appears
  useEffect(() => {
    if (dialogRef.current) {
      dialogRef.current.focus();
    }
  }, []);

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      onCancel();
    }
  };

  return (
    <div
      className="fixed inset-0 flex items-center justify-center bg-black/40 z-50"
      role="dialog"
      aria-modal="true"
      aria-labelledby="speech-confirm-title"
      onKeyDown={handleKeyDown}
    >
      <div
        ref={dialogRef}
        tabIndex="-1"
        className="bg-white rounded-lg shadow-lg max-w-sm w-full p-4 outline-none"
      >
        <h2 id="speech-confirm-title" className="text-lg font-medium mb-3">
          {t('weHeard', `We heard: {{text}}`).replace('{{text}}', text)}
        </h2>
        <div className="flex justify-end gap-3">
          <button
            type="button"
            onClick={onCancel}
            className="px-3 py-1.5 rounded bg-gray-200 hover:bg-gray-300 text-sm"
          >
            {t('tryAgain', 'Try again')}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className="px-3 py-1.5 rounded bg-orange-500 hover:bg-orange-600 text-white text-sm"
          >
            {t('yesCorrect', 'Yes, correct')}
          </button>
        </div>
      </div>
    </div>
  );
};

