<script setup>
import ProblemList from '@/components/ProblemList.vue';
</script>

<template>
    <ProblemList
        title="Problem Sets"
        problemType="problem_set"
        itemLabel="Problem"
        :sortByOrder="false"
    />
</template>
