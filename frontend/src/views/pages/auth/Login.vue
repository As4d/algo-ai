<template>
    <FloatingConfigurator />
    <div class="bg-surface-50 dark:bg-surface-950 flex items-center justify-center min-h-screen min-w-[100vw] overflow-hidden">
        <div class="flex flex-col items-center justify-center">
            <div style="border-radius: 56px; padding: 0.3rem; background: linear-gradient(180deg, var(--primary-color) 10%, rgba(33, 150, 243, 0) 30%)">
                <div class="w-full bg-surface-0 dark:bg-surface-900 py-20 px-8 sm:px-20" style="border-radius: 53px">
                    <div class="text-center mb-8">
                        <div class="text-surface-900 dark:text-surface-0 text-3xl font-medium mb-4">AlgoAI</div>
                        <span class="text-muted-color font-medium">Sign in to continue</span>
                    </div>

                    <div>
                        <label for="email" class="block text-surface-900 dark:text-surface-0 text-xl font-medium mb-2">Email</label>
                        <InputText 
                            id="email" 
                            type="email" 
                            placeholder="Email address" 
                            class="w-full md:w-[30rem] mb-8" 
                            v-model="email"
                            @keyup.enter="login"
                        />

                        <label for="password" class="block text-surface-900 dark:text-surface-0 font-medium text-xl mb-2">Password</label>
                        <Password 
                            id="password" 
                            v-model="password" 
                            placeholder="Password" 
                            :toggleMask="true" 
                            class="mb-4" 
                            fluid 
                            :feedback="false"
                            @keyup.enter="login"
                        />

                        <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                            {{ error }}
                        </div>

                        <div class="flex items-center justify-between mt-2 mb-8 gap-8">
                            <div class="flex items-center">
                                <Checkbox v-model="rememberMe" id="rememberme" binary class="mr-2"></Checkbox>
                                <label for="rememberme">Remember me</label>
                            </div>
                            <span class="font-medium no-underline ml-2 text-right cursor-pointer text-primary">Forgot password?</span>
                        </div>
                        <Button 
                            label="Sign In" 
                            class="w-full" 
                            @click="login"
                            :loading="isLoading"
                        />
                        <div class="text-center mt-4">
                            <span class="text-muted-color">Don't have an account? </span>
                            <router-link to="/auth/register" class="font-medium no-underline text-primary cursor-pointer">Register</router-link>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { useAuthStore } from '@/store/auth';
import { getCSRFToken } from '@/store/auth';
import { useRouter } from 'vue-router';

export default {
    setup() {
        const authStore = useAuthStore();
        const router = useRouter();
        return {
            authStore,
            router
        };
    },
    data() {
        return {
            email: '',
            password: '',
            error: '',
            rememberMe: false,
            isLoading: false
        };
    },
    methods: {
        async login() {
            if (!this.email || !this.password) {
                this.error = 'Please enter both email and password';
                return;
            }

            if (!this.validateEmail(this.email)) {
                this.error = 'Please enter a valid email address';
                return;
            }

            this.error = '';
            this.isLoading = true;

            try {
                const response = await fetch('http://localhost:8000/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({
                        email: this.email,
                        password: this.password
                    }),
                    credentials: 'include'
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    await this.authStore.fetchUser();
                    this.router.push({ name: 'home' });
                } else {
                    this.error = data.message || 'Invalid email or password';
                }
            } catch (error) {
                console.error('Login error:', error);
                this.error = 'An error occurred during login. Please try again.';
            } finally {
                this.isLoading = false;
            }
        },
        validateEmail(email) {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(email);
        },
        resetError() {
            this.error = '';
        }
    }
};
</script>

<style scoped>
.pi-eye {
    transform: scale(1.6);
    margin-right: 1rem;
}

.pi-eye-slash {
    transform: scale(1.6);
    margin-right: 1rem;
}
</style>
