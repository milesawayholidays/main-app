import * as React from 'react';

export type TextFieldProps = {
  label: React.ReactNode;
  value: string | number;
  onChange: (value: string) => void;
  name?: string;
  placeholder?: string;
  type?: React.HTMLInputTypeAttribute;
  min?: number;
  max?: number;
  step?: number;
  inputStyle?: React.CSSProperties;
  containerStyle?: React.CSSProperties;
};

export function TextField({
  label,
  value,
  onChange,
  name,
  placeholder,
  type = 'text',
  min,
  max,
  step,
  inputStyle,
  containerStyle
}: TextFieldProps) {
  const id = React.useId();

  return (
    <label
      htmlFor={id}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 6,
        ...containerStyle
      }}
    >
      {label}
      <input
        id={id}
        name={name}
        type={type}
        value={value}
        min={min}
        max={max}
        step={step}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        style={{
          font: 'inherit',
          ...inputStyle
        }}
      />
    </label>
  );
}
