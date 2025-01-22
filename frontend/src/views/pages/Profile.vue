<template>
    <div class="layout-wrapper">
        <div class="layout-content">
            <div class="profile-container">
                <div class="profile-header bg-primary text-white py-4 px-8 rounded-lg shadow-md">
                    <h1 class="text-2xl font-bold">{{ user.username }}</h1>
                    <p class="text-sm">{{ user.email }}</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { useAuthStore } from '@/store/auth';
import { defineAsyncComponent } from 'vue';

export default {
    data() {
        return {
            user: {
                username: '',
                email: ''
            }
        };
    },
    async mounted() {
        const authStore = useAuthStore();
        await authStore.fetchUser();
        if (authStore.user) {
            this.user = authStore.user;
        }
    }
};
</script>

<style scoped>
.profile-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 1rem;
}

.profile-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.profile-details {
    margin-top: 2rem;
    height: 400px; /* Adjust height as needed */
}
</style>
