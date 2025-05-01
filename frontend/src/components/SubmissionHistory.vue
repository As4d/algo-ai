<template>
    <div class="p-6">
        <h1 class="text-2xl font-bold mb-4">Submission History</h1>
        
        <!-- Back button -->
        <button @click="$router.back()" class="mb-4 text-blue-500 hover:text-blue-700">
            ← Back to Problem
        </button>

        <!-- Submissions list -->
        <div class="space-y-4">
            <div v-for="submission in submissions" :key="submission.id" 
                 class="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                <div class="flex justify-between items-start mb-2">
                    <div>
                        <span class="font-semibold">Status:</span>
                        <span :class="submission.status === 'completed' ? 'text-green-600 dark:text-green-400' : 'text-yellow-600 dark:text-yellow-400'">
                            {{ submission.status }}
                        </span>
                    </div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">
                        {{ formatDate(submission.created_at) }}
                    </div>
                </div>
                
                <div class="mt-2">
                    <button @click="viewCode(submission)" 
                            class="text-blue-500 hover:text-blue-700 text-sm">
                        View Code
                    </button>
                </div>
            </div>

            <!-- No submissions message -->
            <div v-if="submissions.length === 0" class="text-center text-gray-500 dark:text-gray-400">
                No submissions found for this problem.
            </div>
        </div>

        <!-- Code viewer modal -->
        <div v-if="selectedSubmission" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg w-3/4 h-3/4 flex flex-col">
                <div class="p-4 border-b dark:border-gray-700 flex justify-between items-center">
                    <h2 class="text-lg font-semibold">Submission Code</h2>
                    <button @click="selectedSubmission = null" class="text-gray-500 hover:text-gray-700">
                        ✕
                    </button>
                </div>
                <div class="flex-1 overflow-auto p-4">
                    <pre class="bg-gray-100 dark:bg-gray-900 p-4 rounded-lg overflow-x-auto">{{ selectedSubmission.code_submitted }}</pre>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            submissions: [],
            selectedSubmission: null,
            problemId: null
        };
    },
    created() {
        this.problemId = this.$route.params.id;
        this.fetchSubmissions();
    },
    methods: {
        async fetchSubmissions() {
            try {
                const response = await fetch(`http://localhost:8000/problems/${this.problemId}/submissions/`, {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include'
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch submissions');
                }

                this.submissions = await response.json();
                // Sort submissions by date (newest first)
                this.submissions.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
            } catch (error) {
                console.error('Error fetching submissions:', error);
            }
        },
        formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleString();
        },
        viewCode(submission) {
            this.selectedSubmission = submission;
        }
    }
};
</script>

<style scoped>
/* Add any additional styles here */
</style> 