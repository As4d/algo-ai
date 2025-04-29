<template>
    <div class="card p-4">
        <div class="flex justify-between items-center mb-6">
            <div>
                <div class="font-semibold text-xl">Your Plans</div>
                <p class="text-gray-600">Here you can see all your plans.</p>
            </div>
        </div>

        <div v-if="loading" class="flex justify-center p-4">
            <ProgressSpinner />
        </div>

        <div v-else-if="error" class="p-4">
            <Message severity="error" :closable="false">
                {{ error }}
            </Message>
        </div>

        <div v-else-if="plans.length === 0" class="p-4 text-center">
            <p class="text-gray-600">You don't have any plans yet.</p>
            <Button 
                label="Create Your First Plan" 
                class="mt-4" 
                @click="router.push('/create-plan')"
            />
        </div>

        <div v-else class="grid gap-4">
            <Card v-for="plan in plans" :key="plan.id" class="hover:shadow-lg transition-shadow">
                <template #header>
                    <div class="p-4">
                        <div class="flex justify-between items-start">
                            <div>
                                <h3 class="text-lg font-semibold">{{ plan.name }}</h3>
                                <p class="text-sm text-gray-600">{{ plan.description }}</p>
                            </div>
                            <div class="flex gap-2">
                                <Button 
                                    icon="pi pi-eye" 
                                    class="p-button-rounded p-button-text"
                                    @click="router.push(`/plan/${plan.id}`)"
                                />
                                <Button 
                                    icon="pi pi-trash" 
                                    class="p-button-rounded p-button-text p-button-danger"
                                    @click="confirmDelete(plan)"
                                />
                            </div>
                        </div>
                    </div>
                </template>
                <template #content>
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <p class="text-sm text-gray-600">Duration</p>
                            <p>{{ plan.duration_days }} days</p>
                        </div>
                        <div>
                            <p class="text-sm text-gray-600">Difficulty</p>
                            <p class="capitalize">{{ plan.difficulty }}</p>
                        </div>
                        <div>
                            <p class="text-sm text-gray-600">Topics</p>
                            <div class="flex flex-wrap gap-2 mt-1">
                                <Chip 
                                    v-for="topic in plan.topics" 
                                    :key="topic"
                                    :label="formatTopic(topic)"
                                    class="capitalize"
                                />
                            </div>
                        </div>
                        <div>
                            <p class="text-sm text-gray-600">Progress</p>
                            <div class="mt-1">
                                <ProgressBar 
                                    :value="plan.progress.percentage" 
                                    :showValue="true"
                                />
                                <p class="text-sm text-gray-600 mt-1">
                                    {{ plan.progress.completed }} of {{ plan.progress.total }} problems completed
                                </p>
                            </div>
                        </div>
                    </div>
                </template>
                <template #footer>
                    <div class="flex justify-between items-center text-sm text-gray-600">
                        <span>Created {{ formatDate(plan.created_at) }}</span>
                        <Tag 
                            v-if="plan.is_completed" 
                            value="Completed" 
                            severity="success"
                        />
                        <Tag 
                            v-else
                            :value="plan.is_active ? 'Active' : 'Inactive'"
                            :severity="plan.is_active ? 'success' : 'warning'"
                        />
                    </div>
                </template>
            </Card>
        </div>

        <Dialog 
            v-model:visible="deleteDialogVisible" 
            header="Confirm Delete" 
            :modal="true"
            :style="{ width: '450px' }"
        >
            <div class="confirmation-content">
                <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
                <span>Are you sure you want to delete this plan?</span>
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
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import Card from 'primevue/card';
import Button from 'primevue/button';
import ProgressBar from 'primevue/progressbar';
import ProgressSpinner from 'primevue/progressspinner';
import Message from 'primevue/message';
import Chip from 'primevue/chip';
import Tag from 'primevue/tag';
import Dialog from 'primevue/dialog';

const router = useRouter();
const toast = useToast();
const loading = ref(true);
const error = ref(null);
const plans = ref([]);
const deleteDialogVisible = ref(false);
const planToDelete = ref(null);

const fetchPlans = async () => {
    loading.value = true;
    error.value = null;
    try {
        const response = await fetch('http://localhost:8000/plan/list/', {
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Failed to fetch plans');
        }

        plans.value = await response.json();
    } catch (err) {
        error.value = err.message;
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to load plans',
            life: 3000
        });
    } finally {
        loading.value = false;
    }
};

const confirmDelete = (plan) => {
    planToDelete.value = plan;
    deleteDialogVisible.value = true;
};

const deletePlan = async () => {
    if (!planToDelete.value) return;

    try {
        const response = await fetch(`http://localhost:8000/plan/${planToDelete.value.id}/delete/`, {
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

        // Refresh the plans list
        await fetchPlans();
    } catch (err) {
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to delete plan',
            life: 3000
        });
    } finally {
        deleteDialogVisible.value = false;
        planToDelete.value = null;
    }
};

const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
};

const formatTopic = (topic) => {
    return topic.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
};

onMounted(() => {
    fetchPlans();
});
</script>

<style scoped>
.confirmation-content {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
}
</style>
