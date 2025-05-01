<script setup>
import { ref } from 'vue';

import AppMenuItem from './AppMenuItem.vue';

const model = ref([
    {
        label: 'Home',
        items: [{ label: 'Dashboard', icon: 'pi pi-fw pi-home', to: '/' }]
    },
    {
        label: 'Code',
        items: [
            // add items like "problem sets", "learn code basics", etc.
            { label: 'Problem Sets', icon: 'pi pi-fw pi-pencil', to: '/problem-sets' },
            { label: 'Learn Python Basics', icon: 'pi pi-fw pi-book', to: '/learn-python-basics' },
            { label: 'More Coming Soon', icon: 'pi pi-fw pi-clock' }
        ]
    },
    {
        label: 'Learning Plans',
        items: [
            { label: 'Your Plans', icon: 'pi pi-fw pi-calendar', to: '/plans' },
            { label: 'Create Plan', icon: 'pi pi-fw pi-plus', to: '/create-plan' }
        ]
    },
    {
        label: 'More Features Coming Soon',
        items: [
            { label: 'Community', icon: 'pi pi-fw pi-users' },
            { label: 'Submissions', icon: 'pi pi-fw pi-file'},

            { label: 'More Coming Soon', icon: 'pi pi-fw pi-clock' }
        ]
    }
    
]);
</script>

<template>
    <ul class="layout-menu">
        <template v-for="(item, i) in model" :key="item">
            <app-menu-item v-if="!item.separator" :item="item" :index="i"></app-menu-item>
            <li v-if="item.separator" class="menu-separator"></li>
        </template>
    </ul>
</template>

<style lang="scss" scoped></style>
