import { ReactNode, useEffect, useRef, useState } from 'react';

type DeferredSectionProps = {
  children: ReactNode;
  placeholder?: ReactNode;
  rootMargin?: string;
  minHeight?: number;
  className?: string;
};

export default function DeferredSection({
  children,
  placeholder,
  rootMargin = '240px',
  minHeight,
  className,
}: DeferredSectionProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [shouldRender, setShouldRender] = useState(false);

  useEffect(() => {
    if (shouldRender) {
      return;
    }

    const node = containerRef.current;
    if (!node) {
      return;
    }

    if (typeof IntersectionObserver === 'undefined') {
      setShouldRender(true);
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (!entry.isIntersecting) {
          return;
        }

        setShouldRender(true);
        observer.disconnect();
      },
      { rootMargin }
    );

    observer.observe(node);

    return () => observer.disconnect();
  }, [rootMargin, shouldRender]);

  return (
    <div ref={containerRef} className={className}>
      {shouldRender
        ? children
        : placeholder ?? <div aria-hidden="true" style={minHeight ? { minHeight } : undefined} />}
    </div>
  );
}