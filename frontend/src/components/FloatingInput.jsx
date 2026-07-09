import { useState } from 'react';

/**
 * FloatingInput — premium input with floating label, icon and focus glow
 */
export default function FloatingInput({
  id,
  label,
  type = 'text',
  value,
  onChange,
  icon,
  required = true,
  autoComplete,
}) {
  const [focused, setFocused] = useState(false);
  const isFilled = value && value.length > 0;
  const isActive = focused || isFilled;

  return (
    <div style={{ position: 'relative', marginBottom: '1.25rem' }}>
      <style>{`
        /* Float the label when input is focused, has value (not showing placeholder), or is autofilled */
        .floating-input-field:focus ~ .floating-label,
        .floating-input-field:not(:placeholder-shown) ~ .floating-label,
        .floating-input-field:-webkit-autofill ~ .floating-label {
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

      {/* Input */}
      <input
        id={id}
        name={id}
        type={type}
        required={required}
        value={value}
        autoComplete={autoComplete}
        onChange={onChange}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        placeholder=" " // Set to space to enable CSS not(:placeholder-shown) checking
        className="floating-input-field"
        style={{
          display: 'block',
          width: '100%',
          paddingLeft: '2.5rem',
          paddingRight: '1rem',
          paddingTop: '0.875rem',
          paddingBottom: '0.875rem',
          background: 'var(--card-muted-bg)',
          border: `1px solid ${focused ? 'var(--brand-500)' : 'var(--border-color)'}`,
          borderRadius: '0.75rem',
          color: 'var(--text-primary)',
          outline: 'none',
          transition: 'all 0.3s ease',
          fontSize: '0.9rem',
          boxShadow: focused ? '0 0 15px -3px rgba(139,92,246,0.2)' : 'none',
          fontFamily: 'inherit',
          position: 'relative',
          zIndex: 1,
        }}
        onMouseEnter={(e) => {
          if (!focused) e.target.style.borderColor = 'var(--border-muted)';
        }}
        onMouseLeave={(e) => {
          if (!focused) e.target.style.borderColor = 'var(--border-color)';
        }}
      />

      {/* Floating Label */}
      <label
        htmlFor={id}
        className="floating-label"
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
