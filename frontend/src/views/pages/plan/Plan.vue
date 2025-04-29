<template>
    <div class="card p-4" style="background-color: var(--surface-card);">
        <div v-if="loading" class="flex justify-center p-4">
            <ProgressSpinner />
        </div>

        <div v-else-if="error" class="p-4">
            <Message severity="error" :closable="false">
                {{ error }}
            </Message>
        </div>

        <div v-else>
            <!-- Plan Header -->
            <div class="mb-6">
                <div class="flex justify-between items-start">
                    <div>
                        <h1 class="text-2xl font-semibold" style="color: var(--text-color)">{{ plan.name }}</h1>
                        <p style="color: var(--text-secondary-color)" class="mt-2">{{ plan.description }}</p>
                    </div>
                    <div class="flex gap-2">
                        <Button 
                            icon="pi pi-arrow-left" 
                            class="p-button-text text-green-500"
                            @click="router.push('/plans')"
                        />
                        <Button 
                            icon="pi pi-trash" 
                            class="p-button-text text-red-500"
                            @click="confirmDelete"
                        />
                    </div>
                </div>
                <div class="grid grid-cols-4 gap-4 mt-4">
                    <div class="p-4" style="background-color: var(--surface-overlay); border-radius: 8px;">
                        <p style="color: var(--text-secondary-color)" class="text-sm">Duration</p>
                        <p class="font-medium mt-1" style="color: var(--text-color)">{{ plan.duration_days }} days</p>
                    </div>
                    <div class="p-4" style="background-color: var(--surface-overlay); border-radius: 8px;">
                        <p style="color: var(--text-secondary-color)" class="text-sm">Difficulty</p>
                        <p class="font-medium mt-1 capitalize" style="color: var(--text-color)">{{ plan.difficulty }}</p>
                    </div>
                    <div class="p-4" style="background-color: var(--surface-overlay); border-radius: 8px;">
                        <p style="color: var(--text-secondary-color)" class="text-sm">Progress</p>
                        <div class="flex items-center gap-2 mt-1">
                            <ProgressBar 
                                :value="plan.progress.percentage" 
                                :showValue="false"
                                style="width: 100px; height: 6px;"
                                class="custom-progress-bar"
                            />
                            <span class="text-sm" style="color: var(--text-color)">
                                {{ plan.progress.completed }}/{{ plan.progress.total }}
                            </span>
                        </div>
                    </div>
                    <div class="p-4" style="background-color: var(--surface-overlay); border-radius: 8px;">
                        <p style="color: var(--text-secondary-color)" class="text-sm">Status</p>
                        <Tag 
                            v-if="plan.is_completed"
                            value="Completed"
                            severity="success"
                            class="mt-1"
                        />
                        <Tag 
                            v-else
                            :value="plan.is_active ? 'Active' : 'Inactive'"
                            :severity="plan.is_active ? 'success' : 'warning'"
                            class="mt-1"
                        />
                    </div>
                </div>
            </div>

            <!-- AI Explanation -->
            <div v-if="plan.ai_explanation" class="mb-6 p-4 rounded-lg" style="background-color: var(--surface-overlay);">
                <h2 class="text-lg font-semibold mb-2" style="color: var(--text-color)">AI Tutor's Explanation</h2>
                <p style="color: var(--text-secondary-color); white-space: pre-line;">{{ formatExplanation(plan.ai_explanation) }}</p>
            </div>

            <!-- Topics -->
            <div class="mb-6">
                <h2 class="text-lg font-semibold mb-2" style="color: var(--text-color)">Topics</h2>
                <div class="flex flex-wrap gap-2">
                    <Chip 
                        v-for="topic in plan.topics" 
                        :key="topic"
                        :label="formatTopic(topic)"
                        class="capitalize custom-chip"
                    />
                </div>
            </div>

            <!-- Problems List -->
            <div>
                <h2 class="text-lg font-semibold mb-4" style="color: var(--text-color)">Problems</h2>
                <div class="space-y-4">
                    <div 
                        v-for="problem in plan.problems" 
                        :key="problem.id"
                        class="p-4 rounded-lg"
                        style="background-color: var(--surface-overlay);"
                    >
                        <div class="flex justify-between items-start">
                            <div>
                                <h3 class="text-lg font-medium" style="color: var(--text-color)">{{ problem.name }}</h3>
                                <p class="text-sm mt-1" style="color: var(--text-secondary-color)">
                                    {{ problem.language }} • {{ problem.difficulty }}
                                </p>
                            </div>
                            <div class="flex items-center gap-6">
                                <div class="text-center">
                                    <p class="text-sm" style="color: var(--text-secondary-color)">Order</p>
                                    <p class="font-medium mt-1" style="color: var(--text-color)">{{ problem.order }}</p>
                                </div>
                                <div class="text-center">
                                    <p class="text-sm" style="color: var(--text-secondary-color)">Status</p>
                                    <Tag 
                                        :value="problem.is_completed ? 'Completed' : 'Pending'"
                                        :severity="problem.is_completed ? 'success' : 'warning'"
                                        class="mt-1 cursor-pointer"
                                        @click="toggleProblemStatus(problem)"
                                    />
                                </div>
                                <Button 
                                    icon="pi pi-external-link" 
                                    class="p-button-text text-green-500"
                                    style="padding: 0;"
                                    @click="router.push(`/problems/${problem.id}`)"
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Delete Confirmation Dialog -->
        <Dialog 
            v-model:visible="deleteDialogVisible" 
            header="Confirm Delete" 
            :modal="true"
            :style="{ width: '450px' }"
            class="dark-dialog"
        >
            <div class="confirmation-content">
                <i class="pi pi-exclamation-triangle mr-3 text-yellow-400" style="font-size: 2rem" />
                <span style="color: var(--text-color)">Are you sure you want to delete this plan?</span>
            </div>
            <template #footer>
                <Button 
                    label="No" 
                    icon="pi pi-times" 
                    class="p-button-text" 
                    @click="deleteDialogVisible = false"
                />
                <Button 
                    label="Yes" 
                    icon="pi pi-check" 
                    class="p-button-text p-button-danger" 
                    @click="deletePlan"
                />
            </template>
        </Dialog>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import Card from 'primevue/card';
import Button from 'primevue/button';
import ProgressBar from 'primevue/progressbar';
import ProgressSpinner from 'primevue/progressspinner';
import Message from 'primevue/message';
import Chip from 'primevue/chip';
import Tag from 'primevue/tag';
import Dialog from 'primevue/dialog';

const route = useRoute();
const router = useRouter();
const toast = useToast();
const loading = ref(true);
const error = ref(null);
const plan = ref(null);
const deleteDialogVisible = ref(false);

const fetchPlan = async () => {
    loading.value = true;
    error.value = null;
    try {
        console.log('Fetching plan with ID:', route.params.id);
        const response = await fetch(`http://localhost:8000/plan/${route.params.id}/`, {
            credentials: 'include'
        });

        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error('Error response:', errorData);
            throw new Error(errorData.detail || 'Failed to fetch plan');
        }

        const data = await response.json();
        console.log('Plan data:', data);
        
        // Ensure progress object exists with default values
        data.progress = data.progress || {
            percentage: 0,
            completed: 0,
            total: 0
        };
        
        plan.value = data;
    } catch (err) {
        console.error('Error fetching plan:', err);
        error.value = err.message;
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: err.message || 'Failed to load plan',
            life: 3000
        });
    } finally {
        loading.value = false;
    }
};

const confirmDelete = () => {
    deleteDialogVisible.value = true;
};

const deletePlan = async () => {
    try {
        const response = await fetch(`http://localhost:8000/plan/${route.params.id}/delete/`, {
            method: 'DELETE',
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Failed to delete plan');
        }

        toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Plan deleted successfully',
            life: 3000
        });

        router.push('/plans');
    } catch (err) {
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to delete plan',
            life: 3000
        });
    } finally {
        deleteDialogVisible.value = false;
    }
};

const formatTopic = (topic) => {
    return topic.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
};

const formatExplanation = (explanation) => {
    // Remove markdown code blocks if present
    return explanation.replace(/```[^`]*```/g, '').trim();
};

const toggleProblemStatus = async (problem) => {
    try {
        const response = await fetch(
            `http://localhost:8000/plan/${route.params.id}/problems/${problem.id}/status/`, 
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    is_completed: !problem.is_completed
                })
            }
        );

        if (!response.ok) {
            throw new Error('Failed to update problem status');
        }

        // Update the local state
        problem.is_completed = !problem.is_completed;
        
        // Update progress
        const total = plan.value.problems.length;
        const completed = plan.value.problems.filter(p => p.is_completed).length;
        plan.value.progress = {
            total,
            completed,
            percentage: (completed / total) * 100
        };

        toast.add({
            severity: 'success',
            summary: 'Success',
            detail: `Problem marked as ${problem.is_completed ? 'completed' : 'pending'}`,
            life: 3000
        });
    } catch (err) {
        console.error('Error updating problem status:', err);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to update problem status',
            life: 3000
        });
    }
};

onMounted(() => {
    fetchPlan();
});
</script>

<style scoped>
.confirmation-content {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
}

.custom-progress-bar :deep(.p-progressbar) {
    background: var(--surface-border);
    border-radius: 3px;
}

.custom-progress-bar :deep(.p-progressbar-value) {
    background: #10B981;
    border-radius: 3px;
}

.custom-chip {
    background-color: var(--surface-overlay);
    color: var(--text-color);
    border: none;
    padding: 0.5rem 1rem;
}

.dark-dialog :deep(.p-dialog-header) {
    background: var(--surface-card);
    color: var(--text-color);
}

.dark-dialog :deep(.p-dialog-content) {
    background: var(--surface-card);
    color: var(--text-color);
}

.dark-dialog :deep(.p-dialog-footer) {
    background: var(--surface-card);
    border-top: 1px solid var(--surface-border);
}

:deep(.p-tag.p-tag-success) {
    background-color: rgba(16, 185, 129, 0.2);
    color: #10B981;
}

:deep(.p-tag.p-tag-warning) {
    background-color: rgba(245, 158, 11, 0.2);
    color: #F59E0B;
}

:deep(.p-tag) {
    transition: transform 0.2s;
}

:deep(.p-tag:hover) {
    transform: scale(1.05);
}
</style>
