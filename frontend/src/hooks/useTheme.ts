import { useTheme as useThemeContext } from '../contexts/ThemeContext';

// Re-export the useTheme hook from the context
export const useTheme = useThemeContext;