import React from 'react';

/**
 * FormattedMessage component:
 * Safely renders markdown-like formatting (bold, links, lists, paragraphs)
 * without dangerouslySetInnerHTML.
 */
export const FormattedMessage = ({ text, className = '', isDark = false }) => {
  if (!text) return null;

  // Split into lines/paragraphs
  const lines = text.split('\n');

  // Helper to parse inline bold (**text**) and links ([text](url))
  const renderInline = (line, lineKey) => {
    // Regex matching either **bold** or [link text](url)
    const tokenRegex = /(\*\*[^*]+\*\*|\[[^\]]+\]\([^)]+\)|https?:\/\/[^\s)]+)/g;
    const parts = line.split(tokenRegex);

    return parts.map((part, idx) => {
      if (!part) return null;
      const key = `${lineKey}-${idx}`;

      // Bold **text**
      if (part.startsWith('**') && part.endsWith('**') && part.length >= 4) {
        return (
          <strong key={key} className={isDark ? 'font-bold text-white' : 'font-bold text-slate-900'}>
            {part.slice(2, -2)}
          </strong>
        );
      }

      // Link [text](url)
      const linkMatch = part.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
      if (linkMatch) {
        const linkText = linkMatch[1];
        const linkUrl = linkMatch[2];
        return (
          <a
            key={key}
            href={linkUrl}
            target="_blank"
            rel="noopener noreferrer"
            className={`${isDark ? 'text-orange-400 hover:text-orange-300' : 'text-orange-600 hover:text-orange-700'} underline font-semibold`}
          >
            {linkText}
          </a>
        );
      }

      // Bare URL
      if (part.startsWith('http://') || part.startsWith('https://')) {
        return (
          <a
            key={key}
            href={part}
            target="_blank"
            rel="noopener noreferrer"
            className={`${isDark ? 'text-orange-400 hover:text-orange-300' : 'text-orange-600 hover:text-orange-700'} underline break-all font-medium`}
          >
            {part}
          </a>
        );
      }

      return <span key={key}>{part}</span>;
    });
  };

  return (
    <div className={`space-y-1.5 leading-relaxed ${className}`}>
      {lines.map((line, lineIdx) => {
        const trimmed = line.trim();

        // Empty line -> vertical space
        if (!trimmed) {
          return <div key={lineIdx} className="h-1" />;
        }

        // Bullet line (- item or * item)
        if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
          return (
            <div key={lineIdx} className="flex items-start gap-1.5 ml-1">
              <span className={`text-[10px] mt-0.5 ${isDark ? 'text-orange-400' : 'text-orange-500'}`}>•</span>
              <span className="flex-1">{renderInline(trimmed.slice(2), lineIdx)}</span>
            </div>
          );
        }

        // Numbered list (e.g. 1. item)
        const numberedMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);
        if (numberedMatch) {
          const num = numberedMatch[1];
          const content = numberedMatch[2];
          return (
            <div key={lineIdx} className="flex items-start gap-1.5 ml-1">
              <span className={`text-[11px] font-bold ${isDark ? 'text-orange-400' : 'text-orange-600'}`}>
                {num}.
              </span>
              <span className="flex-1">{renderInline(content, lineIdx)}</span>
            </div>
          );
        }

        // Normal paragraph line
        return <p key={lineIdx}>{renderInline(line, lineIdx)}</p>;
      })}
    </div>
  );
};
