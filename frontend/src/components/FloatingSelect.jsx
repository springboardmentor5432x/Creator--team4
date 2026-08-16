import { useState } from 'react';

/**
 * FloatingSelect  premium select dropdown with floating label, leading icon and focus glow
 */
export default function FloatingSelect({
  id,
  label,
  value,
  onChange,
  options = [],
  icon,
  required = true,
}) {
  const [focused, setFocused] = useState(false);
  const isFilled = Boolean(value);
  const isActive = focused || isFilled;

  return (
    <div style={{ position: 'relative', marginBottom: '1.25rem' }}>
      <style>{`
        /* Float label when select is focused or has a selected value */
        .floating-select-field:focus ~ .floating-select-label,
        .floating-select-field:not([data-empty="true"]) ~ .floating-select-label {
          top: -0.55rem !important;
          font-size: 0.65rem !important;
          font-weight: 600 !important;
          color: var(--brand-400) !important;
          background: var(--card-bg) !important;
          padding: 0 0.375rem !important;
          border-radius: 0.25rem !important;
          letter-spacing: 0.02em !important;
          z-index: 3 !important;
        }

        .floating-select-field option {
          background: var(--card-bg, #12141d);
          color: var(--text-primary, #ffffff);
          padding: 0.5rem;
        }
      `}</style>

      {/* Leading Icon */}
      <div
        style={{
          position: 'absolute',
          inset: '0 auto 0 0',
          paddingLeft: '0.75rem',
          display: 'flex',
          alignItems: 'center',
          pointerEvents: 'none',
          color: focused ? 'var(--brand-400)' : 'var(--text-muted)',
          transition: 'color 0.3s',
          zIndex: 2,
        }}
      >
        {icon}
      </div>

      {/* Select Field */}
      <select
        id={id}
        name={id}
        required={required}
        value={value}
        onChange={onChange}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        data-empty={!value}
        className="floating-select-field"
        style={{
          display: 'block',
          width: '100%',
          paddingLeft: '2.5rem',
          paddingRight: '2.5rem',
          paddingTop: '0.875rem',
          paddingBottom: '0.875rem',
          background: 'var(--card-muted-bg)',
          border: `1px solid ${focused ? 'var(--brand-500)' : 'var(--border-color)'}`,
          borderRadius: '0.75rem',
          color: value ? 'var(--text-primary)' : 'var(--text-muted)',
          outline: 'none',
          transition: 'all 0.3s ease',
          fontSize: '0.9rem',
          boxShadow: focused ? '0 0 15px -3px rgba(139,92,246,0.2)' : 'none',
          fontFamily: 'inherit',
          position: 'relative',
          zIndex: 1,
          appearance: 'none',
          WebkitAppearance: 'none',
          MozAppearance: 'none',
          cursor: 'pointer',
        }}
        onMouseEnter={(e) => {
          if (!focused) e.target.style.borderColor = 'var(--border-muted)';
        }}
        onMouseLeave={(e) => {
          if (!focused) e.target.style.borderColor = 'var(--border-color)';
        }}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>

      {/* Trailing Chevron Icon */}
      <div
        style={{
          position: 'absolute',
          inset: '0 0.75rem 0 auto',
          display: 'flex',
          alignItems: 'center',
          pointerEvents: 'none',
          color: focused ? 'var(--brand-400)' : 'var(--text-muted)',
          transition: 'transform 0.2s, color 0.3s',
          transform: focused ? 'rotate(180deg)' : 'rotate(0deg)',
          zIndex: 2,
        }}
      >
        <svg style={{ width: '1.1rem', height: '1.1rem' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </div>

      {/* Floating Label */}
      <label
        htmlFor={id}
        className="floating-select-label"
        style={{
          position: 'absolute',
          left: '2.5rem',
          pointerEvents: 'none',
          transition: 'all 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
          zIndex: 2,
          ...(isActive
            ? {
                top: '-0.55rem',
                fontSize: '0.65rem',
                fontWeight: 600,
                color: 'var(--brand-400)',
                background: 'var(--card-bg)',
                padding: '0 0.375rem',
                borderRadius: '0.25rem',
                letterSpacing: '0.02em',
              }
            : {
                top: '0.875rem',
                fontSize: '0.875rem',
                color: 'var(--text-muted)',
              }),
        }}
      >
        {label}
      </label>
    </div>
  );
}

