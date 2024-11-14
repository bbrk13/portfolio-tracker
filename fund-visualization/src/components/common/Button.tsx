interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary';
  children: React.ReactNode;
}

export const Button = ({ variant = 'primary', children, className, ...props }: ButtonProps) => {
  return (
    <button
      className={`
        btn
        ${variant === 'primary' ? 'btn-primary' : 'btn-secondary'}
        ${className}
      `}
      {...props}
    >
      {children}
    </button>
  );
}; 