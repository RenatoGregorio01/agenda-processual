import Link from "next/link";
import type { ButtonHTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/cn";

export type ButtonVariant = "primary" | "secondary" | "ghost" | "danger" | "link";
export type ButtonSize = "sm" | "md" | "lg";

const variantClass: Record<ButtonVariant, string> = {
  primary:
    "bg-primary text-primary-foreground hover:brightness-110 disabled:opacity-60",
  secondary:
    "border border-border bg-surface text-foreground hover:bg-background disabled:opacity-60",
  ghost: "text-muted hover:bg-background hover:text-foreground disabled:opacity-60",
  danger: "bg-atrasado text-white hover:brightness-110 disabled:opacity-60",
  link: "text-primary underline-offset-4 hover:underline disabled:opacity-60",
};

const sizeClass: Record<ButtonSize, string> = {
  sm: "h-9 px-3 text-sm",
  md: "h-11 px-4 text-sm",
  lg: "h-12 px-5 text-base",
};

function buttonClass(
  variant: ButtonVariant,
  size: ButtonSize,
  fullWidth?: boolean,
  className?: string,
) {
  const base =
    variant === "link"
      ? "inline-flex items-center justify-center font-medium transition"
      : "inline-flex items-center justify-center rounded-md font-semibold transition";
  return cn(base, variantClass[variant], variant === "link" ? "" : sizeClass[size], fullWidth && "w-full", className);
}

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  size?: ButtonSize;
  fullWidth?: boolean;
};

export function Button({
  variant = "primary",
  size = "md",
  fullWidth,
  className,
  type = "button",
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      className={buttonClass(variant, size, fullWidth, className)}
      {...props}
    />
  );
}

type ButtonLinkProps = {
  href: string;
  children: ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
  fullWidth?: boolean;
  className?: string;
};

export function ButtonLink({
  href,
  children,
  variant = "primary",
  size = "md",
  fullWidth,
  className,
}: ButtonLinkProps) {
  return (
    <Link href={href} className={buttonClass(variant, size, fullWidth, className)}>
      {children}
    </Link>
  );
}
