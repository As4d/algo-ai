import { useAuthStore } from '@/store/auth';

export function requireAuth(to, from, next) {
    const authStore = useAuthStore();

    if (authStore.isAuthenticated) {
        next(); // User is authenticated, allow access
    } else {
        next({ name: 'login' }); // Redirect to login page
    }
}


export function isAuthenticated() {
    const authStore = useAuthStore();
    return authStore.isAuthenticated;
}