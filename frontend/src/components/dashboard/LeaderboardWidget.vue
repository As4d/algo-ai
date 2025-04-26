<template>
    <div class="card">
        <div class="flex items-center justify-between mb-6">
            <div class="flex items-center gap-2">
                <i class="pi pi-trophy text-primary text-xl"></i>
                <div class="font-semibold text-xl">Leaderboard</div>
            </div>
        </div>

        <div v-if="leaderboard.length === 0" class="text-center py-4 text-muted-color">
            No leaderboard data available
        </div>

        <div v-else>
            <div class="space-y-4 mb-4">
                <div v-for="(user, index) in paginatedLeaderboard" :key="user.id"
                    class="flex items-center justify-between p-3 rounded-lg"
                    :class="[
                        index === 0 && currentPage === 1 ? 'bg-yellow-100 dark:bg-yellow-900/20' :
                        index === 1 && currentPage === 1 ? 'bg-gray-100 dark:bg-gray-700/20' :
                        index === 2 && currentPage === 1 ? 'bg-amber-100 dark:bg-amber-900/20' :
                        'hover:bg-surface-100 dark:hover:bg-surface-700'
                    ]">
                    <div class="flex items-center">
                        <div class="w-8 h-8 flex items-center justify-center rounded-full mr-3"
                            :class="[
                                index === 0 && currentPage === 1 ? 'bg-yellow-500 text-white' :
                                index === 1 && currentPage === 1 ? 'bg-gray-400 text-white' :
                                index === 2 && currentPage === 1 ? 'bg-amber-600 text-white' :
                                'bg-surface-200 dark:bg-surface-600'
                            ]">
                            {{ (currentPage - 1) * rows + index + 1 }}
                        </div>
                        <div>
                            <div class="font-medium">{{ user.name }}</div>
                            <div class="text-sm text-muted-color">{{ user.problemsSolved }} problems solved</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="flex justify-between items-center">
                <div class="flex items-center gap-2">
                    <span class="text-sm text-muted-color">Rows per page:</span>
                    <Dropdown v-model="rows" :options="[5, 10, 20, 50]" class="w-16" />
                </div>
                <Paginator 
                    v-model:first="first" 
                    :rows="rows" 
                    :total-records="leaderboard.length"
                    :rows-per-page-options="[5, 10, 20, 50]"
                    template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink"
                />
            </div>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            leaderboard: [], // Set to empty array by default
            first: 0,
            rows: 10
        };
    },
    computed: {
        currentPage() {
            return Math.floor(this.first / this.rows) + 1;
        },
        paginatedLeaderboard() {
            const start = this.first;
            const end = start + this.rows;
            return this.leaderboard.slice(start, end);
        }
    },
    methods: {
        async fetchLeaderboard() {
            try {
                const response = await fetch('http://localhost:8000/gamification/leaderboard/', {
                    method: 'GET',
                    credentials: 'include'
                });
                const data = await response.json();
                console.log(data);
                this.leaderboard = data.entries.map(entry => ({
                    id: entry.id,
                    name: entry.user__username,
                    problemsSolved: entry.total_solved
                }));
            } catch (error) {
                console.error('Error fetching leaderboard:', error);
            }
        }
    },
    mounted() {
        this.fetchLeaderboard();
    }
};
</script>