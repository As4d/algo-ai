<template>
    <div class="col-span-12 lg:col-span-6 xl:col-span-6">
        <div class="card mb-0">
            <div class="flex justify-between mb-4">
                <div>
                    <span class="block text-muted-color font-medium mb-4">Streak</span>
                    <div class="text-surface-900 dark:text-surface-0 font-medium text-xl">{{ currentStreak }} days</div>
                </div>
                <div class="flex items-center justify-center bg-green-100 dark:bg-green-400/10 rounded-border"
                    style="width: 2.5rem; height: 2.5rem">
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
                    <div class="text-surface-900 dark:text-surface-0 font-medium text-xl">{{ totalProblemsSolved }}
                    </div>
                </div>
                <div class="flex items-center justify-center bg-blue-100 dark:bg-blue-400/10 rounded-border"
                    style="width: 2.5rem; height: 2.5rem">
                    <i class="pi pi-check-circle text-blue-500 !text-xl"></i>
                </div>
            </div>
            <span class="text-muted-color">last updated: </span>
            <span class="text-primary font-medium">{{ formatDate(lastUpdated) }}</span>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            currentStreak: 0,
            highScore: 0,
            daysToHighScore: 0,
            totalProblemsSolved: 0,
            lastUpdated: 0
        }
    },

    methods: {
        async fetchUserStats() {
            try {
                // Fetch profile data
                const profileResponse = await fetch('http://localhost:8000/api/profile', {
                    method: 'GET',
                    credentials: 'include'
                });
                const profileData = await profileResponse.json();

                // Update streak stats
                this.currentStreak = profileData.streak;
                this.highScore = profileData.high_score_streak;
                this.daysToHighScore = Math.max(0, profileData.high_score_streak - profileData.streak);

                // Fetch gamification stats
                const statsResponse = await fetch('http://localhost:8000/gamification/stats/', {
                    method: 'GET',
                    credentials: 'include'
                });
                const statsData = await statsResponse.json();
                this.totalProblemsSolved = statsData.total_solved;
                this.lastUpdated = statsData.last_updated;
            } catch (error) {
                console.error('Error fetching user stats:', error);
            }
        },
        formatDate(date) {
            if (!date) return 'Not available';
            return new Date(date).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        }
    },

    mounted() {
        this.fetchUserStats();
    }
}
</script>
