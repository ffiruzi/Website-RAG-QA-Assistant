import { useAuth as useAuthContext } from '../contexts/AuthContext';

// Re-export the useAuth hook from the context
export const useAuth = useAuthContext;