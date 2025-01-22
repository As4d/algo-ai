<script>
import { useAuthStore } from '@/store/auth';

export default {
    name: 'Logout',
    created() {
        this.logout();
    },
    methods: {
        logout() {
            const authStore = useAuthStore();
            authStore.logout();
            this.$router.push('/auth/login');
        }
    }
}
</script>
