<template>
    <FloatingConfigurator />
    <div class="bg-surface-50 dark:bg-surface-950 flex items-center justify-center min-h-screen min-w-[100vw] overflow-hidden">
        <div class="flex flex-col items-center justify-center">
            <div style="border-radius: 56px; padding: 0.3rem; background: linear-gradient(180deg, var(--primary-color) 10%, rgba(33, 150, 243, 0) 30%)">
                <div class="w-full bg-surface-0 dark:bg-surface-900 py-20 px-8 sm:px-20" style="border-radius: 53px">
                    <div class="text-center mb-8">
                        <div class="text-surface-900 dark:text-surface-0 text-3xl font-medium mb-4">AlgoAI</div>
                        <span class="text-muted-color font-medium">Create your account</span>
                    </div>

                    <div>
                        <label for="email" class="block text-surface-900 dark:text-surface-0 text-xl font-medium mb-2">Email</label>
                        <InputText id="email" type="text" placeholder="Email address" class="w-full md:w-[30rem] mb-8" v-model="email" />

                        <label for="password" class="block text-surface-900 dark:text-surface-0 font-medium text-xl mb-2">Password</label>
                        <Password id="password" v-model="password" placeholder="Password" :toggleMask="true" class="mb-4" fluid :feedback="false"></Password>

                        <div v-if="error" class="text-red-500 text-sm mb-4">{{ error }}</div>
                        <div v-if="success" class="text-green-500 text-sm mb-4">{{ success }}</div>

                        <Button label="Sign Up" class="w-full" @click="register"></Button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { getCSRFToken } from '@/store/auth';

export default {
    data() {
        return {
            email: '',
            password: '',
            error: '',
            success: ''
        };
    },
    methods: {
        async register() {
            try {
                const response = await fetch('http://localhost:8000/api/register', {
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
                if (response.ok) {
                    this.success = 'Registration successful! Please log in.';
                    setTimeout(() => {
                        this.$router.push('auth/login');
                    }, 1000);
                } else {
                    this.error = data.error || 'Registration failed';
                }
            } catch (err) {
                this.error = 'An error occurred during registration: ' + err;
            }
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
