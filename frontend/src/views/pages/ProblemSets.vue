<script setup>
import { ref, onBeforeMount, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { FilterMatchMode } from '@primevue/core/api';

const problems = ref([]);
const loading = ref(true);
const error = ref('');
const router = useRouter();

const filters = ref({
    global: { value: null, matchMode: FilterMatchMode.CONTAINS },
    name: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    language: { value: null, matchMode: FilterMatchMode.EQUALS },
    difficulty: { value: null, matchMode: FilterMatchMode.EQUALS },
    status: { value: null, matchMode: FilterMatchMode.EQUALS }
});

const difficulties = reactive(['easy', 'medium', 'hard']);

const fetchProblems = async () => {
    try {
        const response = await fetch('http://localhost:8000/problems/list/?type=problem_set', {
            method: 'GET',
            headers: { 'Accept': 'application/json' },
            credentials: 'include'
        });

        if (!response.ok) throw new Error(`Error: ${response.status}`);

        problems.value = await response.json();
    } catch (err) {
        error.value = 'Failed to fetch problems: ' + err;
    } finally {
        loading.value = false;
    }
};

const viewProblem = (problemId) => {
    router.push({ path: `/problems/${problemId}` });
};


const getStatusClass = (status) => {
    switch (status) {
        case 'completed':
            return 'bg-green-500 text-white';
        case 'started':
            return 'bg-yellow-500 text-black';
        case 'not_started':
        default:
            return 'bg-gray-300 text-black';
    }
};

onBeforeMount(fetchProblems);
</script>

<template>
    <div class="p-6">
        <h2 class="text-2xl font-semibold text-center mb-4 text-surface-900 dark:text-surface-0">Problem Sets</h2>

        <div v-if="loading" class="text-center text-gray-500">Loading problems...</div>
        <div v-if="error" class="text-red-500 text-center">{{ error }}</div>

        <DataTable
            v-if="!loading && problems.length"
            :value="problems"
            :paginator="true"
            :rows="10"
            dataKey="id"
            :rowHover="true"
            v-model:filters="filters"
            filterDisplay="menu"
            showGridlines
            class="shadow-md rounded-lg"
            @row-click="(e) => viewProblem(e.data.id)"
            :rowClass="() => 'cursor-pointer'"
        >
            <template #header>
                <div class="flex justify-between items-center">
                    <Button type="button" icon="pi pi-filter-slash" label="Clear" outlined @click="filters = {}" />
                    <InputText v-model="filters.global.value" placeholder="Search Problems..." class="p-inputtext-sm w-60" />
                </div>
            </template>

            <Column field="name" header="Problem Name" style="min-width: 14rem" :sortable="true">
                <template #body="{ data }">
                    <span class="text-primary font-semibold">
                        {{ data.name }}
                    </span>
                </template>
                <template #filter="{ filterModel }">
                    <InputText v-model="filterModel.value" placeholder="Search by name" />
                </template>
            </Column>

            <Column field="language" header="Language" style="min-width: 10rem" :sortable="true">
                <template #filter="{ filterModel }">
                    <Dropdown v-model="filterModel.value" :options="['Python', 'C++', 'Java', 'JavaScript']" placeholder="Filter by Language" showClear />
                </template>
            </Column>

            <Column field="difficulty" header="Difficulty" style="min-width: 10rem" :sortable="true">
                <template #body="{ data }">
                    <span
                        :class="{
                            'text-green-600': data.difficulty === 'easy',
                            'text-yellow-600': data.difficulty === 'medium',
                            'text-red-600': data.difficulty === 'hard'
                        }"
                    >
                        {{ data.difficulty }}
                    </span>
                </template>
                <template #filter="{ filterModel }">
                    <Dropdown v-model="filterModel.value" :options="difficulties" placeholder="Filter by Difficulty" showClear />
                </template>
            </Column>

            <Column field="status" header="Status" style="min-width: 10rem" :sortable="true">
                <template #body="{ data }">
                    <span class="px-2 py-1 rounded" :class="getStatusClass(data.status)">
                        {{ data.status === 'not_started' ? 'Not Started' : 
                           data.status === 'started' ? 'In Progress' :
                           'Completed' }}
                    </span>
                </template>
                <template #filter="{ filterModel }">
                    <Dropdown 
                        v-model="filterModel.value" 
                        :options="[
                            { label: 'Not Started', value: 'not_started' },
                            { label: 'In Progress', value: 'started' },
                            { label: 'Completed', value: 'completed' }
                        ]" 
                        optionLabel="label"
                        optionValue="value"
                        placeholder="Filter by Status" 
                        showClear 
                    />
                </template>
            </Column>

            <template #empty> No problems found. </template>
            <template #loading> Loading problems data. Please wait... </template>
        </DataTable>

        <div v-if="!loading && !problems.length" class="text-center text-gray-500">No problems available.</div>
    </div>
</template>

<style scoped>
/* Add hover effect for the entire row */
:deep(.p-datatable .p-datatable-tbody > tr) {
    transition: background-color 0.2s;
}

:deep(.p-datatable .p-datatable-tbody > tr:hover) {
    background-color: var(--surface-hover) !important;
}
</style>
