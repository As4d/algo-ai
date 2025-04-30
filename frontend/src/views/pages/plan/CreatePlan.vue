<template>
    <div class="card p-4">
        <div class="font-semibold text-xl mb-4">Generate a new plan</div>
        <p class="mb-6">Fill in the form below to generate a new plan.</p>

        <form @submit.prevent="submitForm" class="space-y-4">
            <!-- Plan Name -->
            <div class="field">
                <label for="name" class="block text-sm font-medium mb-2">Plan Name</label>
                <InputText 
                    id="name" 
                    v-model="form.name" 
                    class="w-full" 
                    placeholder="e.g., Python Basics Learning Plan"
                    required
                />
            </div>

            <!-- Description -->
            <div class="field">
                <label for="description" class="block text-sm font-medium mb-2">Description</label>
                <Textarea 
                    id="description" 
                    v-model="form.description" 
                    class="w-full" 
                    rows="3"
                    placeholder="Describe what you want to achieve with this plan"
                />
            </div>

            <!-- Duration -->
            <div class="field">
                <label for="duration" class="block text-sm font-medium mb-2">Duration (days)</label>
                <InputNumber 
                    id="duration" 
                    v-model="form.duration_days" 
                    class="w-full" 
                    :min="1" 
                    :max="365"
                    required
                />
            </div>

            <!-- Difficulty -->
            <div class="field">
                <label for="difficulty" class="block text-sm font-medium mb-2">Difficulty Level</label>
                <Dropdown 
                    id="difficulty" 
                    v-model="form.difficulty" 
                    :options="difficultyOptions" 
                    optionLabel="label"
                    optionValue="value"
                    class="w-full"
                    placeholder="Select difficulty level"
                    required
                />
            </div>

            <!-- Topics -->
            <div class="field">
                <label class="block text-sm font-medium mb-2">Topics</label>
                <MultiSelect 
                    v-model="form.topics" 
                    :options="topicOptions" 
                    optionLabel="label"
                    optionValue="value"
                    class="w-full"
                    placeholder="Select topics"
                    :filter="true"
                    required
                />
            </div>

            <!-- Submit Button -->
            <div class="flex justify-end">
                <Button 
                    type="submit" 
                    label="Generate Plan" 
                    :loading="loading"
                    :disabled="loading"
                />
            </div>
        </form>
    </div>
</template>

<script setup>
import { ref, reactive, onBeforeMount } from 'vue';
import { useRouter } from 'vue-router';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import InputNumber from 'primevue/inputnumber';
import Dropdown from 'primevue/dropdown';
import MultiSelect from 'primevue/multiselect';
import Button from 'primevue/button';
import { useToast } from 'primevue/usetoast';

const router = useRouter();
const toast = useToast();
const loading = ref(false);
const topicOptions = ref([]);

const form = reactive({
    name: '',
    description: '',
    duration_days: 7,
    difficulty: '',
    topics: []
});

const difficultyOptions = [
    { label: 'Beginner', value: 'beginner' },
    { label: 'Intermediate', value: 'intermediate' },
    { label: 'Advanced', value: 'advanced' }
];

const fetchProblemTypes = async () => {
    try {
        const response = await fetch('http://localhost:8000/problems/types/', {
            method: 'GET',
            headers: { 'Accept': 'application/json' },
            credentials: 'include'
        });

        if (!response.ok) throw new Error(`Error: ${response.status}`);

        const types = await response.json();
        topicOptions.value = types.map(type => ({
            label: type.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
            value: type
        }));
    } catch (err) {
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to fetch problem types: ' + err.message,
            life: 3000
        });
    }
};

onBeforeMount(() => {
    fetchProblemTypes();
});

const submitForm = async () => {
    if (!form.name || !form.duration_days || !form.difficulty || form.topics.length === 0) {
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Please fill in all required fields',
            life: 3000
        });
        return;
    }

    loading.value = true;
    try {
        const response = await fetch('http://localhost:8000/plan/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(form)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to create plan');
        }

        const data = await response.json();
        toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Plan created successfully',
            life: 3000
        });
        
        // Redirect to plan details page
        router.push(`/plan/${data.plan_id}`);
    } catch (error) {
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: error.message,
            life: 3000
        });
    } finally {
        loading.value = false;
    }
};
</script>

<style scoped>
.field {
    @apply mb-4;
}

:deep(.p-inputtext) {
    @apply w-full;
}

:deep(.p-dropdown) {
    @apply w-full;
}

:deep(.p-multiselect) {
    @apply w-full;
}
</style>
