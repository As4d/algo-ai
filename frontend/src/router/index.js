import AppLayout from '@/layout/AppLayout.vue';
import { createRouter, createWebHistory } from 'vue-router';
// import require auth
import { requireAuth, redirectIfAuthenticated } from '@/router/guards';
import CodeLayout from '@/codeLayout/CodeLayout.vue';
import SubmissionHistory from '../components/SubmissionHistory.vue'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            name: 'home',
            component: AppLayout,
            beforeEnter: requireAuth,
            children: [
                {
                    path: '',
                    name: 'dashboard',
                    component: () => import('@/views/Dashboard.vue')
                }
            ]
        },
        {
            path: '/auth/login',
            name: 'login',
            component: () => import('@/views/pages/auth/Login.vue'),
            beforeEnter: redirectIfAuthenticated
        },
        {
            path: '/auth/logout',
            name: 'logout',
            component: () => import('@/views/pages/auth/Logout.vue')
        },
        {
            path: '/auth/register',
            name: 'register',
            component: () => import('@/views/pages/auth/Register.vue')
        },
        {
            path: '/auth/access',
            name: 'accessDenied',
            component: () => import('@/views/pages/auth/Access.vue')
        },
        {
            path: '/auth/error',
            name: 'error',
            component: () => import('@/views/pages/auth/Error.vue')
        },
        {
            path: '/profile',
            component: AppLayout,
            beforeEnter: requireAuth,
            children: [
                {
                    path: '',
                    name: 'profile',
                    component: () => import('@/views/pages/Profile.vue')
                }
            ]
        },
        {
            path: '/problem-sets',
            component: AppLayout,
            beforeEnter: requireAuth,
            children: [
                {
                    path: '',
                    name: 'problemSets',
                    component: () => import('@/views/pages/ProblemSets.vue')
                }
            ]
        },
        {
            path: '/learn-python-basics',
            component: AppLayout,
            beforeEnter: requireAuth,
            children: [
                {
                    path: '',
                    name: 'learnPythonBasics',
                    component: () => import('@/views/pages/LearnPythonBasics.vue')
                }
            ]
        },
        {
            path: '/problems/:id',
            component: CodeLayout,
            beforeEnter: requireAuth,
            children: [

            ]
        },
        {
            path: '/problems/:id/submissions',
            name: 'submission-history',
            component: SubmissionHistory,
            props: true
        },
        {
            path: '/plans',
            component: AppLayout,
            beforeEnter: requireAuth,
            children: [
                { path: '', name: 'plans', component: () => import('@/views/pages/plan/Plans.vue') }
            ]
        },
        {
            path: '/create-plan',
            component: AppLayout,
            beforeEnter: requireAuth,
            children: [
                { path: '', name: 'createPlan', component: () => import('@/views/pages/plan/CreatePlan.vue') }
            ]
        },
        {
            path: '/plan/:id',
            component: AppLayout,
            beforeEnter: requireAuth,
            children: [
                { path: '', name: 'plan', component: () => import('@/views/pages/plan/Plan.vue') }
            ]
        }
    ]
});

export default router;
