<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
    leaderboard: {
        type: Array,
        default: () => []
    }
});

const formatScore = (score) => {
    return score.toLocaleString();
};
</script>

<template>
    <div class="card">
        <div class="flex items-center justify-between mb-6">
            <div class="font-semibold text-xl">Leaderboard</div>
        </div>

        <div v-if="leaderboard.length === 0" class="text-center py-4 text-muted-color">
            No leaderboard data available
        </div>

        <div v-else class="space-y-4">
            <div v-for="(user, index) in leaderboard" :key="user.id" 
                 class="flex items-center justify-between p-3 rounded-lg"
                 :class="index === 0 ? 'bg-primary/10' : 'hover:bg-surface-100 dark:hover:bg-surface-700'">
                <div class="flex items-center">
                    <div class="w-8 h-8 flex items-center justify-center rounded-full mr-3"
                         :class="index === 0 ? 'bg-primary text-white' : 'bg-surface-200 dark:bg-surface-600'">
                        {{ index + 1 }}
                    </div>
                    <div>
                        <div class="font-medium">{{ user.name }}</div>
                        <div class="text-sm text-muted-color">{{ user.problemsSolved }} problems solved</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template> 