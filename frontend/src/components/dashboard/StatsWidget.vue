<template>
    <div class="col-span-12 lg:col-span-6 xl:col-span-6">
        <div class="card mb-0">
            <div class="flex justify-between mb-4">
                <div>
                    <span class="block text-muted-color font-medium mb-4">Streak</span>
                    <div class="text-surface-900 dark:text-surface-0 font-medium text-xl">{{ currentStreak }} days</div>
                </div>
                <div class="flex items-center justify-center bg-green-100 dark:bg-green-400/10 rounded-border" style="width: 2.5rem; height: 2.5rem">
                    <i class="pi pi-bolt text-green-500 !text-xl"></i>
                </div>
            </div>
            <span class="text-primary font-medium">{{ daysToHighScore }} days </span>
            <span class="text-muted-color">to beat high score ({{ highScore }})</span>
        </div>
    </div>
    <div class="col-span-12 lg:col-span-6 xl:col-span-6">
        <div class="card mb-0">
            <div class="flex justify-between mb-4">
                <div>
                    <span class="block text-muted-color font-medium mb-4">Problems Solved</span>
                    <div class="text-surface-900 dark:text-surface-0 font-medium text-xl">{{ totalProblemsSolved }}</div>
                </div>
                <div class="flex items-center justify-center bg-blue-100 dark:bg-blue-400/10 rounded-border" style="width: 2.5rem; height: 2.5rem">
                    <i class="pi pi-check-circle text-blue-500 !text-xl"></i>
                </div>
            </div>
            <span class="text-primary font-medium">+{{ problemsSolvedThisWeek }} </span>
            <span class="text-muted-color"> this week</span>
        </div>
    </div>
</template>

<script setup>
const props = defineProps({
    currentStreak: {
        type: Number,
        default: 0
    },
    highScore: {
        type: Number,
        default: 0
    },
    daysToHighScore: {
        type: Number,
        default: 0
    },
    totalProblemsSolved: {
        type: Number,
        default: 0
    },
    problemsSolvedThisWeek: {
        type: Number,
        default: 0
    }
});
</script>
