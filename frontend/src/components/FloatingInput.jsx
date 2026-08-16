import { useState } from 'react';

/**
 * FloatingInput  premium input with floating label, icon and focus glow
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
  const [showPassword, setShowPassword] = useState(false);
  const isFilled = value && value.length > 0;
  const isActive = focused || isFilled;

  const actualType = type === 'password' ? (showPassword ? 'text' : 'password') : type;

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
        type={actualType}
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
          paddingRight: type === 'password' ? '2.5rem' : '1rem',
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

      {/* Trailing Password Toggle Button */}
      {type === 'password' && (
        <button
          type="button"
          onClick={() => setShowPassword(prev => !prev)}
          tabIndex={-1}
          aria-label={showPassword ? "Hide password" : "Show password"}
          title={showPassword ? "Hide password" : "Show password"}
          style={{
            position: 'absolute',
            right: '0.75rem',
            top: '50%',
            transform: 'translateY(-50%)',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            color: showPassword ? 'var(--brand-400)' : 'var(--text-muted)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '0.25rem',
            borderRadius: '0.375rem',
            zIndex: 3,
            transition: 'color 0.2s',
          }}
        >
          {showPassword ? (
            <svg style={{ width: '1.1rem', height: '1.1rem' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858-5.908a8.97 8.97 0 013.682-.763c4.478 0 8.268 2.943 9.542 7a10.025 10.025 0 01-4.132 5.411m-4.092-4.092a3 3 0 11-4.243-4.243M3 3l18 18" />
            </svg>
          ) : (
            <svg style={{ width: '1.1rem', height: '1.1rem' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          )}
        </button>
      )}

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

