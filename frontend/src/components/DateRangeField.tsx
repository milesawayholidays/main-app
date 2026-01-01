import * as React from 'react';
import { DayPicker, type DateRange } from 'react-day-picker';

export type CompleteDateRange = { from: Date; to: Date };

export type DateRangeFieldProps = {
  label: React.ReactNode;
  value: CompleteDateRange | null;
  onChange: (next: CompleteDateRange | null) => void;
  disabled?: boolean;
};

function startOfDay(date: Date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

function isSameDay(a: Date, b: Date) {
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  );
}

function formatShort(date: Date) {
  // Human readable only (API formatting is handled elsewhere)
  return date.toISOString().slice(0, 10);
}

function toRdpRange(value: CompleteDateRange | null): DateRange | undefined {
  if (!value) return undefined;
  return { from: value.from, to: value.to };
}

export function DateRangeField({ label, value, onChange, disabled }: DateRangeFieldProps) {
  const [open, setOpen] = React.useState(false);
  const rootRef = React.useRef<HTMLDivElement | null>(null);

  const selected = toRdpRange(value);

  React.useEffect(() => {
    if (!open) return;

    function onKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') setOpen(false);
    }

    function onMouseDown(e: MouseEvent) {
      const root = rootRef.current;
      if (!root) return;
      if (e.target instanceof Node && !root.contains(e.target)) {
        setOpen(false);
      }
    }

    window.addEventListener('keydown', onKeyDown);
    window.addEventListener('mousedown', onMouseDown);
    return () => {
      window.removeEventListener('keydown', onKeyDown);
      window.removeEventListener('mousedown', onMouseDown);
    };
  }, [open]);

  function handleDayClick(day: Date) {
    if (disabled) return;
    const clicked = startOfDay(day);

    if (!value) {
      onChange({ from: clicked, to: clicked });
      return;
    }

    const from = startOfDay(value.from);
    const to = startOfDay(value.to);

    // If user clicks inside an existing same-day range, keep it stable.
    if (isSameDay(from, to) && isSameDay(from, clicked)) {
      onChange({ from: clicked, to: clicked });
      return;
    }

    // Clicking before the start resets to a new single-day range.
    if (clicked < from) {
      onChange({ from: clicked, to: clicked });
      return;
    }

    // Otherwise keep the original start and move the end.
    onChange({ from, to: clicked });
  }

  return (
    <div ref={rootRef} style={{ position: 'relative', display: 'inline-flex', flexDirection: 'column', gap: 8 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
        <div style={{ fontWeight: 600 }}>{label}</div>
        <button type="button" onClick={() => setOpen((v) => !v)} disabled={disabled}>
          {value ? `${formatShort(value.from)} → ${formatShort(value.to)}` : 'Select dates'}
        </button>
        <button
          type="button"
          onClick={() => {
            onChange(null);
            setOpen(false);
          }}
          disabled={disabled || !value}
        >
          Clear
        </button>
      </div>

      {open ? (
        <div
          role="dialog"
          aria-label="Date range"
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            zIndex: 10,
            marginTop: 8,
            padding: 12,
            border: '1px solid #ddd',
            background: 'white',
            // Ensure 2-month layout stays horizontal instead of wrapping vertically.
            minWidth: 640
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 8 }}>
            <button type="button" onClick={() => setOpen(false)}>
              Close
            </button>
          </div>
          <div style={{ opacity: disabled ? 0.6 : 1, pointerEvents: disabled ? 'none' : 'auto' }}>
            <DayPicker
              mode="range"
              selected={selected}
              onDayClick={handleDayClick}
              weekStartsOn={1}
              numberOfMonths={2}
              styles={{
                months: { display: 'flex', flexWrap: 'nowrap', gap: 16 }
              }}
            />
          </div>
        </div>
      ) : null}
    </div>
  );
}
