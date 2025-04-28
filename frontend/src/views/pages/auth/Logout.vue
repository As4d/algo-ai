<script>
import { useAuthStore } from '@/store/auth';

export default {
    name: 'Logout',
    async created() {
        try {
            const authStore = useAuthStore();
            await authStore.logout(this.$router);
        } catch (error) {
            console.error('Logout failed:', error);
            this.$router.push('/auth/login');
        }
    }
}
</script>
