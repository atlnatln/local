import { useMediaQuery } from '../hooks/useMediaQuery';

export const useIsMobile = (): boolean => useMediaQuery('(max-width: 768px)');
