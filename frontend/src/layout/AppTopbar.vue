<template>
    <div class="layout-topbar">
        <div class="layout-topbar-logo-container">
            <button class="layout-menu-button layout-topbar-action" @click="toggleMenu">
                <i class="pi pi-bars"></i>
            </button>
            <router-link to="/" class="layout-topbar-logo">
                <span>AlgoAI</span>
            </router-link>
        </div>

        <div class="layout-topbar-actions">
            <div class="layout-config-menu">
                <button type="button" class="layout-topbar-action" @click="toggleDarkMode">
                    <i :class="['pi', { 'pi-moon': isDarkTheme, 'pi-sun': !isDarkTheme }]"></i>
                </button>
            </div>

            <button
                class="layout-topbar-menu-button layout-topbar-action"
                v-styleclass="{ selector: '@next', enterFromClass: 'hidden', enterActiveClass: 'animate-scalein', leaveToClass: 'hidden', leaveActiveClass: 'animate-fadeout', hideOnOutsideClick: true }"
            >
                <i class="pi pi-ellipsis-v"></i>
            </button>

            <div class="layout-topbar-menu hidden lg:block">
                <div class="layout-topbar-menu-content">
                    <template v-if="isAuthenticated()">
                        <router-link to="/profile" class="layout-topbar-action">
                            <i class="pi pi-user"></i>
                            <span>Profile</span>
                        </router-link>
                    </template>
                    <template v-if="isAuthenticated()">
                        <router-link to="/auth/logout" class="layout-topbar-action">
                            <i class="pi pi-sign-out"></i>
                            <span>Logout</span>
                        </router-link>
                    </template>
                    <template v-if="!isAuthenticated()">
                        <router-link to="/auth/login" class="layout-topbar-action">
                            <i class="pi pi-sign-in"></i>
                            <span>Login</span>
                        </router-link>
                    </template>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { useLayout } from '@/layout/composables/layout';
const { toggleMenu, toggleDarkMode, isDarkTheme } = useLayout();
import { isAuthenticated } from '@/router/guards';
</script>
